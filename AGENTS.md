# Aria development continuity

Stable application: data-driven `index.html` and `dist/index.html`, compiled from `src/app/` and `data/` with exact v5.26 runtime catalogue parity. `aria-piano-v5.26.html` is an immutable historical archive. Preserve its established interface and features. v6 is an experimental score-model rewrite, not an accepted UI replacement. Never promote v6 merely because its automated tests pass.

Development direction: integrate verified source notation, source-bound curriculum and improved timing/input semantics into the polished v5 experience. Preserve touch/microphone/MIDI/BLE input, progress, readable full-sheet/center-playhead views, quick controls and responsive learning flow. Compare before and after visually and interactively in a real browser. The current v6 candidate has acknowledged UI/feature regressions against the established v5 interface.

## Build and verify

Use Python 3.12+ and Node.js 22+, with the pinned build-only Python dependencies:

```
python -m pip install -r requirements-build.txt
python scripts/build.py
python scripts/test.py
```

Run these from any directory by passing absolute script paths if needed. Build and commit the generated `index.html`, `dist/index.html`, v6 candidate and canonical score JSON when their source changes. `_site/` is disposable and ignored. Pages stages the data-driven stable build as its root and experimental v6 separately. See `data/README.md` for canonical MIDI/YAML/JSON authoring boundaries and import/export. Never run the one-time migration utility during normal builds or silently regenerate the immutable archive. MIDI cannot express a few old fractional values exactly; retain bounded JSON correction metadata until an intentional timing change is reviewed. CI must not silently update the default to the candidate.

Current v6 checks cover hashes, independent publisher MIDI comparison, source-pitch spelling, ties, scope/part/bar bindings, curriculum claims, engine attacks, input simulations, practice state and controlled-clock timing. They do not replace real-browser visual QA or real hardware tests. The full v5.26 test snapshot is in `tests/`, with byte-identical originals in `archive/tests-v5.26-original/`. CI runs the 13 passing baseline files; `python scripts/test_snapshot.py` runs all 24 and intentionally reports the 11 known historical failures documented in `tests/TEST-STATUS.md`. Preserve assertions and report failures honestly. Later historical tests remain under `archive/tests/`.

## Score and curriculum requirements

Read `plans/repertoire-rebuild-plan.md`, `plans/source-catalog/release-scope.md`, `plans/source-catalog/qa-checklist.md` and `v6/REVIEW-NOTES.md` before changing repertoire. Every playable note must trace to an identified edition. Do not invent filler, simplifications, padded repeats or fingering. Keep original files, hashes, attribution and license terms. Preserve the score sources byte-for-byte unless a deliberate documented source update is made; validate against publisher MIDI independently.

Only Mutopia 519's complete main-theme piano arrangement and Mutopia 528's unchanged soprano extraction have verified playable conversion. There are 23 source-bound practice tasks, not 23 compositions. The remaining research catalog and 37 book targets are not playable counts; no source is established as matching Mauro Costa's book. Keep ambiguous targets unresolved. G Major Music Theory reference arrangements have no established embedding permission.

Current v6 limitations: basic score engraving (flagged eighths, limited collision handling), no source beams/full expression evaluation, no posture/technique/fingering grading, monophonic E2–C6 microphone input without physical release assessment, new source-progress storage that does not migrate old generated-lesson completion. Real MIDI/Bluetooth/microphone hardware and browser permission behavior remain unverified. There is a documented learning gap before Blue Danube coordination/dyads; do not hide it with fabricated content.

## Workflow and publication

Published app versions are generated from `version.json` by `scripts/build.py`, not from hardcoded labels. PR and non-main branch validation must not increment versions. The `pages.yml` workflow increments the minor release on normal main publishes or accepts an explicit manual major choice that resets the minor number to zero; it rebuilds, tests, commits `version.json` plus generated `index.html`/`dist/index.html`, and then deploys that tested artifact. The workflow uses a bot-generated `GITHUB_TOKEN` commit to avoid a second push-triggered release; protect against version/publish loops. Keep frozen v5.26 historical archive untouched and do not mistake the release number for changes to the historical content.

All development source, plans and checks belong in this repository. Exclude credentials, `.openai` identity/configuration, local caches, dependencies and temporary QA outputs. Keep deployments limited to `_site/`. Maintain the existing application MIT license and each source edition's own license/attribution. Do not relabel all bundled music MIT.

Use `.github/workflows/ci.yml` for every non-main branch push and PR validation, and `pages.yml` for tested main-branch Pages deployment (both merges and direct pushes). Failed builds, selected tests or generated-file checks must block publication. Manual publication is restricted to main. The repository owner must initially enable Settings → Pages → GitHub Actions. Do not claim Pages is live until a deployment succeeds.
