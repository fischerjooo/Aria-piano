"""Regression coverage for the automatic fingering optimizer."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from lib.catalogue import build_catalogue, load_packages
from lib.fingering import generate_fingering

assert generate_fingering([60, 62, 64, 65, 67, 69, 71, 72], 'RH') == [1, 2, 3, 1, 2, 3, 4, 5]
assert generate_fingering([48, 50, 52, 53, 55, 57, 59, 60], 'LH') == [5, 4, 3, 2, 1, 3, 2, 1]
assert generate_fingering([60, 62, 64, 65, 67], 'RH') == [1, 2, 3, 4, 5]
assert generate_fingering([48, 50, 52, 53, 55], 'LH') == [5, 4, 3, 2, 1]
assert generate_fingering([60, 60, 60, 60], 'RH') == [1, 1, 1, 1]

black_run = generate_fingering([61, 63, 65, 66, 68], 'RH')
assert black_run[0] != 1 and black_run[1] != 1 and black_run[3] != 1 and black_run[4] != 1, black_run

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

print('PASS automatic ergonomic fingering, standard C-scale anchors, no hard-coded package finger arrays')
