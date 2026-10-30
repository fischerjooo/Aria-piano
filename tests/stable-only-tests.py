"""Guard against accidentally rebuilding or redeploying the removed standalone player."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for relative in (
    'v6','data/experimental','src/repertoire','plans',
    'aria-piano-v6.0-candidate.html',
    'data/schemas/learning-bindings.schema.json',
    'data/schemas/learning-descriptions.schema.json',
    'data/schemas/score-descriptions.schema.json',
):
    assert not (ROOT / relative).exists(), f'Unexpected experimental content: {relative}'
build=(ROOT/'scripts/build.py').read_text()
for reference in ('v6/build.py','export_engine_scores.py','aria-piano-v6.0-candidate.html','experimental/v6.html'):
    assert reference not in build, reference
assert (ROOT/'index.html').read_bytes() == (ROOT/'dist/index.html').read_bytes()
site=ROOT/'_site'
assert (site/'index.html').read_bytes()==(ROOT/'index.html').read_bytes()
assert not (site/'experimental').exists()
assert not (site/'src/repertoire').exists()
assert not (site/'aria-piano-v6.0-candidate.html').exists()
assert (site/'manifest.webmanifest').is_file()
print('PASS only the stable player and stable authored catalogue are built and staged')
