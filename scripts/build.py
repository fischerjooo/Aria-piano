"""Build canonical score JSON, standalone app, and a minimal Pages artifact."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def run(*args):
    subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, check=True)

run(ROOT / 'src/repertoire/export_engine_scores.py')
run(ROOT / 'v6/build.py', ROOT / 'src/repertoire/mutopia-519-blue-danube.json',
    ROOT / 'src/repertoire/mutopia-528-ode-satb.json')
candidate = ROOT / 'aria-piano-v6.0-candidate.html'
stable = ROOT / 'aria-piano-v5.26.html'
shutil.copyfile(stable, ROOT / 'index.html')
(ROOT / 'dist').mkdir(exist_ok=True)
shutil.copyfile(stable, ROOT / 'dist/index.html')
site = ROOT / '_site'
if site.exists():
    shutil.rmtree(site)
site.mkdir()
for name in ['index.html', 'aria-piano-v5.26.html', candidate.name]:
    shutil.copyfile(ROOT / name, site / name)
(site / 'experimental').mkdir()
shutil.copyfile(candidate, site / 'experimental/v6.html')
# Retain license notices and the exact score source beside the downloadable app.
shutil.copytree(ROOT / 'src/repertoire', site / 'src/repertoire',
                ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.py'))
(site / '.nojekyll').touch()
print('Built index.html, downloadable candidate, and _site/')
