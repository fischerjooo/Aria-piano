"""Automatic ergonomic piano fingering for monophonic hand lanes.

The optimizer is deterministic and future-looking: it uses dynamic programming over
candidate finger sequences, scoring ergonomic spans, hand-position movement,
crossings, black-key use, repeated notes, and common five-finger/scale positions.

Finger numbers follow piano convention: 1=thumb ... 5=little finger.
"""
from math import isfinite

# Parncutt et al. (1997), Appendix / Table 1, right-hand span matrices.
# Rows are the first finger, columns the second finger; values are semitones.
MAX_PRAC = (
    (0, 10, 12, 14, 15),
    (5, 0, 5, 7, 10),
    (4, -1, 0, 4, 7),
    (3, -1, -1, 0, 5),
    (1, -2, -1, -1, 0),
)
MAX_COMF = (
    (0, 8, 10, 12, 13),
    (3, 0, 3, 5, 8),
    (2, -1, 0, 2, 5),
    (1, -1, -1, 0, 3),
    (-1, -2, -1, -1, 0),
)
MAX_REL = (
    (0, 5, 7, 9, 10),
    (-1, 0, 2, 4, 6),
    (-3, -1, 0, 2, 4),
    (-5, -3, -1, 0, 2),
    (-7, -5, -3, -1, 0),
)

BLACK = {1, 3, 6, 8, 10}
# Approximate horizontal key-centre positions in white-key units.
KEY_X = (0.0, .55, 1.0, 1.55, 2.0, 3.0, 3.55, 4.0, 4.55, 5.0, 5.55, 6.0)


def _norm_finger(finger, hand):
    """Finger coordinate from low to high key: 1..5 for either hand."""
    return finger if hand == 'RH' else 6 - finger


def _right_equivalent(finger, hand):
    return finger if hand == 'RH' else 6 - finger


def _limits(first, second, hand, matrix):
    a, b = _right_equivalent(first, hand), _right_equivalent(second, hand)
    maximum = matrix[a - 1][b - 1]
    minimum = -matrix[b - 1][a - 1]
    return minimum, maximum


def _key_x(note):
    octave, pc = divmod(note, 12)
    return octave * 7 + KEY_X[pc]


def _position(note, finger, hand):
    return _key_x(note) - (_norm_finger(finger, hand) - 1)


def _is_black(note):
    return note % 12 in BLACK


def _boundary_discount(interval, previous_step):
    if abs(interval) >= 12:
        return .22
    if previous_step is not None and previous_step >= 2:
        return .35
    if abs(interval) >= 8:
        return .55
    return 1.0


def _single_cost(note, finger, hand, index, notes):
    norm = _norm_finger(finger, hand)
    cost = 0.0
    if _is_black(note):
        if finger == 1:
            cost += 3.2
        elif finger == 5:
            cost += .45
    if finger == 4:
        cost += .12

    # Common beginner anchor: thumb on C in RH, little finger on C in LH
    # when C is the low edge of the nearby phrase, not when it lies mid-shape.
    if note % 12 == 0:
        lo = min(notes[index:index + 5])
        hi = max(notes[index:index + 5])
        if note == lo and hi - lo <= 9:
            cost += 0 if norm == 1 else .85 * (norm - 1)
    return cost


def _start_cost(notes, finger, hand):
    norm = _norm_finger(finger, hand)
    if len(notes) == 1:
        return .12 * abs(norm - 3)
    look = notes[1:min(len(notes), 5)]
    direction = sum(1 if n > notes[0] else -1 if n < notes[0] else 0 for n in look)
    cost = 0.0
    if direction > 0:
        cost += .32 * (norm - 1)
    elif direction < 0:
        cost += .32 * (5 - norm)
    else:
        cost += .08 * abs(norm - 3)
    if notes[0] % 12 == 0:
        target = 1 if direction >= 0 else 5
        cost += .7 * abs(norm - target)
    return cost


def _end_cost(notes, finger, hand):
    if len(notes) < 2:
        return 0.0
    norm = _norm_finger(finger, hand)
    direction = notes[-1] - notes[-2]
    if direction > 0:
        return .16 * (5 - norm)
    if direction < 0:
        return .16 * (norm - 1)
    return 0.0


def _transition_cost(prev_note, note, prev_finger, finger, hand, previous_step):
    interval = note - prev_note
    discount = _boundary_discount(interval, previous_step)
    if interval == 0:
        return 0.0 if finger == prev_finger else .65

    movement = abs(_position(note, finger, hand) - _position(prev_note, prev_finger, hand))
    cost = max(0.0, movement - .65) * 1.15 * discount

    if finger == prev_finger:
        # Sliding the same finger to a neighboring key is possible, but normally
        # less fluent than using a new finger. Large leaps imply repositioning.
        return cost + (5.5 if abs(interval) <= 2 else 2.8 + .18 * abs(interval)) * discount

    min_rel, max_rel = _limits(prev_finger, finger, hand, MAX_REL)
    min_comf, max_comf = _limits(prev_finger, finger, hand, MAX_COMF)
    min_prac, max_prac = _limits(prev_finger, finger, hand, MAX_PRAC)

    if interval > max_rel:
        if interval <= max_comf:
            cost += .45 * (interval - max_rel)
        elif interval <= max_prac:
            cost += .45 * (max_comf - max_rel) + 1.25 * (interval - max_comf)
        else:
            cost += (3.4 + .28 * (interval - max_prac)) * discount
    elif interval < min_rel:
        if interval >= min_comf:
            cost += (.55 if 1 in (prev_finger, finger) else .9) * (min_rel - interval)
        elif interval >= min_prac:
            cost += 1.35 * (min_comf - interval) + .7
        else:
            cost += (3.4 + .28 * (min_prac - interval)) * discount

    a, b = _norm_finger(prev_finger, hand), _norm_finger(finger, hand)
    directional = (interval > 0 and b > a) or (interval < 0 and b < a)
    if not directional:
        # A reversal of finger order is usually a thumb crossing or a hand shift.
        if 1 in (prev_finger, finger):
            other = finger if prev_finger == 1 else prev_finger
            crossing = {2: 1.6, 3: .65, 4: .85, 5: 2.8}.get(other, 2.8)
            cost += crossing * discount
            if (finger == 1 and _is_black(note)) or (prev_finger == 1 and _is_black(prev_note)):
                cost += 1.5
        else:
            cost += 3.7 * discount

    return cost


def _triple_cost(a, b, c, first, second, third, hand):
    fa, fb, fc = (_norm_finger(f, hand) for f in (first, second, third))
    d1, d2 = b - a, c - b
    if not d1 or not d2 or d1 * d2 <= 0:
        return 0.0
    f1, f2 = fb - fa, fc - fb
    if f1 * f2 < 0 and 1 not in (first, second, third):
        return 2.4
    if fa == fc and fa != fb and abs(c - a) >= 3:
        return 1.2
    return 0.0


def generate_fingering(notes, hand='RH', steps=None):
    """Return an ergonomic 1..5 fingering for one melodic hand lane.

    The search keeps the best cost for every final two-finger state and stores
    back-pointers rather than copying whole paths, making it linear in passage
    length for the fixed 25-state search space.
    """
    notes = list(notes)
    if hand not in ('RH', 'LH'):
        raise ValueError('hand must be RH or LH')
    if not notes or any(type(n) is not int or not 0 <= n <= 127 for n in notes):
        raise ValueError('notes must be a non-empty MIDI-note sequence')
    if steps is not None:
        steps = list(steps)
        if len(steps) != len(notes) or any(type(x) not in (int, float) or not isfinite(x) or x <= 0 for x in steps):
            raise ValueError('steps must match notes and contain positive finite values')

    first_layer = {}
    for finger in range(1, 6):
        key = (0, finger)
        cost = _start_cost(notes, finger, hand) + _single_cost(notes[0], finger, hand, 0, notes)
        first_layer[key] = (cost, None)
    layers = [first_layer]
    states = first_layer

    for index in range(1, len(notes)):
        next_states = {}
        previous_step = steps[index - 1] if steps is not None else None
        for prior_key in sorted(states):
            base, _ = states[prior_key]
            prev_prev_finger, prev_finger = prior_key
            for finger in range(1, 6):
                cost = base
                cost += _single_cost(notes[index], finger, hand, index, notes)
                cost += _transition_cost(notes[index - 1], notes[index], prev_finger, finger, hand, previous_step)
                if index >= 2:
                    cost += _triple_cost(
                        notes[index - 2], notes[index - 1], notes[index],
                        prev_prev_finger, prev_finger, finger, hand,
                    )
                key = (prev_finger, finger)
                current = next_states.get(key)
                if current is None or cost < current[0] - 1e-12:
                    next_states[key] = (cost, prior_key)
        layers.append(next_states)
        states = next_states

    final_key = min(
        states,
        key=lambda key: (states[key][0] + _end_cost(notes, key[1], hand), key),
    )
    path = [final_key[1]]
    key = final_key
    for index in range(len(notes) - 1, 0, -1):
        key = layers[index][key][1]
        path.append(key[1])
    path.reverse()
    return path


def hand_for_record(metadata, secondary=False):
    if secondary:
        return 'LH'
    hand = str(metadata.get('hand', '')).lower()
    return 'LH' if hand.startswith('left') else 'RH'
