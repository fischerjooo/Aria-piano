"""Mark a validated development build as the isolated Aria beta preview.

This runs after normal branch validation. It does not change version.json or main.
The built site's relative PWA paths become /Aria-piano/beta/ when copied there.
"""
import argparse
import json
import re
from pathlib import Path

from version import display_version, next_version, read_version

BETA_STORAGE_SHIM = """<script id="aria-beta-storage-isolation">
(function(){
  // /beta/ shares an origin with production; never mix saved lesson progress.
  if (!('Storage' in window)) return;
  const prefix = 'aria-beta::';
  const proto = Storage.prototype;
  const read = proto.getItem, write = proto.setItem, remove = proto.removeItem, clear = proto.clear;
  proto.getItem = function(key) {
    return read.call(this, this === window.localStorage ? prefix + String(key) : key);
  };
  proto.setItem = function(key, value) {
    return write.call(this, this === window.localStorage ? prefix + String(key) : key, value);
  };
  proto.removeItem = function(key) {
    return remove.call(this, this === window.localStorage ? prefix + String(key) : key);
  };
  proto.clear = function() {
    if (this !== window.localStorage) return clear.call(this);
    for (let i = this.length - 1; i >= 0; i--) {
      const key = this.key(i);
      if (key && key.startsWith(prefix)) remove.call(this, key);
    }
  };
})();
</script>"""


def mark_beta(site, version_path, sha, install_base="/Aria-piano/beta/"):
    # Same-origin /beta/ is retained for previewing, but a distinct PWA on
    # Android Chrome requires an independent origin to avoid an install collision.
    if not install_base.startswith("/") or not install_base.endswith("/") or "//" in install_base:
        raise ValueError("install_base must be a path beginning and ending in /")
    site = Path(site)
    version = display_version(next_version(read_version(version_path), "minor"))
    suffix = re.sub(r"[^a-fA-F0-9]", "", sha)[:8].lower() or "preview"
    beta = f"{version}-beta.{suffix}"
    entry = site / "index.html"
    html = entry.read_text(encoding="utf-8")
    if BETA_STORAGE_SHIM.split('"')[1] in html:
        raise ValueError("Beta branding already applied")
    title = re.compile(r"(<title>Aria v)[^<]+?(?=\s*[—-])")
    html, changed = title.subn(lambda m: "<title>Aria (beta) v" + beta, html, count=1)
    if changed != 1:
        raise ValueError("Cannot find Aria page title for beta branding")
    metadata = re.compile(r'(<meta name="application-version" content=")[^"]*(")')
    html = metadata.sub(lambda m: m.group(1) + beta + m.group(2), html, count=1)
    label = re.compile(r'(<span class="brand-version">)[^<]*(</span>)')
    html = label.sub(lambda m: m.group(1) + "v" + beta + m.group(2), html, count=1)
    if '<head>' not in html:
        raise ValueError("No HTML head to isolate beta progress")
    # Android's installed-app label comes from the manifest; these metadata fields
    # also make the beta identity visible in browser tabs and on other platforms.
    apple_title = re.compile(r'(<meta name="apple-mobile-web-app-title" content=")[^"]*(")')
    html, apple_count = apple_title.subn(lambda m: m.group(1) + "Aria (beta)" + m.group(2), html, count=1)
    if apple_count != 1:
        raise ValueError("Expected Apple installed-app title in beta HTML")
    if 'rel="manifest" href="./manifest.webmanifest"' not in html:
        raise ValueError("Beta must link its own scoped PWA manifest")
    html = html.replace(
        '<head>',
        '<head><meta name="robots" content="noindex">'
        '<meta name="application-name" content="Aria (beta)">'
        + BETA_STORAGE_SHIM,
        1,
    )
    entry.write_text(html, encoding="utf-8")
    # Cache Storage is origin-wide: separate beta and stable offline caches.
    # Otherwise a stable service worker could delete a beta's cached app.
    sw_path = site / "sw.js"
    worker = sw_path.read_text(encoding="utf-8")
    if "'aria-piano-shell-v1'" not in worker or "name.startsWith('aria-piano-shell-')" not in worker:
        raise ValueError("Unexpected service-worker cache format")
    worker = worker.replace("'aria-piano-shell-v1'", "'aria-piano-beta-shell-v1'")
    worker = worker.replace("name.startsWith('aria-piano-shell-')", "name.startsWith('aria-piano-beta-shell-')")
    # The worker's HOME and URLs are relative to its /beta/ registration scope.
    if "new URL('./', self.registration.scope)" not in worker or "ARIA_CHECK_UPDATE" not in worker:
        raise ValueError("Beta needs scoped, auto-updating, network-first service worker")
    sw_path.write_text(worker, encoding="utf-8")
    manifest_path = site / "manifest.webmanifest"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["name"] = "Aria (beta)"
    manifest["short_name"] = "Aria (beta)"
    manifest["description"] = "Aria Piano beta preview. Updates automatically from the beta channel."
    # Fixed identity and launch path for each hosting origin. A separate beta
    # hostname + "/" is the reliable Android install route; same-origin nested
    # GitHub Pages cannot guarantee a second installation.
    manifest["id"] = install_base
    manifest["start_url"] = install_base
    manifest["scope"] = install_base
    if manifest.get("display") != "fullscreen":
        raise ValueError("Beta must keep immersive fullscreen when installed")
    if not all((site / icon["src"]).is_file() for icon in manifest.get("icons", [])):
        raise ValueError("Beta icon assets must exist before publication")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Aria beta preview v" + beta)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True, type=Path)
    parser.add_argument("--version-file", required=True, type=Path)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--install-base", default="/Aria-piano/beta/",
                        help="PWA install scope on the deployment origin; use / on a dedicated beta hostname")
    args = parser.parse_args()
    mark_beta(args.site, args.version_file, args.sha, args.install_base)


if __name__ == "__main__":
    main()
