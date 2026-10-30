"""Adversarial SMF checks, independent of the catalog exporter."""
from pathlib import Path
import importlib.util
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('aria_midi', ROOT / 'scripts/lib/midi.py')
midi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(midi)

def smf(track):
    return b'MThd' + struct.pack('>IHHH', 6, 0, 1, 480) + b'MTrk' + struct.pack('>I', len(track)) + track

class MidiNegative(unittest.TestCase):
    def test_bad_events(self):
        for change in ({'pitch': 128}, {'pitch': -1}, {'duration': 0}, {'duration': -1}, {'tick': -1}, {'channel': 16}, {'velocity': 0}):
            e = dict(tick=0, duration=10, pitch=60, channel=0, velocity=80)
            e.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError): midi.encode([e])

    def test_bad_streams(self):
        good = midi.encode([dict(tick=0, duration=120, pitch=60)])
        cases = [good[:-1], good + b'garbage', b'',
                 smf(b'\x00\x90\x3c\x40\x00\xff\x2f\x00'), # held note
                 smf(b'\x00\x80\x3c\x00\x00\xff\x2f\x00'), # unmatched release
                 smf(b'\x00\x90\x3c\x40\x01\x90\x3c\x40\x01\x80\x3c\x00\x00\xff\x2f\x00'),
                 smf(b'\x81\x81\x81\x81\x00\xff\x2f\x00'), # 5-byte VLQ
                 smf(b'\x00\xff\x2f\x00\x00'), # bytes after EOT
                 smf(b'\x00\x90\x80\x40\x00\xff\x2f\x00')]
        for data in cases:
            with self.subTest(data=data), self.assertRaises(ValueError): midi.decode(data)

    def test_note_off_before_next_attack_and_silent_end(self):
        events = [dict(tick=0, duration=10, pitch=60), dict(tick=10, duration=5, pitch=60)]
        result = midi.decode(midi.encode(events, end_tick=30))
        self.assertEqual([(e['tick'], e['duration'], e['pitch']) for e in result['events']], [(0,10,60),(10,5,60)])
        self.assertEqual(result['endTick'], 30)

if __name__ == '__main__': unittest.main()
