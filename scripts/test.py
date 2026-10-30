"""Run source fidelity, curriculum, player and input checks without npm packages."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
for name in ['validate_sources.py', 'validate_curriculum.py']:
    subprocess.run([sys.executable, str(ROOT / 'src/repertoire' / name)], cwd=ROOT, check=True)
for test in sorted((ROOT / 'v6/tests').glob('*.cjs')):
    subprocess.run(['node', str(test)], cwd=ROOT, check=True)
# Passing v5.26 baseline; see tests/TEST-STATUS.md for all 24 snapshot results.
for name in ['piano-center-playhead-tests.cjs', 'piano-curriculum-tests.cjs', 'piano-dsp-tests.cjs', 'piano-early-holds-tests.cjs', 'piano-independent-rhythm-tests.cjs', 'piano-melody-cleanup-tests.cjs', 'piano-notation-sizing-tests.cjs', 'piano-quick-controls-tests.cjs', 'piano-release-window-tests.cjs', 'piano-replay-midi-tests.cjs', 'piano-tests.cjs', 'piano-timing-option-tests.cjs', 'piano-timing-sync-tests.cjs']:
    subprocess.run(['node', str(ROOT / 'tests' / name)], cwd=ROOT, check=True)
# Prevent a stale deployment or a silently unexpanded build template.
stable = (ROOT / 'aria-piano-v5.26.html').read_bytes()
assert stable == (ROOT / 'index.html').read_bytes()
assert stable == (ROOT / 'dist/index.html').read_bytes()
html = (ROOT / 'aria-piano-v6.0-candidate.html').read_bytes()
assert b'/*__CATALOG__*/' not in html and b'/*__LEARNING__*/' not in html
assert b'/*__INPUT__*/' not in html and b'/*__PLAYER__*/' not in html
print('PASS all current tests and built-entrypoint consistency')
