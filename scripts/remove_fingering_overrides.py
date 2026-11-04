"""Remove authored fingering arrays so automatic generation is authoritative."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
changed = 0
for base in (ROOT / 'data' / 'lessons', ROOT / 'data' / 'songs'):
    for path in sorted(base.rglob('notation.json')):
        data = json.loads(path.read_text())
        notation = data.get('notation', {})
        before = set(notation)
        notation.pop('f', None)
        notation.pop('lf', None)
        if set(notation) != before:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
            changed += 1
print(f'Removed hard-coded fingering arrays from {changed} notation packages')
