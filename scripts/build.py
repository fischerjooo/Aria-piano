"""Build data-driven stable app, canonical source scores and experimental app."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
from lib.catalogue import compile_stable, compile_learning, runtime_js

ROOT = Path(__file__).resolve().parents[1]

def run(*args):
    subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, check=True)

catalogue = compile_stable()
learning = compile_learning()
(ROOT / 'src/repertoire/learning-path.json').write_text(json.dumps(learning, ensure_ascii=False, indent=2) + '\n')
app = ROOT / 'src/app'
script = (app / 'runtime.js').read_text().replace('/*__CATALOGUE__*/', runtime_js(catalogue))
html = (app / 'template.html').read_text().replace('/*__STYLES__*/', (app / 'styles.css').read_text()).replace('/*__RUNTIME__*/', script)
if any(marker in html for marker in ('/*__STYLES__*/', '/*__RUNTIME__*/', '/*__CATALOGUE__*/')):
    raise ValueError('Unexpanded stable app template')
(ROOT / 'index.html').write_text(html)
(ROOT / 'dist').mkdir(exist_ok=True)
(ROOT / 'dist/index.html').write_text(html)
run(ROOT / 'src/repertoire/export_engine_scores.py')
run(ROOT / 'v6/build.py', ROOT / 'src/repertoire/mutopia-519-blue-danube.json',
    ROOT / 'src/repertoire/mutopia-528-ode-satb.json')
candidate = ROOT / 'aria-piano-v6.0-candidate.html'
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
print('Built data-driven stable index.html, experimental candidate, and _site/')
