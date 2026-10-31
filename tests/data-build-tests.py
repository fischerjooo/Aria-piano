"""Package discovery, archive fidelity, MIDI round trips and local edits."""
import hashlib
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from lib.catalogue import DATA, build_catalogue, read_yaml, load_packages
from lib.midi import decode, encode
from catalogue import import_midi

catalogue = build_catalogue()
provenance = read_yaml(DATA / 'provenance.yaml')
assert hashlib.sha256((ROOT / provenance['archive']).read_bytes()).hexdigest() == provenance['sha256']
midi_files = sorted(list((DATA / 'lessons').rglob('performance.mid')) + list((DATA / 'songs').rglob('performance.mid')))
assert len(midi_files) == 346, len(midi_files)
for path in midi_files:
    original = decode(path.read_bytes())
    tempo = original['tempos'][0]['microsecondsPerQuarter']
    converted = decode(encode(original['events'], 60000000 / tempo, original['ticksPerQuarter'], original['endTick']))
    assert converted == original, path

with tempfile.TemporaryDirectory(prefix='aria-data-test-') as temporary:
    directory = Path(temporary) / 'data'
    shutil.copytree(DATA, directory)
    record_id = 'lesson-1'
    locations = load_packages(directory)['locations']
    path = locations[record_id] / 'performance.mid'
    original = path.read_bytes()
    assert import_midi(directory, record_id, original, apply=True) is False
    assert path.read_bytes() == original
    midi = decode(original)
    for event in midi['events']:
        event['pitch'] += 1
    changed = encode(midi['events'], 60000000 / midi['tempos'][0]['microsecondsPerQuarter'], end_tick=midi['endTick'])
    before = build_catalogue(directory)
    assert import_midi(directory, record_id, changed) is True
    assert path.read_bytes() == original, 'Dry-run import must never mutate data'
    assert import_midi(directory, record_id, changed, apply=True) is True
    after = build_catalogue(directory)
    target = next(l for row in after['lessonLevels'] for l in row if l['id'] == record_id)
    old = next(l for row in before['lessonLevels'] for l in row if l['id'] == record_id)
    assert target['seq'] == [n + 1 for n in old['seq']]
    assert target['f'] == old['f'], 'MIDI import cannot invent fingering'
    assert target['beats'] == old['beats'], 'MIDI import cannot guess written note length'

# A lesson's own unique 1..100 difficulty controls ordering, not a central binding list.
with tempfile.TemporaryDirectory(prefix='aria-difficulty-test-') as temporary:
    directory = Path(temporary) / 'data'
    shutil.copytree(DATA, directory)
    locations = load_packages(directory)[3]
    first = locations['lesson-1'] / 'lesson.yaml'
    second = locations['lesson-2'] / 'lesson.yaml'
    first_config, second_config = read_yaml(first), read_yaml(second)
    before_ids = [row[0]['id'] for row in build_catalogue(directory)['lessonLevels']]
    first.write_text(f"id: lesson-1\ndifficulty: {second_config['difficulty']}\n")
    second.write_text(f"id: lesson-2\ndifficulty: {first_config['difficulty']}\n")
    reordered = build_catalogue(directory)
    after_ids = [row[0]['id'] for row in reordered['lessonLevels']]
    assert (before_ids.index('lesson-1') < before_ids.index('lesson-2')) != (after_ids.index('lesson-1') < after_ids.index('lesson-2'))
    assert reordered['lessonLevels'][after_ids.index('lesson-1')][0]['courseIndex'] == after_ids.index('lesson-1')
    assert sorted(l['id'] for l in reordered['melodyData']) == sorted(l['id'] for l in catalogue['melodyData'])

# Renaming readable package folders must never change course/library ordering.
with tempfile.TemporaryDirectory(prefix='aria-folder-rename-test-') as temporary:
    directory = Path(temporary) / 'data'
    shutil.copytree(DATA, directory)
    before = build_catalogue(directory)
    locations = load_packages(directory)[3]
    lesson_path = locations['lesson-1']
    song_path = locations['repertoire-mary-had-a-little-lamb']
    lesson_path.rename(lesson_path.with_name('zzz-readable-lesson-folder'))
    song_path.rename(song_path.with_name('zzz-readable-song-folder'))
    after = build_catalogue(directory)
    assert [[item['id'] for item in row] for row in after['lessonLevels']] == [[item['id'] for item in row] for row in before['lessonLevels']]
    assert [item['id'] for item in after['melodyData']] == [item['id'] for item in before['melodyData']]

print('PASS 346 distributed packages, source/archive parity, per-song MIDI, imports and 1-100 difficulty ordering and folder-rename stability')
