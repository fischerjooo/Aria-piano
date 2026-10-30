"""Run every retained v5.26 regression; exits nonzero for known historical failures."""
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
failed = []
for test in sorted((ROOT / 'tests').glob('*-tests.cjs')):
    result = subprocess.run(['node', str(test)], cwd=ROOT)
    if result.returncode:
        failed.append(test.name)
print(f'{24-len(failed)}/24 test files passed; failing files: {", ".join(failed)}')
sys.exit(bool(failed))
