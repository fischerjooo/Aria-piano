"""Validate standard authoring data and compile the legacy-compatible app model."""
from copy import deepcopy
import json
import math
from pathlib import Path
import re

import yaml
from jsonschema import Draft202012Validator
from .midi import PPQ, decode

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data'
MUSICAL_FIELDS = ('f', 'lf', 'beats', 'steps', 'holds')


class UniqueSafeLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise ValueError('YAML keys must be unique strings: ' + str(key))
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def finite_tree(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('Non-finite number in data')
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise ValueError('Object keys must be strings')
            finite_tree(child)
    elif isinstance(value, list):
        for child in value:
            finite_tree(child)
    elif value is not None and not isinstance(value, (str, int, float, bool)):
        raise ValueError('Unsupported YAML value type')


def read_yaml(path):
    value = yaml.load(Path(path).read_text(), Loader=UniqueSafeLoader)
    finite_tree(value)
    return value


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    value = json.loads(Path(path).read_text(), object_pairs_hook=pairs,
                       parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Non-finite JSON number')))
    finite_tree(value)
    return value


def safe_path(base, relative):
    if not isinstance(relative, str) or '\\' in relative:
        raise ValueError('Invalid data path')
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts or path.as_posix() != relative:
        raise ValueError('Data paths must be normalized and relative')
    resolved = (base / path).resolve()
    if not resolved.is_relative_to(base.resolve()):
        raise ValueError('Data path escapes its root')
    return resolved


def validate_document(value, schema_name):
    finite_tree(value)
    schema = read_json(DATA / 'schemas' / schema_name)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda error: str(list(error.path)))
    if errors:
        raise ValueError(schema_name + ': ' + '; '.join(error.message for error in errors[:3]))


def ticks(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError('Beat values must be positive finite numbers')
    result = round(value * PPQ)
    return result


def load_packages(directory):
    """Discover self-contained lesson and song packages without a central catalogue.

    Lesson difficulty (1..100) controls course order. Stable IDs, not array
    positions, remain the authoritative identifiers for saved progress.
    """
    directory = Path(directory)
    lesson_dir, song_dir = directory / 'lessons', directory / 'songs'
    if not lesson_dir.is_dir() or not song_dir.is_dir():
        raise ValueError('Expected data/lessons and data/songs package directories')
    descriptions, notations, locations = {}, {}, {}
    courses, songs = [], []

    def collect(package, level=None, expected_id=None, kind=None):
        metadata_file, notation_file = package / 'metadata.yaml', package / 'notation.json'
        description = read_yaml(metadata_file)
        notation = read_json(notation_file)
        if not isinstance(description, dict) or not isinstance(notation, dict):
            raise ValueError('Invalid metadata/notation package: ' + str(package))
        record_id = description.get('id')
        if not isinstance(record_id, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]*', record_id):
            raise ValueError('Invalid package record ID: ' + str(package))
        if expected_id and record_id != expected_id:
            raise ValueError('Package identity differs from folder: ' + str(package))
        if record_id in descriptions:
            raise ValueError('Duplicate package record ID: ' + record_id)
        if kind and description.get('kind') != kind:
            raise ValueError('Unexpected package kind: ' + record_id)
        if level is not None and description.get('level') != level:
            raise ValueError('Unexpected lesson level: ' + record_id)
        if notation.get('midi') != 'performance.mid':
            raise ValueError('MIDI must be in the same package folder: ' + record_id)
        if not (package / 'performance.mid').is_file():
            raise ValueError('Missing MIDI for ' + record_id)
        descriptions[record_id], notations[record_id], locations[record_id] = description, notation, package
        return record_id

    for package in sorted(lesson_dir.iterdir()):
        if not package.is_dir():
            raise ValueError('Unexpected file in lessons: ' + package.name)
        config = read_yaml(package / 'lesson.yaml')
        if not isinstance(config, dict) or set(config) != {'id', 'difficulty'}:
            raise ValueError('Lesson config needs id and difficulty: ' + package.name)
        if not isinstance(config['id'], str) or type(config['difficulty']) is not int or not 1 <= config['difficulty'] <= 100:
            raise ValueError('Lesson id must be text and difficulty must be 1..100: ' + package.name)
        ids = [collect(package, level=0, expected_id=config['id'], kind='lesson')]
        for level in (1, 2):
            ids.append(collect(package / 'levels' / str(level + 1), level=level, kind='lesson'))
        courses.append((config['difficulty'], ids[0], ids))
    if not courses:
        raise ValueError('No lessons found')
    courses.sort(key=lambda value: (value[0], value[1]))
    level_ids = [ids for _, _, ids in courses]
    for new_index, row in enumerate(level_ids):
        for record_id in row:
            descriptions[record_id]['courseIndex'] = new_index

    for package in sorted(song_dir.iterdir()):
        if not package.is_dir():
            raise ValueError('Unexpected file in songs: ' + package.name)
        config = read_yaml(package / 'song.yaml')
        if not isinstance(config, dict) or not isinstance(config.get('id'), str):
            raise ValueError('Invalid song folder identity: ' + package.name)
        if not {'id', 'libraryOrder'} <= set(config) or set(config) - {'id', 'libraryOrder', 'gameOrder'}:
            raise ValueError('Song config needs id and libraryOrder: ' + package.name)
        order = config['libraryOrder']
        if type(order) is not int or order < 1:
            raise ValueError('Invalid song libraryOrder: ' + package.name)
        if 'gameOrder' in config and (type(config['gameOrder']) is not int or config['gameOrder'] < 1):
            raise ValueError('Invalid song gameOrder: ' + package.name)
        record_id = collect(package, expected_id=config['id'], kind='melody')
        songs.append((order, record_id, config.get('gameOrder')))
    songs.sort(key=lambda entry: (entry[0], entry[1]))
    melody_ids = [entry[1] for entry in songs]
    game_ids = [entry[1] for entry in sorted((s for s in songs if s[2] is not None), key=lambda s: (s[2], s[1]))]
    bindings = {'schemaVersion': 1, 'courseLength': len(level_ids),
                'lessonIds': [row[0] for row in level_ids] + melody_ids,
                'melodyIds': melody_ids, 'gameIds': game_ids, 'levelIds': level_ids,
                'levelLabels': ['Introduction', 'Challenge', 'Known melody']}
    descriptions_doc = {'schemaVersion': 1, 'provenance': read_yaml(directory / 'provenance.yaml'),
                        'records': descriptions}
    notation_doc = {'schemaVersion': 1, 'ticksPerQuarter': PPQ, 'records': notations}
    return descriptions_doc, notation_doc, bindings, locations


def compile_stable(data_dir=None):
    directory = Path(data_dir or DATA)
    metadata, notation, bindings, locations = load_packages(directory)
    validate_document(metadata, 'stable-descriptions.schema.json')
    validate_document(notation, 'stable-notation.schema.json')
    validate_document(bindings, 'stable-bindings.schema.json')
    if set(metadata['records']) != set(notation['records']):
        raise ValueError('Description/notation record IDs differ')
    records = {}
    for record_id, description in metadata['records'].items():
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', record_id) or description['id'] != record_id:
            raise ValueError('Invalid record ID')
        if any(k in description for k in ('seq', 'left', *MUSICAL_FIELDS)):
            raise ValueError('Music belongs in MIDI/notation, not descriptions')
        item = notation['records'][record_id]
        midi = decode(safe_path(locations[record_id], item['midi']).read_bytes())
        if midi['ticksPerQuarter'] != PPQ:
            raise ValueError(record_id + ': unexpected MIDI PPQ')
        if midi['tempos'] != [{'tick': 0, 'microsecondsPerQuarter': round(60000000 / description.get('normalBpm', 60))}]:
            raise ValueError(record_id + ': tempo differs from description')
        lanes = {channel: [e for e in midi['events'] if e['channel'] == channel] for channel in (0, 1)}
        count = item['stepCount']
        if len(lanes[0]) != count or len(lanes[1]) != (count if item['secondaryLane'] else 0):
            raise ValueError(record_id + ': MIDI lane/step count differs')
        if len(midi['events']) != sum(map(len, lanes.values())):
            raise ValueError(record_id + ': unexpected MIDI channel')
        music = deepcopy(item['notation'])
        if ('lf' in music) != item['secondaryLane']:
            raise ValueError(record_id + ': secondary fingering differs')
        for key, values in music.items():
            if key not in MUSICAL_FIELDS or len(values) != count:
                raise ValueError(record_id + ': invalid notation array ' + key)
            if key in ('f', 'lf'):
                if any(v != '' and (type(v) is not int or not 1 <= v <= 5) for v in values):
                    raise ValueError(record_id + ': invalid fingering')
            else:
                for value in values:
                    ticks(value)
        timing = item['timing']
        onsets = [event['tick'] for event in lanes[0]]
        if onsets[0] != 0 or any(a >= b for a, b in zip(onsets, onsets[1:])):
            raise ValueError(record_id + ': invalid primary onset sequence')
        steps = [(b-a) / PPQ for a, b in zip(onsets, onsets[1:] + [timing['spacingEndTick']])]
        holds = [event['duration'] / PPQ for event in lanes[0]]
        for key, values in [('stepCorrections', steps), ('holdCorrections', holds)]:
            for index, original in timing[key].items():
                if not index.isdigit() or not 0 <= int(index) < count or ticks(original) != ticks(values[int(index)]):
                    raise ValueError(record_id + ': invalid sub-tick correction')
                if abs(original - values[int(index)]) > .5 / PPQ + 1e-12:
                    raise ValueError(record_id + ': correction exceeds MIDI rounding resolution')
                values[int(index)] = original
        if timing['stepsPresent']:
            music['steps'] = steps
        if timing['holdsPresent']:
            music['holds'] = holds
        for values in (steps, holds):
            for value in values:
                ticks(value)
        cursor = 0
        for i in range(count):
            beat = music.get('beats', [1] * count)[i]
            step = music.get('steps', music.get('beats', [1] * count))[i]
            hold = music.get('holds', music.get('beats', [1] * count))[i]
            duration = ticks(hold)
            for channel in (0, 1) if item['secondaryLane'] else (0,):
                event = lanes[channel][i]
                if event['tick'] != cursor or event['duration'] != duration or event['velocity'] != 80:
                    raise ValueError(record_id + ': MIDI timing differs from notation at step ' + str(i))
                if not 36 <= event['pitch'] <= 96:
                    raise ValueError(record_id + ': pitch outside retained catalogue range')
            ticks(beat)
            cursor += ticks(step)
        end = max(cursor, max(e['tick'] + e['duration'] for e in midi['events']))
        if timing['spacingEndTick'] != cursor or midi['endTick'] != end:
            raise ValueError(record_id + ': MIDI end loses written trailing spacing')
        record = {**description, **deepcopy(music), 'seq': [e['pitch'] for e in lanes[0]]}
        if item['secondaryLane']:
            record['left'] = [e['pitch'] for e in lanes[1]]
        records[record_id] = record
    referenced = set(bindings['lessonIds']) | set(bindings['melodyIds']) | {i for row in bindings['levelIds'] for i in row}
    if referenced != set(records):
        raise ValueError('Unbound or missing catalogue records')
    if bindings['courseLength'] != len(bindings['levelIds']) or len(bindings['lessonIds']) != bindings['courseLength'] + len(bindings['melodyIds']):
        raise ValueError('Course/library count mismatch')
    for key in ('lessonIds', 'melodyIds', 'gameIds'):
        if len(bindings[key]) != len(set(bindings[key])) or not set(bindings[key]) <= set(records):
            raise ValueError('Duplicate or unknown IDs in ' + key)
    for i, row in enumerate(bindings['levelIds']):
        if len(row) != 3 or row[0] != bindings['lessonIds'][i]:
            raise ValueError('Invalid course level binding')
        for level, record_id in enumerate(row):
            record = records[record_id]
            if record.get('courseIndex') != i or record.get('level') != level:
                raise ValueError('Course level metadata mismatch')
    if bindings['lessonIds'][bindings['courseLength']:] != bindings['melodyIds']:
        raise ValueError('Library order mismatch')
    return dict(lessons=[records[i] for i in bindings['lessonIds']],
                lessonLevels=[[records[i] for i in row] for row in bindings['levelIds']],
                melodyData=[records[i] for i in bindings['melodyIds']],
                gameMelodies=[records[i] for i in bindings['gameIds']],
                courseLength=bindings['courseLength'], levelLabels=bindings['levelLabels'])


def runtime_js(catalogue):
    """Hydrate references once so selection/progress retains v5 object identity."""
    records = {l['id']: l for l in catalogue['lessons']}
    for row in catalogue['lessonLevels']:
        for record in row:
            records[record['id']] = record
    payload = dict(records=records, lessonIds=[l['id'] for l in catalogue['lessons']],
                   melodyIds=[l['id'] for l in catalogue['melodyData']],
                   levelIds=[[l['id'] for l in row] for row in catalogue['lessonLevels']],
                   gameIds=[l['id'] for l in catalogue['gameMelodies']],
                   levelLabels=catalogue['levelLabels'])
    encoded = json.dumps(payload, ensure_ascii=False, separators=(',', ':'), allow_nan=False).replace('</', '<\\/')
    return ('// Compiled by discovering data/lessons and data/songs package folders.\n'
            'const catalogue=' + encoded + ';\n'
            'const lessons=catalogue.lessonIds.map(id=>catalogue.records[id]);\n'
            'const lessonLevels=catalogue.levelIds.map(row=>row.map(id=>catalogue.records[id]));\n'
            'const melodyData=catalogue.melodyIds.map(id=>catalogue.records[id]);\n'
            'const gameMelodies=catalogue.gameIds.map(id=>catalogue.records[id]);\n'
            'let courseLength=lessonLevels.length,currentLevel=0;\n'
            'const levelLabels=catalogue.levelLabels;\n')


