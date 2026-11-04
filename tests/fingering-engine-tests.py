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
    actual = generate_fingering(case['notes'], case['hand'], steps=case.get('steps'))
    expected = case['fingers']
    same = sum(a == b for a, b in zip(actual, expected))
    matched_notes += same
    total_notes += len(expected)
    if actual != expected:
        mismatches.append((case['name'], expected, actual, case['source']))
accuracy = matched_notes / total_notes
strict_names = {case['name'] for case in CASES if case.get('strict', True)}
strict_mismatches = [m for m in mismatches if m[0] in strict_names]
if mismatches:
    for name, expected, actual, source in mismatches:
        print(f'FINGERING MISMATCH {name}: expected={expected} actual={actual} source={source}')
print(f'Corpus exact-note agreement: {matched_notes}/{total_notes} = {accuracy:.1%}; exact cases: {len(CASES)-len(mismatches)}/{len(CASES)}')
print(f'Canonical strict cases: {len(strict_names)-len(strict_mismatches)}/{len(strict_names)} exact')
long_cases = [case for case in CASES if 'long form' in case['name']]
long_matches = 0
long_total = 0
long_exact = 0
for case in long_cases:
    actual = generate_fingering(case['notes'], case['hand'], steps=case.get('steps'))
    expected = case['fingers']
    same = sum(a == b for a, b in zip(actual, expected))
    long_matches += same
    long_total += len(expected)
    long_exact += int(actual == expected)
print(f'Long-form agreement: {long_matches}/{long_total} = {long_matches/long_total:.1%}; exact cases: {long_exact}/{len(long_cases)}')
# Aggregate agreement is a regression diagnostic because published fingerings
# can legitimately differ. Canonical cases remain exact hard gates; the
# aggregate and long-form floors prevent silent quality drift from this
# expanded, heterogeneous reference baseline.
assert accuracy >= .80, f'fingering corpus accuracy {accuracy:.1%} below 80% baseline'
assert long_matches / long_total >= .85, f'long-form fingering accuracy {long_matches/long_total:.1%} below 85% baseline'
assert len(CASES) - len(mismatches) >= 40, 'too many previously exact benchmark cases regressed'
assert long_exact >= 5, 'long-form exact-match count regressed below 5/10'
assert not strict_mismatches, f'canonical fingering cases regressed: {[m[0] for m in strict_mismatches]}'

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

print('PASS automatic ergonomic fingering, 50-melody / 10 long-form benchmark, scale anchors, and no hard-coded package finger arrays')
