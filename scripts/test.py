"""Run source fidelity, curriculum, player and input checks without npm packages."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
for test in ['pwa-install-tests.py', 'version-tests.py', 'beta-preview-tests.py', 'ble-reconnect-tests.py', 'data-build-tests.py', 'data-midi-negative.py', 'data-validation-negative.py']:
    subprocess.run([sys.executable, str(ROOT / 'tests' / test)], cwd=ROOT, check=True)
subprocess.run(['node', str(ROOT / 'tests/data-runtime-parity.cjs')], cwd=ROOT, check=True)
for name in ['validate_sources.py', 'validate_curriculum.py']:
    subprocess.run([sys.executable, str(ROOT / 'src/repertoire' / name)], cwd=ROOT, check=True)
for test in sorted((ROOT / 'v6/tests').glob('*.cjs')):
    subprocess.run(['node', str(test)], cwd=ROOT, check=True)
# Run the full maintained stable regression suite once (all 24 portable files).
subprocess.run([sys.executable, str(ROOT / 'scripts/test_snapshot.py')], cwd=ROOT, check=True)
# Prevent a stale deployment or a silently unexpanded build template.
stable = (ROOT / 'index.html').read_bytes()
assert stable == (ROOT / 'dist/index.html').read_bytes()
assert all(marker not in stable for marker in [b'/*__CATALOGUE__*/', b'/*__STYLES__*/', b'/*__RUNTIME__*/'])
html = (ROOT / 'aria-piano-v6.0-candidate.html').read_bytes()
assert b'/*__CATALOG__*/' not in html and b'/*__LEARNING__*/' not in html
assert b'/*__INPUT__*/' not in html and b'/*__PLAYER__*/' not in html
print('PASS all current tests and built-entrypoint consistency')
