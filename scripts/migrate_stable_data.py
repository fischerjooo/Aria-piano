"""One-time explicit migration of the immutable v5.26 snapshot into authoring data.

Never called by build.py: builds read the extracted files, not the old generators.
The old archive is read only. This conversion makes no new notes or fingerings.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import yaml
from lib.midi import PPQ, encode
from lib.catalogue import MUSICAL_FIELDS, ROOT, ticks


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def migrate():
    archive = ROOT / 'aria-piano-v5.26.html'
    snapshot = json.loads(subprocess.check_output(['node', str(ROOT / 'scripts/export_runtime.cjs'), str(archive)], cwd=ROOT))
    records = {l['id']: l for l in snapshot['lessons']}
    for row in snapshot['lessonLevels']:
        for record in row:
            if record['id'] in records and records[record['id']] != record:
                raise ValueError('Same ID has different materialized records')
            records[record['id']] = record
    destination = ROOT / 'data/stable'
    (destination / 'midi').mkdir(parents=True, exist_ok=True)
    descriptions, notation = {}, {}
    for record_id, record in records.items():
        descriptions[record_id] = {k: v for k, v in record.items() if k not in ('seq', 'left', *MUSICAL_FIELDS)}
        music = {k: v for k, v in record.items() if k in ('f', 'lf', 'beats')}
        count = len(record['seq'])
        events, cursor, step_corrections, hold_corrections = [], 0, {}, {}
        for i in range(count):
            beat = record.get('beats', [1] * count)[i]
            hold = record.get('holds', record.get('beats', [1] * count))[i]
            step = record.get('steps', record.get('beats', [1] * count))[i]
            if step != ticks(step) / PPQ:
                step_corrections[str(i)] = step
            if hold != ticks(hold) / PPQ:
                hold_corrections[str(i)] = hold
            for channel, key in [(0, 'seq'), (1, 'left')]:
                if key in record:
                    events.append(dict(tick=cursor, duration=ticks(hold), pitch=record[key][i], channel=channel, velocity=80))
            cursor += ticks(step)
        relative = f'midi/{record_id}.mid'
        end = max(cursor, max(e['tick'] + e['duration'] for e in events))
        (destination / relative).write_bytes(encode(events, record.get('normalBpm', 60), end_tick=end))
        notation[record_id] = dict(midi=relative, stepCount=count, secondaryLane='left' in record, notation=music,
            timing=dict(spacingEndTick=cursor, stepsPresent='steps' in record, holdsPresent='holds' in record,
                        stepCorrections=step_corrections, holdCorrections=hold_corrections))
    provenance = dict(archive=archive.name, sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                      status='historical-generated-content-preserved',
                      note='Frozen v5.26 studies, including generated variations and suggested fingering. This format migration does not establish authentic score provenance, change rights, improve pedagogy or introduce newly composed notes.')
    (destination / 'descriptions.yaml').write_text(yaml.safe_dump(dict(schemaVersion=1, provenance=provenance, records=descriptions), sort_keys=False, allow_unicode=True, width=110))
    write_json(destination / 'notation.json', dict(schemaVersion=1, ticksPerQuarter=PPQ, records=notation))
    write_json(destination / 'bindings.json', dict(schemaVersion=1, courseLength=snapshot['courseLength'],
        lessonIds=[l['id'] for l in snapshot['lessons']], melodyIds=[l['id'] for l in snapshot['melodyData']],
        gameIds=[l['id'] for l in snapshot['gameMelodies']], levelIds=[[l['id'] for l in row] for row in snapshot['lessonLevels']], levelLabels=snapshot['levelLabels']))
    source = archive.read_text()
    head, rest = source.split('<style>', 1)
    css, rest = rest.split('</style>', 1)
    markup, rest = rest.split('<script>', 1)
    script, tail = rest.rsplit('</script>', 1)
    # Keep the mature engine and every UI function; replace music generators with data hydration.
    start, end = script.index('const lessons=['), script.index('function levelPassed(')
    script = script[:start] + '/*__CATALOGUE__*/\n' + script[end:]
    start, end = script.index('/* Original Aria exercises'), script.index('function curriculumEscape(')
    script = script[:start] + script[end:]
    start, end = script.index('const BAYLOR_CURRICULUM_SPECS='), script.index('let notationSizing=')
    script = script[:start] + script[end:]
    app = ROOT / 'src/app'
    app.mkdir(exist_ok=True)
    (app / 'styles.css').write_text(css)
    (app / 'runtime.js').write_text(script)
    (app / 'template.html').write_text(head + '<style>/*__STYLES__*/</style>' + markup + '<script>/*__RUNTIME__*/</script>' + tail)
    learning = json.loads((ROOT / 'src/repertoire/learning-path.json').read_text())
    lessons = learning.pop('lessons')
    text_keys = ('title', 'objective', 'guide')
    text = {l['id']: {k: l[k] for k in text_keys if k in l} for l in lessons}
    bindings = [{k: v for k, v in l.items() if k not in text_keys} for l in lessons]
    (ROOT / 'data/experimental/learning-descriptions.yaml').write_text(yaml.safe_dump(dict(schemaVersion=1, path=learning, lessons=text), sort_keys=False, allow_unicode=True, width=110))
    write_json(ROOT / 'data/experimental/learning-bindings.json', dict(schemaVersion=1, lessons=bindings))
    print(f'Migrated {len(records)} historical studies, {len(lessons)} experimental source-bound tasks; archive unchanged')


if __name__ == '__main__':
    migrate()
