"""Meaningful data/build round trips and archive fidelity, with no network."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from lib.catalogue import DATA, compile_stable, read_json, read_yaml
from lib.midi import decode, encode
from catalogue import import_midi

stable = compile_stable()
reference = json.loads(subprocess.check_output(['node', str(ROOT / 'scripts/export_runtime.cjs'), str(ROOT / 'aria-piano-v5.26.html')]))
assert stable == reference, 'Every materialized property must match the frozen app'
provenance = read_yaml(DATA / 'stable/descriptions.yaml')['provenance']
assert hashlib.sha256((ROOT / provenance['archive']).read_bytes()).hexdigest() == provenance['sha256']
for path in sorted((DATA / 'stable/midi').glob('*.mid')):
    original = decode(path.read_bytes())
    tempo = original['tempos'][0]['microsecondsPerQuarter']
    converted = decode(encode(original['events'], 60000000 / tempo, original['ticksPerQuarter'], original['endTick']))
    assert converted == original, path.name

with tempfile.TemporaryDirectory(prefix='aria-data-test-') as temporary:
    directory = Path(temporary) / 'stable'
    shutil.copytree(DATA / 'stable', directory)
    record_id = 'lesson-1'
    path = directory / 'midi' / (record_id + '.mid')
    original = path.read_bytes()
    assert import_midi(directory, record_id, original, apply=True) is False
    assert path.read_bytes() == original
    midi = decode(original)
    for event in midi['events']:
        event['pitch'] += 1
    changed = encode(midi['events'], 60000000 / midi['tempos'][0]['microsecondsPerQuarter'], end_tick=midi['endTick'])
    before = compile_stable(directory)
    assert import_midi(directory, record_id, changed) is True
    assert path.read_bytes() == original, 'Dry run must not mutate data'
    assert import_midi(directory, record_id, changed, apply=True) is True
    after = compile_stable(directory)
    target = next(l for row in after['lessonLevels'] for l in row if l['id'] == record_id)
    old = next(l for row in before['lessonLevels'] for l in row if l['id'] == record_id)
    assert target['seq'] == [n + 1 for n in old['seq']]
    assert target['f'] == old['f'], 'MIDI import cannot invent fingering'
    assert target['beats'] == old['beats'], 'MIDI contact must not guess written notation'
print('PASS exact catalogue/archive parity, all 346 MIDI round trips and editable MIDI import/dry run')
