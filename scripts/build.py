"""Build the stable Aria piano app and its Pages assets."""
from pathlib import Path
import shutil
import subprocess
import sys
from lib.catalogue import build_catalogue, runtime_js
from version import read_version, display_version

ROOT = Path(__file__).resolve().parents[1]

def run(*args):
    subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, check=True)

run(ROOT / 'scripts/branding_icons.py')
catalogue = build_catalogue()
app = ROOT / 'src/app'
script = (app / 'runtime.js').read_text().replace('/*__CATALOGUE__*/', runtime_js(catalogue))
html = (app / 'template.html').read_text().replace('/*__STYLES__*/', (app / 'styles.css').read_text()).replace('/*__RUNTIME__*/', script).replace('/*__PWA__*/', (app / 'pwa.js').read_text()).replace('__ARIA_VERSION__', display_version(read_version()))
if any(marker in html for marker in ('/*__STYLES__*/', '/*__RUNTIME__*/', '/*__CATALOGUE__*/', '/*__PWA__*/', '__ARIA_VERSION__')):
    raise ValueError('Unexpanded stable app template')
(ROOT / 'index.html').write_text(html)
(ROOT / 'dist').mkdir(exist_ok=True)
(ROOT / 'dist/index.html').write_text(html)
site = ROOT / '_site'
if site.exists():
    shutil.rmtree(site)
site.mkdir()
shutil.copyfile(ROOT / 'index.html', site / 'index.html')
# Install assets are deployed beside the stable GitHub Pages entrypoint.
shutil.copyfile(ROOT / 'manifest.webmanifest', site / 'manifest.webmanifest')
shutil.copyfile(ROOT / 'sw.js', site / 'sw.js')
shutil.copytree(ROOT / 'icons', site / 'icons')
(site / '.nojekyll').touch()
print('Built stable index.html, dist/index.html, and production _site/ only')
