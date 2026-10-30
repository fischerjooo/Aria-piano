# Development and repository notes

This document retains developer context formerly held in the main README. **The public-facing starting point is [README.md](../README.md).**

## Build and tests

Requires Python 3.12+ and Node.js 22+. Build-time dependencies are pinned in `requirements-build.txt`; the downloadable HTML remains self-contained.

```sh
python -m pip install -r requirements-build.txt
python scripts/build.py
python scripts/test.py
python -m http.server 8000
```

The root application is assembled from `src/app/` and `data/stable/`, using the established interface and preserved progression data. `aria-piano-v5.26.html` is a frozen historical archive; current released HTML is generated from `version.json`. The 346 MIDI records represent 204 lesson variants and 142 melody records. No separate score-engine prototype is built or published.

`scripts/branding_icons.py` produces stable and beta 192px, 512px and maskable Android PNGs from `icons/aria.svg`. The same SVG is the homepage icon and favicon. `scripts/build.py` regenerates these assets and stages the `_site/` deployment.

The core `scripts/test.py` runs stable catalogue and MIDI parity, app/version/PWA tests, BLE regression checks and all 24 maintained portable stable regressions. `python scripts/test_snapshot.py` runs those same maintained 24 files; original v5.26 historical fixtures remain in `archive/tests-v5.26-original/`. Passing automation is not equivalent to physical MIDI/BLE/microphone testing.

See [data/README.md](../data/README.md), [AGENTS.md](../AGENTS.md) and [docs/TESTING.md](TESTING.md) for the current catalogue, development workflow and acceptance constraints.

## Channels and publishing

- **Live:** https://fischerjooo.github.io/Aria-piano/
- **Beta browser preview:** https://fischerjooo.github.io/Aria-piano/beta/

Feature branches run validation. A passing feature-branch push may update the rolling beta preview; it does not replace the stable release. Main publishes are built and tested by `.github/workflows/pages.yml`, which increments the released minor version from `version.json` and stages the production Pages artifact, retaining the last validated beta when possible.

Stable and beta are served under the same GitHub Pages hostname. Chrome for Android may not support independently installing both PWA identities reliably. A separately installable beta requires a configured different HTTPS origin and a deployment of the validated `beta-preview` branch; `vercel.json` is provided as optional hosting configuration, not proof of an existing independent beta URL.

The site service worker caches the icon and app resources for offline use; changes to branding should advance the cache name and its related regression assertion.

## Project areas

- `src/app/`: app markup, styles, runtime and browser integrations.
- `data/`: stable MIDI/YAML/JSON study material and schemas.
- `archive/`: historical HTML and test baselines.
- `scripts/`: builders, validators and release helpers.
- `tests/`: current regression checks, with known historical limitations recorded.

## Licensing and music provenance

Application code uses [MIT](../LICENSE). Existing study data retains the notices recorded in `data/stable/descriptions.yaml`; this does not establish a new license for third-party works. Future music imports require a separate edition-level copyright and attribution review.
