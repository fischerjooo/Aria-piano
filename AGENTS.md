# Aria development continuity

Production is the stable `index.html` and `dist/index.html` assembled from `src/app/`, `data/stable/`, and `version.json`. Preserve the established UI, 68 lessons with three existing levels, 142 song records, progress identifiers and all touch, MIDI, Bluetooth MIDI and microphone controls. The versioned `aria-piano-v5.26.html` snapshot and `archive/` are historical evidence and should not be altered.

There is only one active player and one catalog model. Do not recreate or publish a second experimental score engine, separate lesson browser or unrelated playable song database. The formerly separate prototype, its staging files, score imports and standalone build/tests have been removed at the owner's request. New changes should improve the released player and be reviewed before merging.

## Build and checks

Use Python 3.12+, Node.js 22+, and `requirements-build.txt`:

```
python -m pip install -r requirements-build.txt
python scripts/build.py
python scripts/test.py
```

The builder regenerates the stable `index.html` and `dist/index.html`, PNG brand icons and a production-only `_site/` tree. `_site/` is disposable and ignored by Git. Build does not change `data/stable/` and does not stage independent players or unpublished score editions. Retain the exact MIDI/YAML/JSON migration boundaries in `data/README.md`. Do not use the one-time `scripts/migrate_stable_data.py` to perform normal edits.

`scripts/test.py` runs data, version, PWA/BLE and the 24 maintained stable regression tests. `python scripts/test_snapshot.py` runs those same 24 portable stable tests; frozen originals are kept separately under `archive/tests-v5.26-original/`. CI also runs responsive Playwright screenshot and functional browser checks. Automated tests do not certify physical hardware or screen quality on actual devices.

## Edition policy and changes

Retained stable study data is historical; some older arrangements and fingering were generated and do not establish exact score-edition provenance. Never relabel existing studies as certified source editions. Any future classical score import needs its own verified composer, edition, permissions, attribution and notation tests. Keep source-specific publication rights separate from the application MIT license. Do not fabricate score content or finger choices.

Keep the current app's navigation, score readability, fixed-center playhead, full-sheet view, tempo/hands controls, touch, MIDI/Bluetooth MIDI, microphone fallback, local progress and installability. Test UI changes visually on mobile and tablet.

## Publishing and owner approval

The stable root site lives at `https://fischerjooo.github.io/Aria-piano/`. `pages.yml` builds, tests, increments `version.json` on a normal main release and deploys one Pages artifact. Beta preview at `/Aria-piano/beta/` is a separately branded preview of the same stable player, not a second experimental engine. Its progress is namespaced and its PWA identity scoped. A separately installable Android beta still requires a different HTTPS origin; GitHub Pages `/beta/` may collide with the root PWA.

Use a `feature/*` or `fix/*` branch from `main` for substantial changes. CI must succeed on the exact SHA; a successful validated branch push can publish the fixed rolling beta through `.github/workflows/beta.yml` and update `beta-preview`. Verify the exact preview SHA and successful Pages deployment before calling a beta ready. **Do not merge a proposed feature until the owner explicitly approves it.** A directly requested minor change to main may follow the existing direct-main exception, with tests and successful Pages publication. Never let beta deploy over stable root. Preserve GitHub Actions release versioning and avoid version bump loops.

Application identity: Aria piano in production and Aria piano (beta) for the branded preview. `icons/aria.svg` is the sole master (A monogram, gold note and keyboard); icons for both channels must show identical artwork. `scripts/branding_icons.py` produces the PNG icons. Do not commit credentials, temporary test captures, caches or dependencies.
