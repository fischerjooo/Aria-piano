# Aria-piano

Piano teach web app with a self-contained HTML download, sheet music, local progress, touch, microphone, MIDI and Bluetooth input.

**Stable default: the v5.26 interface and curriculum, with the published app version tracked in `version.json`.** The root `index.html` and `dist/index.html` now compile from modular app sources plus MIDI/YAML/JSON data, preserving the established interface and features. `aria-piano-v5.26.html` remains the immutable historical archive. The v6 source-first rewrite is experimental: it has useful score provenance and timing work, but it is not a feature-complete replacement for v5.26. Its separate downloadable file is `aria-piano-v6.0-candidate.html`; the Pages build also exposes `experimental/v6.html`.

Next development direction: bring the verified v6 score model and source-bound learning path into the polished v5 experience, preserving existing controls, notation readability, learning flow and input options. Compare both versions in a real browser before changing the stable default. The experimental rewrite must not silently replace the stable app.

## Local development

Requires Python 3.12+ and Node.js 22+. Build-only Python dependencies are pinned in `requirements-build.txt`; the downloadable application remains self-contained with no runtime dependencies or npm packages.

```sh
python -m pip install -r requirements-build.txt
python scripts/build.py
python scripts/test.py
python -m http.server 8000
```

Open `http://localhost:8000/` for stable v5.26 or `http://localhost:8000/aria-piano-v6.0-candidate.html` for the experimental candidate. Microphone, Web MIDI and Web Bluetooth depend on browser support, secure contexts and user permission. Actual hardware testing is still required.

`build.py` validates and compiles 346 existing studies from Standard MIDI performances, YAML descriptions and JSON notation/bindings, then assembles the stable HTML from `src/app/template.html`, `styles.css` and `runtime.js`. It no longer runs the old music generators. It also rebuilds the two canonical experimental scores from retained LilyPond, compiles the 23 source-bound tasks from YAML/JSON, assembles the separate v6 candidate and stages the minimal `_site/` deployment. Only that directory is published.

See [data/README.md](data/README.md) for authoring boundaries, exact legacy timing corrections, schemas and offline MIDI import/export commands. This is a format/build refactor: the historical generated content and fingering are preserved, not relabeled as verified editions or improved teaching material.

`test.py` runs exact materialized catalogue parity against the immutable archive, all 346 MIDI round trips, import/dry-run/apply and negative validation tests, source/publisher-MIDI comparisons, all 23 curriculum bindings, six experimental v6 test files and 13 passing stable regression files (including the 89-case core suite). It does not certify browser appearance or hardware compatibility.

All 24 original v5.26 test files from commit `612273319a4e70a1b9b7b10ff7e5b6fc8f736b76` are preserved byte-for-byte under `archive/tests-v5.26-original/`. Portable copies in `tests/` target the stable root, use the retained v3.1 DSP fixture and write optional diagnostics to ignored `test-results/`. Run `python scripts/test_snapshot.py` to execute every file; it reports 13 passing files and 11 known historical failures, then exits nonzero. See `tests/TEST-STATUS.md`. Assertions were not rewritten to make those historical tests pass.

Later v5.27 releases/tests remain in `archive/`; v6 source, research and checks remain under their original development directories. Neither later version replaces the stable v5.26 entrypoint.

## Bluetooth MIDI on Android

Pair your BLE MIDI piano once with **Connect & pair piano**. Aria remembers the permitted piano locally and reuses the already-authorized `BluetoothDevice` for reconnection if it disconnects while the same app page is still alive. Returning to the active app after switching away attempts that reconnection when needed.

For a fresh launch, Aria can reconnect without the chooser **only if** the browser supports `navigator.bluetooth.getDevices()` and retains permission. Chrome for Android may not expose that API, even though initial pairing works. In that case, press **Connect & pair piano** on each fresh launch; Aria should not claim that session-level reconnection is unavailable. Manually pressing Disconnect disables automatic retries until you connect again.

A service worker cannot hold or reestablish a Bluetooth connection in the background; Web Bluetooth is unavailable there. The operating system may suspend pages when hidden. Avoid continuous background wake locks or fake worker keep-alive loops. Reliable always-on background BLE would require a native Android app with an appropriate foreground service, not just a GitHub Pages PWA.

## Permanent beta preview

The latest **validated development-branch build** is available at **https://fischerjooo.github.io/Aria-piano/beta/**, while the stable published app stays at **https://fischerjooo.github.io/Aria-piano/**. These are two paths under one GitHub Pages deployment; the production app always lives at the root.

**Every feature-branch push:** The existing **Validate** workflow builds and tests the branch. After a successful *push* run in this repository (not a pull-request workflow or fork), the trusted **Publish validated beta preview** workflow checks out the exact tested commit, builds and retests it, and deploys a combined site: current released `main` in the root and the branch build in `/beta/`. Failed development builds never replace the last working beta. The shared `pages` concurrency group prevents overlapping beta and stable deployments. The latest successfully validated development branch becomes the rolling beta; successive pushes replace it at the same link. Branch and pull-request tests do not increment `version.json`.

**On normal main releases:** The regular **Build and deploy Pages** workflow keeps the latest beta by rebuilding from the saved `beta-preview` branch reference and overlays that preview under `/beta/`. The `beta-preview` ref is managed by the beta workflow and records the latest validated development commit. Publishing a stable release does not replace beta with stable or remove its fixed URL.

Beta has an unmistakable version such as **v5.29-beta.a1b2c3d4**: the next minor release candidate plus the first eight characters of the validated commit SHA. Beta's page title, visible header label, and HTML application-version metadata all use this suffix. Its web-app manifest names it **Aria Piano Beta** and its service worker, installed app identity, and icons use relative `/beta/` paths. Beta's browser-local lesson/progress settings are automatically namespaced separately from stable. **Do not treat beta as your primary progress store**, and always test on the correct URL.

**Important:** The repository Settings → Pages must use **GitHub Actions** and Actions must have the required Pages deployment / branch-write permissions. The first beta build appears after the beta workflow is on `main` and a development branch passes validation (or a validated beta source ref is seeded). GitHub Pages deployments do not allow unrelated workflow runs to host two sites independently; both workflows publish a combined artifact.

## Release versioning

The release version has one source of truth: `version.json`, currently starting at `v5.26`. The stable music content is independently preserved byte-for-byte against the frozen v5.26 archive; incrementing a release number does not claim that the content or music has changed.

**Normal development/publishing:** Work on a feature branch and open a pull request. CI builds and tests at the **current** release number; PR checks do not bump versions. After a change is merged or pushed to `main`, **Build and deploy Pages** automatically increments the **minor** version (for example `5.26 → 5.27`), rebuilds and tests the app, commits the version and generated HTML back to `main`, and publishes that same tested build. The GitHub Actions bot uses `GITHUB_TOKEN`; its release commit does not start another publish run, so it cannot loop.

**Major release option:** Open **Actions → Build and deploy Pages → Run workflow** on `main` and select **major**. That increments the major number and resets minor to **0** (for example `5.27 → 6.0`). Selecting **minor** instead publishes another minor release. Both options run the same build, validation, commit and GitHub Pages deployment process.

The browser title, home header and HTML application-version metadata are generated from `version.json` by `scripts/build.py`. Do not hand-edit these generated labels or the historical v5.26 archive. For local testing, run `python scripts/version.py show`; to exercise version increments in a temporary copy, run `python scripts/version.py bump --part minor --file /tmp/aria-version-test.json` on a copy of the version file. A published release is recorded on `main` only after checks pass. Release automation requires Actions to have permission to push version commits to `main`.

## GitHub Pages

Branch commits run **Validate** automatically; pull requests also validate the proposed merge. Passing development-branch pushes publish the rolling **/beta/** preview without altering stable. Merges and direct pushes to `main` run **Build and deploy Pages**: build → selected regression/source tests → generated-file consistency check → upload `_site/` → deploy. Any failed check blocks publication. Main commits use the Pages workflow's checks rather than duplicating the branch-push run. Both workflows support manual runs; publication is restricted to `main`. Concurrent branch validations cancel older runs for the same event/ref; Pages deployments run serially. No personal access token is required. The full historical snapshot still contains 11 documented failures; these are preserved in `tests/TEST-STATUS.md`, not silently treated as passing.

One-time repository setup: open **Settings → Pages → Build and deployment → Source → GitHub Actions**. After enabling this source, push to `main` or manually run **Build and deploy Pages** from the Actions tab. The expected project URL is `https://fischerjooo.github.io/Aria-piano/`; it becomes available only after Pages is enabled and deployment succeeds. Repository or organization policy may require an administrator to enable Actions or approve the `github-pages` environment.

## Source and development map

- `src/app/`: stable application markup template, styles and mature runtime engine.
- `data/`: authored standard MIDI/YAML/JSON catalogue, source-task descriptions/bindings and enforced schemas.
- `scripts/catalogue.py`: offline validation and MIDI import/export.
- `v6/`: experimental score engine, input adapters, template, builder, tests and review notes.
- `src/repertoire/`: retained source editions, hashes, canonical timed scores, conversion and independent source/curriculum validation.
- `plans/`: repertoire requirements, research catalog, book targets, release scope, engine audit and QA gates.
- `archive/`: earlier HTML releases from v3.1 through v5.27, release notes and legacy tests. Their generated lesson content is historical and must not be confused with verified source editions.
- `AGENTS.md`: development continuity and acceptance requirements.

## Repertoire and licenses

The experimental candidate imports one complete published main-theme piano arrangement of Blue Danube (Mutopia 519), one complete soprano extraction from an Ode to Joy SATB setting (Mutopia 528), and 23 exact-source practice tasks. This is not the complete orchestral Blue Danube, an original piano Ode arrangement, a complete beginner course, or all 37 book targets.

The repository's existing MIT `LICENSE` is preserved for application code. Music editions and derived score data retain their own terms and attribution; the repository license does not override them. Blue Danube's arrangement and typesetting are © 2014 Nikos Kouremenos, based on Christian Mondrup / WIMA, Mutopia-2014/03/24-519, CC BY-SA 4.0; conversion changes representation, not musical notes. Ode to Joy's SATB setting is typeset by Peter Chubb, Mutopia-2009/08/05-528, Public Domain; the soprano is extracted unchanged. Source headers, per-score `license`, `licenseUrl`, `sourceAttribution`, `sourceUrl`, and `source-manifest.json` are retained. Other editions in the research catalog have individual terms; reference status does not establish embedding permission.
