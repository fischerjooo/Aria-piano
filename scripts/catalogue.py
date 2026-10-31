"""Inspect, validate, export and import folder-based lesson and song packages."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile

import yaml
from lib.catalogue import DATA, PPQ, build_catalogue, load_packages, read_json, read_yaml
from lib.midi import decode, encode


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def import_midi(directory, record_id, midi_bytes, written_values=None, apply=False):
    """Edit only the selected package, keeping MIDI, notation and metadata together.

    A reviewed import may change note pitches and their onset/hold timing.
    Written beat values and fingering are never guessed from MIDI contact.
    """
    directory = Path(directory)
    build_catalogue(directory)
    locations = load_packages(directory)['locations']
    if record_id not in locations:
        raise ValueError('Unknown study ID: ' + record_id)
    folder = locations[record_id]
    notation_file = folder / 'notation.json'
    metadata_file = folder / 'metadata.yaml'
    midi_file = folder / 'performance.mid'
    item = read_json(notation_file)
    description = read_yaml(metadata_file)
    existing = midi_file.read_bytes()
    if midi_bytes == existing and written_values is None:
        return False
    midi = decode(midi_bytes)
    if midi['ticksPerQuarter'] != PPQ or len(midi['tempos']) != 1 or midi['tempos'][0]['tick'] != 0:
        raise ValueError('Import requires PPQ 9600 and one initial tempo')
    primary = [event for event in midi['events'] if event['channel'] == 0]
    secondary = [event for event in midi['events'] if event['channel'] == 1]
    if len(primary) != item['stepCount'] or len(secondary) != (len(primary) if item['secondaryLane'] else 0):
        raise ValueError('Import changes step count or lane count; update notation first')
    if len(primary) + len(secondary) != len(midi['events']):
        raise ValueError('Import supports channel 0 and simultaneous channel 1 only')
    if any(event['velocity'] != 80 for event in midi['events']):
        raise ValueError('Performance velocities other than 80 require explicit review')
    for a, b in zip(primary, secondary):
        if (a['tick'], a['duration']) != (b['tick'], b['duration']):
            raise ValueError('Staggered or unequal-duration secondary notes are unsupported')
    item['timing'] = dict(spacingEndTick=midi['endTick'], stepsPresent=True,
                          holdsPresent=True, stepCorrections={}, holdCorrections={})
    if written_values is not None:
        item['notation']['beats'] = written_values
    tempo = midi['tempos'][0]['microsecondsPerQuarter']
    old_bpm = description.get('normalBpm', 60)
    if tempo != round(60000000 / old_bpm):
        description['normalBpm'] = round(60000000 / tempo, 6)

    with tempfile.TemporaryDirectory(prefix='aria-package-import-') as temporary:
        staged = Path(temporary) / 'data'
        shutil.copytree(directory, staged)
        copy = staged / folder.relative_to(directory)
        (copy / 'performance.mid').write_bytes(midi_bytes)
        write_json(copy / 'notation.json', item)
        (copy / 'metadata.yaml').write_text(yaml.safe_dump(description, sort_keys=False, allow_unicode=True, width=110))
        build_catalogue(staged)
        if apply:
            for name in ('performance.mid', 'notation.json', 'metadata.yaml'):
                shutil.copyfile(copy / name, folder / name)
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
        catalogue = build_catalogue()
        print(f"PASS {len(catalogue['lessonLevels']) * 3} course levels, {len(catalogue['melodyData'])} melodies")
    elif args.command == 'inspect-midi':
        print(json.dumps(decode(args.file.read_bytes()), indent=2))
    elif args.command == 'export-midi':
        build_catalogue()
        locations = load_packages(DATA)['locations']
        if args.id not in locations:
            raise ValueError('Unknown study ID')
        args.output.write_bytes((locations[args.id] / 'performance.mid').read_bytes())
        print(args.output)
    else:
        written = read_json(args.written_values) if args.written_values else None
        changed = import_midi(DATA, args.id, args.file.read_bytes(), written, args.apply)
        print('Imported and validated' if args.apply and changed else 'Validated; no files written')


if __name__ == '__main__':
    main()
