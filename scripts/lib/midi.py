"""Offline Standard MIDI File conversion. No music or fingering generation.

The stable catalogue uses separate channels for its primary and secondary lane.
Absolute ticks preserve silent spacing; note-off ticks preserve key contact.
"""
import math
import struct

PPQ = 9600


def vlq(value):
    if not isinstance(value, int) or not 0 <= value <= 0x0fffffff:
        raise ValueError('MIDI delta outside four-byte VLQ range')
    result = [value & 127]
    while value >> 7:
        value >>= 7
        result.insert(0, (value & 127) | 128)
    return bytes(result)


def encode(events, bpm=60, ppq=PPQ, end_tick=None):
    """Encode events {tick,duration,pitch,channel,velocity} as SMF format 0."""
    if not isinstance(ppq, int) or not 0 < ppq < 0x8000:
        raise ValueError('Invalid ticks per quarter')
    if isinstance(bpm, bool) or not isinstance(bpm, (int, float)) or not math.isfinite(bpm) or not 1 <= bpm <= 1000:
        raise ValueError('Invalid MIDI tempo')
    tempo = round(60000000 / bpm)
    if not 1 <= tempo <= 0xffffff:
        raise ValueError('Tempo cannot be represented by a MIDI tempo event')
    messages = [(0, -1, b'\xff\x51\x03' + tempo.to_bytes(3, 'big'))]
    occupied = {}
    for i, event in enumerate(events):
        tick, duration, pitch = event['tick'], event['duration'], event['pitch']
        channel, velocity = event.get('channel', 0), event.get('velocity', 80)
        if any(type(v) is not int for v in [tick, duration, pitch, channel, velocity]):
            raise ValueError('MIDI event values must be integers')
        if tick < 0 or duration <= 0 or not 0 <= pitch <= 127 or not 0 <= channel <= 15 or not 1 <= velocity <= 127:
            raise ValueError('Invalid MIDI event')
        intervals = occupied.setdefault((channel, pitch), [])
        if any(tick < finish and tick + duration > start for start, finish in intervals):
            raise ValueError('Ambiguous overlapping MIDI note of same pitch/channel')
        intervals.append((tick, tick + duration))
        messages.extend([(tick, i * 2 + 1, bytes([0x90 | channel, pitch, velocity])),
                         (tick + duration, i * 2, bytes([0x80 | channel, pitch, 0]))])
    end = max((e['tick'] + e['duration'] for e in events), default=0)
    if end_tick is not None:
        if type(end_tick) is not int or end_tick < end:
            raise ValueError('MIDI end precedes final release')
        end = end_tick
    # At equal ticks, release old notes before starting the next repeated note.
    messages.sort(key=lambda e: (e[0], 0 if e[2][0] & 0xf0 == 0x80 else 1, e[1]))
    result, previous = bytearray(), 0
    for tick, _, message in messages:
        result.extend(vlq(tick - previous) + message)
        previous = tick
    result.extend(vlq(end - previous) + b'\xff\x2f\x00')
    return b'MThd' + struct.pack('>IHHH', 6, 0, 1, ppq) + b'MTrk' + struct.pack('>I', len(result)) + result


def decode(data):
    """Read SMF formats 0/1, including running status and tempo events.

    Reject incomplete, SMPTE, unmatched, and ambiguous overlapping same-pitch
    data instead of flattening it. Returns absolute ticks, never float seconds.
    """
    pos = 0

    def take(count):
        nonlocal pos
        if pos + count > len(data):
            raise ValueError('Truncated MIDI')
        value = data[pos:pos + count]
        pos += count
        return value

    def variable():
        value = 0
        for _ in range(4):
            byte = take(1)[0]
            value = (value << 7) | (byte & 127)
            if byte < 128:
                return value
        raise ValueError('Invalid MIDI VLQ')

    if take(4) != b'MThd' or int.from_bytes(take(4), 'big') != 6:
        raise ValueError('Invalid MIDI header')
    fmt, tracks, ppq = struct.unpack('>HHH', take(6))
    if fmt not in (0, 1) or tracks < 1 or (fmt == 0 and tracks != 1) or not 0 < ppq < 0x8000:
        raise ValueError('Unsupported MIDI format or SMPTE timing')
    events, tempos, ends = [], [], []
    for track in range(tracks):
        if take(4) != b'MTrk':
            raise ValueError('Missing MIDI track')
        limit = int.from_bytes(take(4), 'big') + pos
        if limit > len(data):
            raise ValueError('Truncated MIDI track')
        tick, status, active, ended = 0, None, {}, False
        while pos < limit:
            tick += variable()
            first = take(1)[0]
            if first < 128:
                if status is None:
                    raise ValueError('Invalid MIDI running status')
                pos -= 1
                first = status
            if first == 0xff:
                status = None
                kind = take(1)[0]
                payload = take(variable())
                if kind == 0x51:
                    if len(payload) != 3 or int.from_bytes(payload, 'big') == 0:
                        raise ValueError('Invalid MIDI tempo')
                    tempos.append({'tick': tick, 'microsecondsPerQuarter': int.from_bytes(payload, 'big')})
                elif kind == 0x2f:
                    if payload or pos != limit:
                        raise ValueError('Invalid MIDI end-of-track')
                    ended = True
                    ends.append(tick)
                continue
            if first in (0xf0, 0xf7):
                status = None
                take(variable())
                continue
            if not 0x80 <= first <= 0xef:
                raise ValueError('Unsupported MIDI status')
            status = first
            kind, channel = first & 0xf0, first & 15
            payload = take(1 if kind in (0xc0, 0xd0) else 2)
            if any(v > 127 for v in payload):
                raise ValueError('Invalid MIDI data byte')
            if kind not in (0x80, 0x90):
                continue
            pitch, velocity = payload
            key = channel, pitch
            if kind == 0x90 and velocity:
                if key in active:
                    raise ValueError('Ambiguous overlapping MIDI note of same pitch/channel')
                active[key] = (tick, velocity)
            else:
                if key not in active:
                    raise ValueError('MIDI release without attack')
                start, attack_velocity = active.pop(key)
                if tick <= start:
                    raise ValueError('Non-positive MIDI duration')
                events.append(dict(tick=start, duration=tick-start, pitch=pitch,
                                   channel=channel, velocity=attack_velocity, track=track))
        if pos != limit or not ended or active:
            raise ValueError('Unclosed MIDI track or held notes')
    if pos != len(data):
        raise ValueError('Trailing MIDI bytes')
    return dict(format=fmt, ticksPerQuarter=ppq, events=sorted(events, key=lambda e: (e['tick'], e['channel'], e['pitch'])),
                tempos=sorted(tempos, key=lambda e: e['tick']), endTick=max(ends))
