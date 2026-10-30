"""Run the maintained stable build, data and input regression suites."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
for test in ['pwa-install-tests.py', 'version-tests.py', 'beta-preview-tests.py', 'ble-reconnect-tests.py', 'data-build-tests.py', 'data-midi-negative.py', 'data-validation-negative.py']:
    subprocess.run([sys.executable, str(ROOT / 'tests' / test)], cwd=ROOT, check=True)
subprocess.run(['node', str(ROOT / 'tests/data-runtime-parity.cjs')], cwd=ROOT, check=True)
# Run the full maintained stable regression suite once (all 24 portable files).
subprocess.run([sys.executable, str(ROOT / 'scripts/test_snapshot.py')], cwd=ROOT, check=True)
# Prevent a stale deployment or a silently unexpanded build template.
stable = (ROOT / 'index.html').read_bytes()
assert stable == (ROOT / 'dist/index.html').read_bytes()
assert all(marker not in stable for marker in [b'/*__CATALOGUE__*/', b'/*__STYLES__*/', b'/*__RUNTIME__*/'])
subprocess.run([sys.executable, str(ROOT / 'tests/stable-only-tests.py')], cwd=ROOT, check=True)
print('PASS stable-only build, data and current regression suite')
