# Aria development continuity

Production is `index.html` and `dist/index.html`, assembled from `src/app/`, discovered packages in `data/lessons/` and `data/songs/`, and `version.json`. Preserve the established UI, 68 lessons with three levels, 142 song records, progress identifiers and all touch, MIDI, Bluetooth MIDI and microphone controls. Package folders are the only catalogue source of truth.

There is only one active player and one catalog model. Do not recreate or publish a second experimental score engine, separate lesson browser or unrelated playable song database. The formerly separate prototype, its staging files, score imports and standalone build/tests have been removed at the owner's request. New changes should improve the released player and be reviewed before merging.

## Build and checks

Use Python 3.12+, Node.js 22+, and `requirements-build.txt`:

```
python -m pip install -r requirements-build.txt
python scripts/build.py
python scripts/test.py
```

The builder regenerates `index.html` and `dist/index.html`, PNG brand icons and a production-only `_site/` tree. `_site/` is disposable and ignored by Git. Build does not change authored item packages in `data/lessons/` or `data/songs/`. Retain the exact MIDI/YAML/JSON package boundaries and attribute-based dynamic discovery documented in `data/README.md`.

`scripts/test.py` runs package-data, version, PWA/BLE and maintained regression tests. `python scripts/test_snapshot.py` runs the portable application tests. CI also runs responsive Playwright screenshot and functional browser checks. Automated tests do not certify physical hardware or screen quality on actual devices.

## Edition policy and changes

Some repertoire arrangements and fingering do not establish exact score-edition provenance. Never relabel existing studies as certified source editions. Any future classical score import needs its own verified composer, edition, permissions, attribution and notation tests. Keep source-specific publication rights separate from the application MIT license. Do not fabricate score content or finger choices.

Keep the current app's navigation, score readability, fixed-center playhead, full-sheet view, tempo/hands controls, touch, MIDI/Bluetooth MIDI, microphone fallback, local progress and installability. Test UI changes visually on mobile and tablet.

## Publishing and owner approval

The production root site lives at `https://fischerjooo.github.io/Aria-piano/`. `pages.yml` builds, tests, increments `version.json` on a normal main release and deploys one Pages artifact. Beta preview at `/Aria-piano/beta/` is a separately branded preview of the same production player, not a second experimental engine. Its progress is namespaced and its PWA identity scoped. A separately installable Android beta still requires a different HTTPS origin; GitHub Pages `/beta/` may collide with the root PWA.

Use a `feature/*` or `fix/*` branch from `main` for substantial changes. CI must succeed on the exact SHA; a successful validated branch push can publish the fixed rolling beta through `.github/workflows/beta.yml` and update `beta-preview`. Verify the exact preview SHA and successful Pages deployment before calling a beta ready. **Do not merge a proposed feature until the owner explicitly approves it.** A directly requested minor change to main may follow the existing direct-main exception, with tests and successful Pages publication. Never let beta deploy over the production root. Preserve GitHub Actions release versioning and avoid version bump loops.

Application identity: Aria piano in production and Aria piano (beta) for the branded preview. `icons/aria.svg` is the sole master (A monogram, gold note and keyboard); icons for both channels must show identical artwork. `scripts/branding_icons.py` produces the PNG icons. Do not commit credentials, temporary test captures, caches or dependencies.
