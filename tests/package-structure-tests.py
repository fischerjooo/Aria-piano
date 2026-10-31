"""Guard the package-only data/build architecture."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'

for relative in (
    'data/stable',
    'data/schemas/stable-descriptions.schema.json',
    'data/schemas/stable-notation.schema.json',
    'data/schemas/stable-bindings.schema.json',
):
    assert not (ROOT / relative).exists(), f'Legacy catalogue artifact reappeared: {relative}'

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

build = (ROOT / 'scripts/build.py').read_text()
catalogue = (ROOT / 'scripts/lib/catalogue.py').read_text()
for forbidden in ('compile_stable', 'stable-bindings', 'stable-descriptions', 'stable-notation', 'data/stable'):
    assert forbidden not in build + catalogue, f'Legacy catalogue reference remains: {forbidden}'

assert (ROOT / 'index.html').read_bytes() == (ROOT / 'dist/index.html').read_bytes()
site = ROOT / '_site'
assert (site / 'index.html').read_bytes() == (ROOT / 'index.html').read_bytes()
assert not (site / 'aria-piano-v5.26.html').exists()
assert (site / 'manifest.webmanifest').is_file()
print('PASS package-only data model and build output')
