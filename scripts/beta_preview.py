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


def mark_beta(site, version_path, sha):
    site = Path(site)
    version = display_version(next_version(read_version(version_path), "minor"))
    suffix = re.sub(r"[^a-fA-F0-9]", "", sha)[:8].lower() or "preview"
    beta = f"{version}-beta.{suffix}"
    entry = site / "index.html"
    html = entry.read_text(encoding="utf-8")
    if BETA_STORAGE_SHIM.split('"')[1] in html:
        raise ValueError("Beta branding already applied")
    title = re.compile(r"(<title>Aria v)[^<]+?(?=\s*[—-])")
    html, changed = title.subn(lambda m: m.group(1) + beta, html, count=1)
    if changed != 1:
        raise ValueError("Cannot find Aria page title for beta branding")
    metadata = re.compile(r'(<meta name="application-version" content=")[^"]*(")')
    html = metadata.sub(lambda m: m.group(1) + beta + m.group(2), html, count=1)
    label = re.compile(r'(<span class="brand-version">)[^<]*(</span>)')
    html = label.sub(lambda m: m.group(1) + "v" + beta + m.group(2), html, count=1)
    if '<head>' not in html:
        raise ValueError("No HTML head to isolate beta progress")
    html = html.replace('<head>', '<head><meta name="robots" content="noindex">' + BETA_STORAGE_SHIM, 1)
    entry.write_text(html, encoding="utf-8")
    manifest_path = site / "manifest.webmanifest"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["name"] = "Aria Piano Beta"
    manifest["short_name"] = "Aria Beta"
    # Relative app identity, start URL, service worker and icons remain inside /beta/.
    manifest["id"] = "./"
    manifest["start_url"] = "./"
    manifest["scope"] = "./"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Aria beta preview v" + beta)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True, type=Path)
    parser.add_argument("--version-file", required=True, type=Path)
    parser.add_argument("--sha", required=True)
    args = parser.parse_args()
    mark_beta(args.site, args.version_file, args.sha)


if __name__ == "__main__":
    main()
