# Automated testing

The repository uses three complementary checks. All of the **supported release gates** must pass before publishing.

| Layer | Command | Validates |
| --- | --- | --- |
| Source and unit/integration regression | `python scripts/test.py` | PWA configuration, releases, BLE reconnection, source/curriculum fidelity, MIDI data conversion, timing, progression, rendering and selected stable runtime scenarios |
| Browser navigation and screenshot smoke | `node e2e/capture.cjs` | Tablet and phone navigation through 16 UI states each; release mode `--capture` regenerates screenshots |
| Browser behavioral flows | `node e2e/flows.cjs` | Course filters, melody searching/filtering, opening and closing controls, focus persistence over reload, sheet navigation and return home |

Use `python scripts/build.py` first, and install pinned Chromium tooling as in `.github/workflows/ci.yml` before browser tests. CI runs all three layers on branches and pull requests. `.github/workflows/pages.yml` runs them before a stable release.

## Historical snapshot — preserved but not part of the supported release suite

`python scripts/test_snapshot.py` runs the original 24 v5.26 test files against today's application. Eleven files contain legacy assumptions (catalogue sizes, old indices, UI dimensions and timing expectations), and **currently fail**. See [TEST-STATUS.md](../tests/TEST-STATUS.md). The original source files under `archive/tests-v5.26-original/` remain byte-identical.

These failures must **not** be relabelled as passing, silently skipped in the snapshot runner, or resolved by deleting assertions. Reconcile each legacy expectation with the current application contract, migrate meaningful checks into supported regression tests, and only then retire redundant legacy cases.

## Remaining hardware and flow coverage

The Playwright tests exercise the app in Chromium, not a real connected piano. The next priority is full lesson completion with simulated MIDI/touch, wrong-note and timing scenarios, settings changes during practice, and results/progress reloads. Real Bluetooth, Web MIDI hardware and microphone permission/pitch behavior also require device testing. Browser navigation checks do not substitute for those tests.
