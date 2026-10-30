"""Version source of truth, generated headers and release bump behavior."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from version import read_version, display_version, next_version

version = read_version()
label = "v" + display_version(version)
template = (ROOT / "src/app/template.html").read_text()
assert template.count("__ARIA_VERSION__") == 3, "Version marker required in title, metadata and home header"
app = (ROOT / "index.html").read_text()
assert f"<title>Aria {label} " in app, "Browser title must contain release version"
assert f'<meta name="application-version" content="{display_version(version)}">' in app
assert f'class="brand-version">{label}</span>' in app
assert "__ARIA_VERSION__" not in app
assert (ROOT / "dist/index.html").read_text() == app
assert json.loads((ROOT / "version.json").read_text()) == version
assert next_version({"major": 5, "minor": 26}, "minor") == {"major": 5, "minor": 27}
assert next_version({"major": 5, "minor": 26}, "major") == {"major": 6, "minor": 0}

with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / "version.json"
    path.write_text('{"major": 5, "minor": 26}\n')
    cli = [sys.executable, str(ROOT / "scripts/version.py")]
    assert subprocess.check_output([*cli, "bump", "--part", "minor", "--file", str(path)], text=True).strip() == "5.27"
    assert subprocess.check_output([*cli, "bump", "--part", "major", "--file", str(path)], text=True).strip() == "6.0"
    assert read_version(path) == {"major": 6, "minor": 0}
    for invalid in ['{"major":true,"minor":1}', '{"major":5,"minor":-1}', '{"major":5,"minor":2,"patch":0}']:
        path.write_text(invalid)
        try:
            read_version(path)
            raise AssertionError(f"Accepted invalid version: {invalid}")
        except ValueError:
            pass

workflow = (ROOT / ".github/workflows/pages.yml").read_text()
assert "branches: [main]" in workflow, "Normal main publishes must bump the version"
assert "workflow_dispatch:" in workflow and "options:" in workflow, "Manual release selection required"
assert "- minor" in workflow and "- major" in workflow
assert 'python scripts/version.py bump --part "$RELEASE_PART"' in workflow
assert "git add version.json index.html dist/index.html" in workflow
assert "git push origin HEAD:main" in workflow
assert "needs: build" in workflow, "Deployment must wait for the verified release"

print("PASS release version source, displayed title/header, automatic minor, manual major reset and invalid inputs")
