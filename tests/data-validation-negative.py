"""Exercise authoring validation against corrupted copies of real catalog data."""
from pathlib import Path
import copy, json, shutil, sys, tempfile, unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from lib import catalogue

class NegativeCatalog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.tmp.name) / 'stable'
        shutil.copytree(ROOT / 'data/stable', cls.base)
        cls.original = {name: (cls.base / name).read_bytes() for name in ('notation.json','bindings.json','descriptions.yaml')}
    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()
    def tearDown(self):
        for name, content in self.original.items(): (self.base / name).write_bytes(content)
    def reject_json(self, name, mutate):
        doc = json.loads(self.original[name]); mutate(doc)
        (self.base / name).write_text(json.dumps(doc))
        with self.assertRaises((ValueError, FileNotFoundError)): catalogue.compile_stable(self.base)
    def test_duplicate_yaml_key(self):
        with (self.base / 'descriptions.yaml').open('ab') as f: f.write(b'\nschemaVersion: 1\n')
        with self.assertRaises(ValueError): catalogue.compile_stable(self.base)
    def test_unknown_and_missing_fields(self):
        self.reject_json('bindings.json', lambda d: d.update(unexpected=True))
        self.tearDown()
        self.reject_json('bindings.json', lambda d: d.pop('courseLength'))
    def test_bad_reference(self):
        self.reject_json('bindings.json', lambda d: d['lessonIds'].__setitem__(0, 'nonexistent'))
    def test_bad_midi_path(self):
        self.reject_json('notation.json', lambda d: d['records']['lesson-1'].__setitem__('midi', '../outside.mid'))
    def test_invalid_notation(self):
        self.reject_json('notation.json', lambda d: d['records']['lesson-1']['notation']['f'].__setitem__(0, 6))
    def test_invalid_duration_or_onset(self):
        self.reject_json('notation.json', lambda d: d['records']['lesson-1']['timing'].__setitem__('spacingEndTick', -1))
    def test_bad_midi_bytes(self):
        target = self.base / 'midi/lesson-1.mid'; original = target.read_bytes()
        try:
            target.write_bytes(original + b'bad')
            with self.assertRaises(ValueError): catalogue.compile_stable(self.base)
        finally: target.write_bytes(original)
if __name__ == '__main__': unittest.main()
