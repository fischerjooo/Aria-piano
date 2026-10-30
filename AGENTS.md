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

Chrome for Android has a known same-origin multi-PWA installation regression. Do not claim the GitHub Pages /beta/ path alone can install independently of stable on Android. For the separate Android beta, use a different HTTPS hostname with a fixed production project tracking the validated beta-preview branch, and run scripts/beta_preview.py with --install-base / to give the PWA a root-scoped identity. Keep the existing /beta/ path as a browser preview. The Vercel config supports optional independent hosting; deployment requires connecting/configuring the Vercel project and confirming its URL, and must not be represented as live before that setup.

Every non-main development-branch push must pass the existing Validate workflow before a trusted workflow_run builds and publishes the latest validated branch as the rolling beta at `/Aria-piano/beta/`. Never publish PR/fork artifacts as beta, never increment version.json on beta, and never allow a beta deployment to replace root production. Use one Pages artifact with root stable and nested /beta/. Save the validated source commit in the managed beta-preview ref so later normal main releases can preserve that beta URL. Both deployment workflows must share the pages concurrency group. Display a next-minor beta version suffix including the tested commit hash, scope PWA service workers and manifest paths to /beta/, and namespace beta localStorage to avoid mixing progress with stable. Failed beta builds must leave the previously published preview untouched.

Published app versions are generated from `version.json` by `scripts/build.py`, not from hardcoded labels. PR and non-main branch validation must not increment versions. The `pages.yml` workflow increments the minor release on normal main publishes or accepts an explicit manual major choice that resets the minor number to zero; it rebuilds, tests, commits `version.json` plus generated `index.html`/`dist/index.html`, and then deploys that tested artifact. The workflow uses a bot-generated `GITHUB_TOKEN` commit to avoid a second push-triggered release; protect against version/publish loops. Keep frozen v5.26 historical archive untouched and do not mistake the release number for changes to the historical content.

All development source, plans and checks belong in this repository. Exclude credentials, `.openai` identity/configuration, local caches, dependencies and temporary QA outputs. Keep deployments limited to `_site/`. Maintain the existing application MIT license and each source edition's own license/attribution. Do not relabel all bundled music MIT.

Use `.github/workflows/ci.yml` for every non-main branch push and PR validation, and `pages.yml` for tested main-branch Pages deployment (both merges and direct pushes). Failed builds, selected tests or generated-file checks must block publication. Manual publication is restricted to main. The repository owner must initially enable Settings → Pages → GitHub Actions. Do not claim Pages is live until a deployment succeeds.

## Required feature development and owner approval

Repository: `fischerjooo/Aria-piano`. In new sessions inspect this repo and this file first. Do not claim account authorization is permanent: GitHub app permissions and confirmation prompts are managed by ChatGPT and the GitHub integration, not by this repository.

**Feature requests:** Create a new `feature/*` or `fix/*` branch from `main` by default, implement in the branch, run `python scripts/build.py` and `python scripts/test.py`, and wait for the push-triggered Validate workflow to pass. The validated development commit is published to the rolling `/Aria-piano/beta/` preview by the beta workflow. Offer the user the beta URL for hands-on testing. **Do not merge a new feature into main before the user explicitly reviews and approves it**, even if CI passes. PR approval must be user approval, not merely a green CI status. When the user asks to merge an already tested feature or explicitly approves merging, merge the validated PR.

**Exception for direct main:** If the user explicitly requests a minor fix or change to go straight into `main`, it is permitted to commit/push directly to main without beta review. Run relevant checks and preserve the automatic release/versioning workflow, and make sure production still deploys. Do not infer this exception from routine wording.

**Release flow:** feature branch → source and generated outputs → Validate CI → publish fixed beta preview → user tests/reviews → explicit approval → merge → normal main minor release and Pages deployment. Major releases are opt-in through the existing manual workflow. Do not alter historical v5.26 archives; source of truth for app version is version.json. Do not confuse GitHub Pages beta browser preview with a separately installable Android PWA on a distinct hostname.

**Brand identity:** Production is named `Aria piano` and beta is named `Aria piano (beta)`. Homepage logo is the A monogram followed directly by `ria piano`, i.e. the icon supplies the letter A. The icon uses a broad single-letter form legible at small sizes, not micro-details. Generate launcher icons for both channels with `scripts/branding_icons.py` during the normal build.
