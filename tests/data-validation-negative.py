"""Adversarial package validation across self-contained study folders."""
from pathlib import Path
import json, shutil, sys, tempfile, unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from lib import catalogue


class NegativeCatalog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.tmp.name) / 'data'
        shutil.copytree(catalogue.DATA, cls.base)
    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def modify(self, relative, update):
        if relative.startswith('lessons/lesson-1/'):
            target = catalogue.load_packages(self.base)['locations']['lesson-1'] / relative.split('/', 2)[2]
        elif relative.startswith('songs/repertoire-hot-cross-buns/'):
            target = catalogue.load_packages(self.base)[3]['repertoire-hot-cross-buns'] / relative.split('/', 2)[2]
        else:
            target = self.base / relative
        before = target.read_bytes()
        try:
            update(target)
            with self.assertRaises((ValueError, FileNotFoundError, KeyError)):
                catalogue.build_catalogue(self.base)
        finally:
            target.write_bytes(before)

    def corrupt_json(self, relative, mutate):
        def change(path):
            value = json.loads(path.read_text())
            mutate(value)
            path.write_text(json.dumps(value))
        self.modify(relative, change)

    def test_duplicate_yaml_key(self):
        self.modify('lessons/lesson-1/metadata.yaml', lambda p: p.write_text(p.read_text() + '\nid: duplicated\n'))

    def test_bad_difficulty(self):
        for score in ['0', '101', 'true']:
            self.modify('lessons/lesson-1/lesson.yaml', lambda p: p.write_text('id: lesson-1\ndifficulty: ' + score + '\n'))

    def test_lesson_difficulty_collision(self):
        locations = catalogue.load_packages(self.base)[3]
        first = locations['lesson-1'] / 'lesson.yaml'
        second = locations['lesson-2'] / 'lesson.yaml'
        first_config, second_config = catalogue.read_yaml(first), catalogue.read_yaml(second)
        before = second.read_bytes()
        try:
            second.write_text(f"id: {second_config['id']}\ndifficulty: {first_config['difficulty']}\n")
            with self.assertRaisesRegex(ValueError, 'Lesson difficulty collision'):
                catalogue.load_packages(self.base)
        finally:
            second.write_bytes(before)

    def test_song_library_order_collision(self):
        song_folders = sorted((self.base / 'songs').iterdir())
        first, second = song_folders[:2]
        a, b = catalogue.read_yaml(first / 'song.yaml'), catalogue.read_yaml(second / 'song.yaml')
        before = (second / 'song.yaml').read_bytes()
        try:
            b['libraryOrder'] = a['libraryOrder']
            (second / 'song.yaml').write_text(__import__('yaml').safe_dump(b, sort_keys=False))
            with self.assertRaisesRegex(ValueError, 'Song libraryOrder collision'):
                catalogue.load_packages(self.base)
        finally:
            (second / 'song.yaml').write_bytes(before)

    def test_song_game_order_collision(self):
        game = []
        for folder in sorted((self.base / 'songs').iterdir()):
            config = catalogue.read_yaml(folder / 'song.yaml')
            if 'gameOrder' in config:
                game.append((folder, config))
            if len(game) == 2:
                break
        self.assertEqual(len(game), 2)
        (first, a), (second, b) = game
        before = (second / 'song.yaml').read_bytes()
        try:
            b['gameOrder'] = a['gameOrder']
            (second / 'song.yaml').write_text(__import__('yaml').safe_dump(b, sort_keys=False))
            with self.assertRaisesRegex(ValueError, 'Song gameOrder collision'):
                catalogue.load_packages(self.base)
        finally:
            (second / 'song.yaml').write_bytes(before)

    def test_missing_song_config_field(self):
        self.modify('songs/repertoire-hot-cross-buns/song.yaml',
                    lambda p: p.write_text('id: repertoire-hot-cross-buns\n'))

    def test_bad_package_identity(self):
        self.modify('lessons/lesson-1/lesson.yaml',
                    lambda p: p.write_text('id: nonexistent\ndifficulty: 1\n'))

    def test_bad_midi_path(self):
        self.corrupt_json('lessons/lesson-1/notation.json', lambda d: d.__setitem__('midi', '../outside.mid'))

    def test_invalid_notation(self):
        self.corrupt_json('lessons/lesson-1/notation.json', lambda d: d['notation']['f'].__setitem__(0, 6))

    def test_invalid_duration(self):
        self.corrupt_json('lessons/lesson-1/notation.json', lambda d: d['timing'].__setitem__('spacingEndTick', -1))

    def test_bad_midi_bytes(self):
        self.modify('lessons/lesson-1/performance.mid',
                    lambda p: p.write_bytes(p.read_bytes() + b'bad'))


if __name__ == '__main__':
    unittest.main()
