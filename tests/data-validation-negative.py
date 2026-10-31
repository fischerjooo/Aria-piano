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
        target = self.base / relative
        before = target.read_bytes()
        try:
            update(target)
            with self.assertRaises((ValueError, FileNotFoundError, KeyError)):
                catalogue.compile_stable(self.base)
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
