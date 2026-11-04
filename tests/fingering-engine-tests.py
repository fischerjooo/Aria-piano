"""Regression coverage for the automatic fingering optimizer."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from lib.catalogue import build_catalogue, load_packages
from lib.fingering import generate_fingering
from fingering_corpus import CASES

assert generate_fingering([60, 62, 64, 65, 67, 69, 71, 72], 'RH') == [1, 2, 3, 1, 2, 3, 4, 5]
assert generate_fingering([48, 50, 52, 53, 55, 57, 59, 60], 'LH') == [5, 4, 3, 2, 1, 3, 2, 1]
assert generate_fingering([60, 62, 64, 65, 67], 'RH') == [1, 2, 3, 4, 5]
assert generate_fingering([48, 50, 52, 53, 55], 'LH') == [5, 4, 3, 2, 1]
assert generate_fingering([60, 60, 60, 60], 'RH') == [1, 1, 1, 1]

mismatches = []
matched_notes = total_notes = 0
for case in CASES:
    actual = generate_fingering(case['notes'], case['hand'])
    expected = case['fingers']
    same = sum(a == b for a, b in zip(actual, expected))
    matched_notes += same
    total_notes += len(expected)
    if actual != expected:
        mismatches.append((case['name'], expected, actual, case['source']))
accuracy = matched_notes / total_notes
if mismatches:
    for name, expected, actual, source in mismatches:
        print(f'FINGERING MISMATCH {name}: expected={expected} actual={actual} source={source}')
print(f'Corpus exact-note agreement: {matched_notes}/{total_notes} = {accuracy:.1%}; exact melodies: {len(CASES)-len(mismatches)}/{len(CASES)}')
assert accuracy >= .95, f'fingering corpus accuracy {accuracy:.1%} below 95%'
assert not next((m for m in mismatches if m[0] == 'Ode to Joy'), None), 'canonical Ode to Joy fingering regressed'
assert not next((m for m in mismatches if m[0] == 'Turkish March'), None), 'contextual black-key thumb turn regressed'

packages = load_packages()
for record_id, package in packages['records'].items():
    notation = package['notation']['notation']
    assert 'f' not in notation, record_id
    assert 'lf' not in notation, record_id

catalogue = build_catalogue()
records = [item for row in catalogue['lessonLevels'] for item in row] + catalogue['melodyData']
for record in records:
    assert len(record['f']) == len(record['seq']), record['id']
    assert all(type(f) is int and 1 <= f <= 5 for f in record['f']), record['id']
    if 'left' in record:
        assert len(record['lf']) == len(record['left']), record['id']
        assert all(type(f) is int and 1 <= f <= 5 for f in record['lf']), record['id']

print('PASS automatic ergonomic fingering, 20-melody benchmark, scale anchors, and no hard-coded package finger arrays')
