"""Validate installed Aria fullscreen PWA configuration and deployment assets."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'manifest.webmanifest').read_text())
assert manifest['display'] == 'fullscreen', 'Installed Aria must launch fullscreen'
assert manifest['start_url'] == './' and manifest['scope'] == './'
assert manifest['icons'], 'Install icons required'
for icon in manifest['icons']:
    path = ROOT / icon['src']
    assert path.is_file(), f'Missing icon: {path}'
    assert path.read_bytes().startswith(bytes.fromhex('89504e470d0a1a0a')), f'Invalid PNG: {path}'
build = (ROOT / 'scripts/build.py').read_text()
assert "shutil.copyfile(ROOT / 'manifest.webmanifest', site / 'manifest.webmanifest')" in build
assert "shutil.copytree(ROOT / 'icons', site / 'icons')" in build
page = (ROOT / 'src/app/template.html').read_text()
assert 'rel="manifest" href="./manifest.webmanifest"' in page
assert 'class="app-nav home-nav"' in page
assert 'src="./icons/aria-192.png"' in page, 'Home screen should show the installed app icon'
assert 'class="brand-version">v5.26</span>' in page, 'Show the current stable version after Aria'
assert 'id="homeFullscreen"' in page, 'Fullscreen must be accessible from the home screen'
runtime = (ROOT / 'src/app/runtime.js').read_text()
assert "$('homeFullscreen').onclick" in runtime
assert "(display-mode: fullscreen)" in runtime, 'Already-fullscreen PWAs must not request fullscreen again'
print('PASS immersive fullscreen PWA manifest, icons and Pages build configuration')
