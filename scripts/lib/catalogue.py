"""Discover, validate, and build Aria's folder-based lesson and song packages."""
from copy import deepcopy
import json
import math
from pathlib import Path
import re

import yaml
from .midi import PPQ, decode

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data'
MUSICAL_FIELDS = ('f', 'lf', 'beats', 'steps', 'holds')
LEVEL_LABELS = ['Introduction', 'Challenge', 'Known melody']


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
    value = json.loads(
        Path(path).read_text(),
        object_pairs_hook=pairs,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Non-finite JSON number')),
    )
    finite_tree(value)
    return value


def ticks(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError('Beat values must be positive finite numbers')
    return round(value * PPQ)


def _text_fields(record_id, description, fields):
    missing = [key for key in fields if not isinstance(description.get(key), str) or not description[key].strip()]
    if missing:
        raise ValueError(record_id + ': missing required display fields: ' + ', '.join(missing))


def _validate_notation(record_id, item):
    if not isinstance(item, dict) or set(item) != {'midi', 'stepCount', 'secondaryLane', 'notation', 'timing'}:
        raise ValueError(record_id + ': notation.json has unexpected fields')
    if item['midi'] != 'performance.mid':
        raise ValueError(record_id + ': MIDI must be performance.mid in the same folder')
    count = item['stepCount']
    if type(count) is not int or count < 1:
        raise ValueError(record_id + ': stepCount must be a positive integer')
    if type(item['secondaryLane']) is not bool:
        raise ValueError(record_id + ': secondaryLane must be boolean')
    music = item['notation']
    if not isinstance(music, dict) or not set(music) <= set(MUSICAL_FIELDS) or 'f' not in music:
        raise ValueError(record_id + ': invalid notation fields')
    for key, values in music.items():
        if not isinstance(values, list) or len(values) != count:
            raise ValueError(record_id + ': invalid notation array ' + key)
        if key in ('f', 'lf'):
            if any(v != '' and (type(v) is not int or not 1 <= v <= 5) for v in values):
                raise ValueError(record_id + ': invalid fingering')
        else:
            for value in values:
                ticks(value)
    if ('lf' in music) != item['secondaryLane']:
        raise ValueError(record_id + ': secondary fingering differs from secondaryLane')
    timing = item['timing']
    required_timing = {'spacingEndTick', 'stepsPresent', 'holdsPresent', 'stepCorrections', 'holdCorrections'}
    if not isinstance(timing, dict) or set(timing) != required_timing:
        raise ValueError(record_id + ': invalid timing fields')
    if type(timing['spacingEndTick']) is not int or timing['spacingEndTick'] < 0:
        raise ValueError(record_id + ': invalid spacingEndTick')
    for key in ('stepsPresent', 'holdsPresent'):
        if type(timing[key]) is not bool:
            raise ValueError(record_id + ': ' + key + ' must be boolean')
    for key in ('stepCorrections', 'holdCorrections'):
        corrections = timing[key]
        if not isinstance(corrections, dict):
            raise ValueError(record_id + ': ' + key + ' must be an object')
        for index, value in corrections.items():
            if not isinstance(index, str) or not index.isdigit() or not 0 <= int(index) < count:
                raise ValueError(record_id + ': invalid timing correction index')
            ticks(value)


def load_packages(directory=DATA):
    """Discover packages. Ordering comes only from package attributes."""
    directory = Path(directory)
    lesson_dir, song_dir = directory / 'lessons', directory / 'songs'
    if not lesson_dir.is_dir() or not song_dir.is_dir():
        raise ValueError('Expected data/lessons and data/songs package directories')

    records, locations = {}, {}
    lesson_groups, songs = [], []
    lesson_difficulties, song_orders, game_orders = {}, {}, {}

    def collect(package, *, expected_id=None, kind=None, level=None, require_nav=False):
        description = read_yaml(package / 'metadata.yaml')
        notation = read_json(package / 'notation.json')
        if not isinstance(description, dict):
            raise ValueError('Invalid metadata package: ' + str(package))
        record_id = description.get('id')
        if not isinstance(record_id, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]*', record_id):
            raise ValueError('Invalid package record ID: ' + str(package))
        if expected_id is not None and record_id != expected_id:
            raise ValueError('Package identity differs from package config: ' + str(package))
        if record_id in records:
            raise ValueError('Duplicate package record ID: ' + record_id)
        if description.get('kind') != kind:
            raise ValueError('Unexpected package kind: ' + record_id)
        if level is not None and description.get('level') != level:
            raise ValueError('Unexpected lesson level: ' + record_id)
        if kind == 'lesson':
            fields = ['title', 'sub', 'time', 'hand', 'instruction', 'fingering', 'tip']
            if require_nav:
                fields.append('nav')
            _text_fields(record_id, description, fields)
        elif kind == 'melody':
            _text_fields(record_id, description, ('title', 'nav', 'sub', 'time', 'hand'))
        if any(key in description for key in ('seq', 'left', *MUSICAL_FIELDS)):
            raise ValueError(record_id + ': music belongs in notation.json/performance.mid')
        _validate_notation(record_id, notation)
        midi_path = package / 'performance.mid'
        if not midi_path.is_file():
            raise ValueError('Missing MIDI for ' + record_id)
        records[record_id] = {'metadata': description, 'notation': notation, 'folder': package}
        locations[record_id] = package
        return record_id

    for package in sorted(lesson_dir.iterdir()):
        if not package.is_dir():
            raise ValueError('Unexpected file in lessons: ' + package.name)
        config = read_yaml(package / 'lesson.yaml')
        if not isinstance(config, dict) or set(config) != {'id', 'difficulty'}:
            raise ValueError('Lesson config needs exactly id and difficulty: ' + package.name)
        if not isinstance(config['id'], str):
            raise ValueError('Lesson id must be text: ' + package.name)
        difficulty = config['difficulty']
        if type(difficulty) is not int or not 1 <= difficulty <= 100:
            raise ValueError('Lesson difficulty must be an integer from 1 to 100: ' + package.name)
        if difficulty in lesson_difficulties:
            raise ValueError(f'Lesson difficulty collision {difficulty}: {lesson_difficulties[difficulty]} and {package.name}')
        lesson_difficulties[difficulty] = package.name
        ids = [collect(package, expected_id=config['id'], kind='lesson', level=0, require_nav=True)]
        for level in (1, 2):
            ids.append(collect(package / 'levels' / str(level + 1), kind='lesson', level=level))
        lesson_groups.append((difficulty, ids))

    if not lesson_groups:
        raise ValueError('No lessons found')
    lesson_groups.sort(key=lambda entry: entry[0])
    level_ids = [ids for _, ids in lesson_groups]
    for course_index, row in enumerate(level_ids):
        for record_id in row:
            records[record_id]['metadata']['courseIndex'] = course_index

    for package in sorted(song_dir.iterdir()):
        if not package.is_dir():
            raise ValueError('Unexpected file in songs: ' + package.name)
        config = read_yaml(package / 'song.yaml')
        allowed = {'id', 'libraryOrder', 'gameOrder'}
        if not isinstance(config, dict) or not {'id', 'libraryOrder'} <= set(config) or not set(config) <= allowed:
            raise ValueError('Song config needs id, libraryOrder, and optional gameOrder: ' + package.name)
        if not isinstance(config['id'], str):
            raise ValueError('Song id must be text: ' + package.name)
        order = config['libraryOrder']
        if type(order) is not int or order < 1:
            raise ValueError('Song libraryOrder must be a positive integer: ' + package.name)
        if order in song_orders:
            raise ValueError(f'Song libraryOrder collision {order}: {song_orders[order]} and {package.name}')
        song_orders[order] = package.name
        game_order = config.get('gameOrder')
        if game_order is not None:
            if type(game_order) is not int or game_order < 1:
                raise ValueError('Song gameOrder must be a positive integer: ' + package.name)
            if game_order in game_orders:
                raise ValueError(f'Song gameOrder collision {game_order}: {game_orders[game_order]} and {package.name}')
            game_orders[game_order] = package.name
        record_id = collect(package, expected_id=config['id'], kind='melody')
        songs.append((order, game_order, record_id))

    songs.sort(key=lambda entry: entry[0])
    melody_ids = [record_id for _, _, record_id in songs]
    game_ids = [record_id for _, _, record_id in sorted((entry for entry in songs if entry[1] is not None), key=lambda entry: entry[1])]

    return {
        'records': records,
        'locations': locations,
        'levelIds': level_ids,
        'melodyIds': melody_ids,
        'gameIds': game_ids,
    }


def _materialize_record(record_id, package):
    description = package['metadata']
    item = package['notation']
    midi = decode((package['folder'] / 'performance.mid').read_bytes())
    if midi['ticksPerQuarter'] != PPQ:
        raise ValueError(record_id + ': unexpected MIDI PPQ')
    expected_tempo = round(60000000 / description.get('normalBpm', 60))
    if midi['tempos'] != [{'tick': 0, 'microsecondsPerQuarter': expected_tempo}]:
        raise ValueError(record_id + ': tempo differs from metadata')

    lanes = {channel: [event for event in midi['events'] if event['channel'] == channel] for channel in (0, 1)}
    count = item['stepCount']
    if len(lanes[0]) != count or len(lanes[1]) != (count if item['secondaryLane'] else 0):
        raise ValueError(record_id + ': MIDI lane/step count differs')
    if len(midi['events']) != sum(map(len, lanes.values())):
        raise ValueError(record_id + ': unexpected MIDI channel')

    music = deepcopy(item['notation'])
    timing = item['timing']
    onsets = [event['tick'] for event in lanes[0]]
    if not onsets or onsets[0] != 0 or any(a >= b for a, b in zip(onsets, onsets[1:])):
        raise ValueError(record_id + ': invalid primary onset sequence')

    steps = [(b - a) / PPQ for a, b in zip(onsets, onsets[1:] + [timing['spacingEndTick']])]
    holds = [event['duration'] / PPQ for event in lanes[0]]
    for key, values in [('stepCorrections', steps), ('holdCorrections', holds)]:
        for index, original in timing[key].items():
            if ticks(original) != ticks(values[int(index)]):
                raise ValueError(record_id + ': invalid sub-tick correction')
            if abs(original - values[int(index)]) > .5 / PPQ + 1e-12:
                raise ValueError(record_id + ': correction exceeds MIDI rounding resolution')
            values[int(index)] = original

    if timing['stepsPresent']:
        music['steps'] = steps
    if timing['holdsPresent']:
        music['holds'] = holds

    cursor = 0
    beats = music.get('beats', [1] * count)
    step_values = music.get('steps', beats)
    hold_values = music.get('holds', beats)
    for i in range(count):
        duration = ticks(hold_values[i])
        for channel in (0, 1) if item['secondaryLane'] else (0,):
            event = lanes[channel][i]
            if event['tick'] != cursor or event['duration'] != duration or event['velocity'] != 80:
                raise ValueError(record_id + ': MIDI timing differs from notation at step ' + str(i))
            if not 36 <= event['pitch'] <= 96:
                raise ValueError(record_id + ': pitch outside supported range')
        ticks(beats[i])
        cursor += ticks(step_values[i])

    end = max(cursor, max(event['tick'] + event['duration'] for event in midi['events']))
    if timing['spacingEndTick'] != cursor or midi['endTick'] != end:
        raise ValueError(record_id + ': MIDI end loses written trailing spacing')

    record = {**deepcopy(description), **music, 'seq': [event['pitch'] for event in lanes[0]]}
    if item['secondaryLane']:
        record['left'] = [event['pitch'] for event in lanes[1]]
    return record


def build_catalogue(data_dir=None):
    """Build the runtime catalogue directly from folder packages."""
    package_index = load_packages(data_dir or DATA)
    records = {
        record_id: _materialize_record(record_id, package)
        for record_id, package in package_index['records'].items()
    }

    level_ids = package_index['levelIds']
    melody_ids = package_index['melodyIds']
    game_ids = package_index['gameIds']
    referenced = set(melody_ids) | set(game_ids) | {record_id for row in level_ids for record_id in row}
    if referenced != set(records):
        raise ValueError('Unbound or missing package records')
    if len(melody_ids) != len(set(melody_ids)) or len(game_ids) != len(set(game_ids)):
        raise ValueError('Duplicate song IDs after package discovery')
    for course_index, row in enumerate(level_ids):
        if len(row) != 3:
            raise ValueError('Every lesson must contain exactly three levels')
        for level, record_id in enumerate(row):
            record = records[record_id]
            if record.get('courseIndex') != course_index or record.get('level') != level:
                raise ValueError('Lesson level metadata mismatch: ' + record_id)

    lesson_levels = [[records[record_id] for record_id in row] for row in level_ids]
    melodies = [records[record_id] for record_id in melody_ids]
    return {
        'lessons': [row[0] for row in lesson_levels] + melodies,
        'lessonLevels': lesson_levels,
        'melodyData': melodies,
        'gameMelodies': [records[record_id] for record_id in game_ids],
        'courseLength': len(lesson_levels),
        'levelLabels': LEVEL_LABELS,
    }


def runtime_js(catalogue):
    records = {lesson['id']: lesson for lesson in catalogue['lessons']}
    for row in catalogue['lessonLevels']:
        for record in row:
            records[record['id']] = record
    payload = {
        'records': records,
        'lessonIds': [lesson['id'] for lesson in catalogue['lessons']],
        'melodyIds': [lesson['id'] for lesson in catalogue['melodyData']],
        'levelIds': [[lesson['id'] for lesson in row] for row in catalogue['lessonLevels']],
        'gameIds': [lesson['id'] for lesson in catalogue['gameMelodies']],
        'levelLabels': catalogue['levelLabels'],
    }
    encoded = json.dumps(payload, ensure_ascii=False, separators=(',', ':'), allow_nan=False).replace('</', '<\\/')
    return (
        '// Compiled from data/lessons and data/songs packages.\n'
        'const catalogue=' + encoded + ';\n'
        'const lessons=catalogue.lessonIds.map(id=>catalogue.records[id]);\n'
        'const lessonLevels=catalogue.levelIds.map(row=>row.map(id=>catalogue.records[id]));\n'
        'const melodyData=catalogue.melodyIds.map(id=>catalogue.records[id]);\n'
        'const gameMelodies=catalogue.gameIds.map(id=>catalogue.records[id]);\n'
        'let courseLength=lessonLevels.length,currentLevel=0;\n'
        'const levelLabels=catalogue.levelLabels;\n'
    )
