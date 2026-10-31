"""Guard the package-only data/build architecture."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'

lesson_folders = [path for path in (DATA / 'lessons').iterdir() if path.is_dir()]
song_folders = [path for path in (DATA / 'songs').iterdir() if path.is_dir()]
assert len(lesson_folders) == 68
assert len(song_folders) == 142

for folder in lesson_folders:
    assert (folder / 'lesson.yaml').is_file()
    for path in (folder, folder / 'levels/2', folder / 'levels/3'):
        for name in ('metadata.yaml', 'notation.json', 'performance.mid'):
            assert (path / name).is_file(), f'Missing {name}: {path}'

for folder in song_folders:
    assert (folder / 'song.yaml').is_file()
    for name in ('metadata.yaml', 'notation.json', 'performance.mid'):
        assert (folder / name).is_file(), f'Missing {name}: {folder}'

catalogue_source = (ROOT / 'scripts/lib/catalogue.py').read_text()
assert 'def build_catalogue(' in catalogue_source
assert "directory / 'lessons'" in catalogue_source
assert "directory / 'songs'" in catalogue_source

assert (ROOT / 'index.html').read_bytes() == (ROOT / 'dist/index.html').read_bytes()
site = ROOT / '_site'
assert (site / 'index.html').read_bytes() == (ROOT / 'index.html').read_bytes()
assert (site / 'manifest.webmanifest').is_file()
print('PASS package-only data model and build output')
