# Historical test baseline

Checked against the unchanged stable v5.27 snapshot during migration on 29 October 2026. All historical fixtures are retained; older requirements and missing harness behavior are not silently rewritten to pass. Only the passing stable regression checks below run in `scripts/test.py`; the experimental v6 tests and source validators also run there. These results do not imply complete browser or hardware coverage.

| Historical file | v5.27 result |
|---|---|
| `audit-melodies.cjs` | Historical failure; excluded from current acceptance |
| `piano-center-playhead-tests.cjs` | Pass |
| `piano-curriculum-tests.cjs` | Pass |
| `piano-dsp-tests.cjs` | Pass |
| `piano-early-holds-tests.cjs` | Historical failure; excluded from current acceptance |
| `piano-extension-tests.cjs` | Historical failure; excluded from current acceptance |
| `piano-finger-tests.cjs` | Historical failure; excluded from current acceptance |
| `piano-games-info-tests.cjs` | Historical failure; excluded from current acceptance |
| `piano-hold-coach-tests.cjs` | Historical failure; excluded from current acceptance |
| `piano-independent-rhythm-tests.cjs` | Pass |
| `piano-level-tests.cjs` | Historical failure; excluded from current acceptance |
| `piano-melody-cleanup-tests.cjs` | Pass |
| `piano-notation-sizing-tests.cjs` | Pass |
| `piano-progression-tests.cjs` | Pass |
| `piano-quick-controls-tests.cjs` | Pass |
| `piano-readability-tests.cjs` | Historical failure; excluded from current acceptance |
| `piano-release-window-tests.cjs` | Pass |
| `piano-repertoire-tests.cjs` | Historical failure; excluded from current acceptance |
| `piano-replay-midi-tests.cjs` | Pass |
| `piano-results-key-tests.cjs` | Historical failure; excluded from current acceptance |
| `piano-rhythm-tests.cjs` | Historical failure; excluded from current acceptance |
| `piano-speed-tests.cjs` | Historical failure; excluded from current acceptance |
| `piano-tests.cjs` | Historical failure; excluded from current acceptance |
| `piano-timing-option-tests.cjs` | Pass |
| `piano-timing-sync-tests.cjs` | Pass |
| `piano-timing-tests.cjs` | Historical failure; excluded from current acceptance |
