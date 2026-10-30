"""Inspect, validate, export and import canonical stable MIDI, entirely offline."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile

import yaml
from lib.catalogue import DATA, PPQ, compile_stable, read_json, read_yaml, safe_path
from lib.midi import decode, encode


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def import_midi(directory, record_id, midi_bytes, written_values=None, apply=False):
    """Import a reviewed performance without inferring notation or fingering.

    Stable v5 steps require one primary event, optionally one simultaneous second
    event. More complex polyphony is unsupported by this stable importer.
    """
    compile_stable(directory)
    descriptions = read_yaml(directory / 'descriptions.yaml')
    notation = read_json(directory / 'notation.json')
    if record_id not in notation['records']:
        raise ValueError('Unknown study ID')
    item = notation['records'][record_id]
    relative = item['midi']
    existing = safe_path(directory, relative).read_bytes()
    if midi_bytes == existing and written_values is None:
        return False
    midi = decode(midi_bytes)
    if midi['ticksPerQuarter'] != PPQ or len(midi['tempos']) != 1 or midi['tempos'][0]['tick'] != 0:
        raise ValueError('Import requires PPQ 9600 and one initial tempo; tempo maps are unsupported by stable v5')
    primary = [event for event in midi['events'] if event['channel'] == 0]
    secondary = [event for event in midi['events'] if event['channel'] == 1]
    if len(primary) != item['stepCount'] or len(secondary) != (len(primary) if item['secondaryLane'] else 0):
        raise ValueError('Import changes step count or lane count: author explicit notation/fingering first')
    if len(primary) + len(secondary) != len(midi['events']):
        raise ValueError('Import supports primary channel 0 and secondary channel 1 only')
    if any(event['velocity'] != 80 for event in midi['events']):
        raise ValueError('Legacy studies use velocity 80; varying performance velocities require another engine')
    for a, b in zip(primary, secondary):
        if (a['tick'], a['duration']) != (b['tick'], b['duration']):
            raise ValueError('Stable v5 cannot express staggered or unequal-duration secondary notes')
    # Preserve the imported end-of-track as the final written onset spacing.
    # The MIDI must include the final release and any intended trailing silence.
    item['timing'] = dict(spacingEndTick=midi['endTick'], stepsPresent=True,
                          holdsPresent=True, stepCorrections={}, holdCorrections={})
    if written_values is not None:
        item['notation']['beats'] = written_values
    old_bpm = descriptions['records'][record_id].get('normalBpm', 60)
    tempo = midi['tempos'][0]['microsecondsPerQuarter']
    if tempo != round(60000000 / old_bpm):
        descriptions['records'][record_id]['normalBpm'] = round(60000000 / tempo, 6)
    # Validate staged files completely before applying any authoring changes.
    with tempfile.TemporaryDirectory(prefix='aria-midi-import-') as temporary:
        staging = Path(temporary) / 'stable'
        shutil.copytree(directory, staging)
        safe_path(staging, relative).write_bytes(midi_bytes)
        write_json(staging / 'notation.json', notation)
        (staging / 'descriptions.yaml').write_text(yaml.safe_dump(descriptions, sort_keys=False, allow_unicode=True, width=110))
        compile_stable(staging)
        if apply:
            for name in (relative, 'notation.json', 'descriptions.yaml'):
                shutil.copyfile(safe_path(staging, name), safe_path(directory, name))
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('validate')
    inspect = commands.add_parser('inspect-midi')
    inspect.add_argument('file', type=Path)
    export = commands.add_parser('export-midi')
    export.add_argument('id')
    export.add_argument('output', type=Path)
    importer = commands.add_parser('import-midi')
    importer.add_argument('id')
    importer.add_argument('file', type=Path)
    importer.add_argument('--written-values', type=Path, help='Explicit JSON array of notated beat values; never inferred from key contact')
    importer.add_argument('--apply', action='store_true', help='Write after validating the complete staged catalogue (default: validate only)')
    args = parser.parse_args()
    if args.command == 'validate':
        stable = compile_stable()
        print(f"PASS {len(stable['lessonLevels']) * 3} course levels, {len(stable['melodyData'])} melodies")
    elif args.command == 'inspect-midi':
        print(json.dumps(decode(args.file.read_bytes()), indent=2))
    elif args.command == 'export-midi':
        compile_stable()
        records = read_json(DATA / 'stable/notation.json')['records']
        if args.id not in records:
            raise ValueError('Unknown study ID')
        args.output.write_bytes(safe_path(DATA / 'stable', records[args.id]['midi']).read_bytes())
        print(args.output)
    else:
        written = read_json(args.written_values) if args.written_values else None
        changed = import_midi(DATA / 'stable', args.id, args.file.read_bytes(), written, args.apply)
        print('Imported and validated' if args.apply and changed else 'Validated; no files written')


if __name__ == '__main__':
    main()
