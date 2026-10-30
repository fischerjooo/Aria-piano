"""Regression checks for the permanent /beta/ preview and its release isolation."""
from pathlib import Path
import json
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from beta_preview import mark_beta

with tempfile.TemporaryDirectory() as folder:
    base = Path(folder)
    site = base / "site"
    site.mkdir()
    entry = '<!doctype html><html lang="en"><head><link rel="manifest" href="./manifest.webmanifest"><meta name="apple-mobile-web-app-title" content="Aria Piano"><meta name="application-version" content="5.27"><title>Aria v5.27 — A little music.</title></head><body><span class="brand-version">v5.27</span><script>localStorage.setItem("aria-progress-v1","ok")</script></body></html>'
    (site / "index.html").write_text(entry, encoding="utf-8")
    (site / "sw.js").write_text("const CACHE = 'aria-piano-shell-v1';\\nconst HOME = new URL('./', self.registration.scope).href;\\nconst cleanup = name.startsWith('aria-piano-shell-');\\nconst message = 'ARIA_CHECK_UPDATE';\\n")
    (site / "icons").mkdir()
    (site / "icons/aria-192.png").write_bytes(b"fake icon")
    (site / "manifest.webmanifest").write_text(json.dumps({"name": "Aria Piano", "short_name": "Aria", "id": "./", "start_url": "./", "scope": "./", "display": "fullscreen", "icons": [{"src": "icons/aria-192.png"}]}))
    version = base / "version.json"
    version.write_text('{"major":5,"minor":27}')
    mark_beta(site, version, "a1b2c3d4e5")
    beta_html = (site / "index.html").read_text()
    assert "Aria (beta) v5.28-beta.a1b2c3d4" in beta_html
    assert 'class="brand-version">v5.28-beta.a1b2c3d4</span>' in beta_html
    assert 'name="application-version" content="5.28-beta.a1b2c3d4"' in beta_html
    assert 'id="aria-beta-storage-isolation"' in beta_html
    assert beta_html.index('id="aria-beta-storage-isolation"') < beta_html.index('localStorage.setItem("aria-progress-v1"')
    assert "aria-beta::" in beta_html, "Separate lesson progress from live stable app"
    assert 'name="application-name" content="Aria (beta)"' in beta_html
    assert 'name="apple-mobile-web-app-title" content="Aria (beta)"' in beta_html
    worker=(site / "sw.js").read_text()
    assert "'aria-piano-beta-shell-v1'" in worker
    assert "name.startsWith('aria-piano-beta-shell-')" in worker
    assert "ARIA_CHECK_UPDATE" in worker
    assert (site / "manifest.webmanifest").exists()
    beta_manifest = json.loads((site / "manifest.webmanifest").read_text())
    assert beta_manifest["name"] == "Aria (beta)"
    assert beta_manifest["short_name"] == "Aria (beta)"
    assert beta_manifest["scope"] == beta_manifest["start_url"] == beta_manifest["id"] == "/Aria-piano/beta/"
    assert beta_manifest["icons"][0]["src"] == "icons/aria-192.png", "Relative PWA paths must remain scoped"
    assert json.loads(version.read_text()) == {"major": 5, "minor": 27}, "Beta never increments the stable source version"

pipeline = (ROOT / ".github/workflows/beta.yml").read_text()
pages = (ROOT / ".github/workflows/pages.yml").read_text()
assert "workflow_run:" in pipeline and "workflows: [Validate]" in pipeline
assert "github.event.workflow_run.conclusion == 'success'" in pipeline
assert "github.event.workflow_run.event == 'push'" in pipeline
assert "github.event.workflow_run.head_repository.full_name == github.repository" in pipeline
assert "git worktree add --detach" in pipeline
assert 'git push --force origin "$TESTED_SHA":refs/heads/beta-preview' in pipeline
assert "cp -a" in pipeline and "_site/beta" in pipeline
assert "path: _site" in pipeline and "actions/deploy-pages@v4" in pipeline
assert "group: pages" in pipeline and "group: pages" in pages, "Serialize both deployments"
assert "beta-preview" in pages and "scripts/beta_preview.py" in pages
assert "_site/beta" in pages
assert "python scripts/version.py bump" in pages, "Stable releases still increment"
assert "beta-preview" not in (ROOT / ".github/workflows/ci.yml").read_text(), "Beta branch is only created after successful validation"

print("PASS fixed beta path, beta version suffix, isolated data, gated previews and stable preservation")
