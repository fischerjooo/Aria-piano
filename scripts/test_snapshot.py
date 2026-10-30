"""Run all maintained portable stable regressions; preserve frozen originals separately."""
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
failed = []
for test in sorted((ROOT / 'tests').glob('*-tests.cjs')):
    result = subprocess.run(['node', str(test)], cwd=ROOT)
    if result.returncode:
        failed.append(test.name)
total = len(list((ROOT / 'tests').glob('*-tests.cjs')))
print(f'{total-len(failed)}/{total} portable stable test files passed; failing files: {", ".join(failed) or "none"}')
sys.exit(bool(failed))
