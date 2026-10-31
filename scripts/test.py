"""Run the maintained build, package-data, and input regression suites."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
for test in ['pwa-install-tests.py', 'version-tests.py', 'beta-preview-tests.py', 'ble-reconnect-tests.py', 'data-build-tests.py', 'data-midi-negative.py', 'data-validation-negative.py']:
    subprocess.run([sys.executable, str(ROOT / 'tests' / test)], cwd=ROOT, check=True)
# Run the maintained browser-independent regression suite.
subprocess.run([sys.executable, str(ROOT / 'scripts/test_snapshot.py')], cwd=ROOT, check=True)
# Prevent a stale deployment or a silently unexpanded build template.
built = (ROOT / 'index.html').read_bytes()
assert built == (ROOT / 'dist/index.html').read_bytes()
assert all(marker not in built for marker in [b'/*__CATALOGUE__*/', b'/*__STYLES__*/', b'/*__RUNTIME__*/'])
subprocess.run([sys.executable, str(ROOT / 'tests/package-structure-tests.py')], cwd=ROOT, check=True)
print('PASS package build, data validation, and current regression suite')
