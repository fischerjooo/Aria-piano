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

The root app is assembled from `src/app/` and `data/`. The default stable interface preserves the v5.26 learning experience; `aria-piano-v5.26.html` is a frozen historical archive. The independent `aria-piano-v6.0-candidate.html` / `experimental/v6.html` source-first prototype is experimental, not a feature-complete replacement.

The catalogue includes 346 existing studies. Experimental score-source work has 23 source-bound practice tasks based on two separately attributed source editions. Do not present the experimental catalogue as verified for all legacy studies.

`scripts/branding_icons.py` produces stable and beta 192px, 512px and maskable Android PNGs from `icons/aria.svg`. The same SVG is the homepage icon and favicon. `scripts/build.py` regenerates these assets and stages the `_site/` deployment.

The core `scripts/test.py` suite checks validated selected regressions, catalogue parity and source data. The optional `python scripts/test_snapshot.py` executes all 24 preserved historical v5.26 test files, including 11 documented historical failures; see `tests/TEST-STATUS.md`. Passing automation is not equivalent to real-device, visual, microphone or hardware testing.

See [data/README.md](../data/README.md), [AGENTS.md](../AGENTS.md) and `plans/` for the exact catalogue, edition, development and acceptance constraints.

## Channels and publishing

- **Live:** https://fischerjooo.github.io/Aria-piano/
- **Beta browser preview:** https://fischerjooo.github.io/Aria-piano/beta/

Feature branches run validation. A passing feature-branch push may update the rolling beta preview; it does not replace the stable release. Main publishes are built and tested by `.github/workflows/pages.yml`, which increments the released minor version from `version.json` and stages the production Pages artifact, retaining the last validated beta when possible.

Stable and beta are served under the same GitHub Pages hostname. Chrome for Android may not support independently installing both PWA identities reliably. A separately installable beta requires a configured different HTTPS origin and a deployment of the validated `beta-preview` branch; `vercel.json` is provided as optional hosting configuration, not proof of an existing independent beta URL.

The site service worker caches the icon and app resources for offline use; changes to branding should advance the cache name and its related regression assertion.

## Project areas

- `src/app/`: app markup, styles, runtime and browser integrations.
- `data/`: stable MIDI/YAML/JSON study material and schemas.
- `src/repertoire/`: source score representations and license metadata.
- `v6/`: separate experimental score engine and tests.
- `archive/`: historical HTML and test baselines.
- `scripts/`: builders, validators and release helpers.
- `tests/`: current regression checks, with known historical limitations recorded.

## Licensing and music provenance

Application code uses [MIT](../LICENSE). Third-party scores and extracted musical works retain individual permissions, attribution and license terms. The Blue Danube Mutopia 519 arrangement is credited to Nikos Kouremenos, derived from Christian Mondrup/WIMA, under CC BY-SA 4.0; the Ode to Joy Mutopia 528 SATB setting is typeset by Peter Chubb and identified as Public Domain. Inspect retained source manifests and per-score attribution before redistribution.
