# v5.26 test snapshot baseline

Verified 30 October 2026 against the byte-identical v5.26 app from commit `612273319a4e70a1b9b7b10ff7e5b6fc8f736b76`. All 24 test originals are retained in `archive/tests-v5.26-original/`. Portable copies change only DSP fixture and diagnostic paths; assertions remain unchanged. The core suite passes all 89 cases.

`python scripts/test.py` runs 13 passing stable files plus experimental v6 checks. `python scripts/test_snapshot.py` runs all 24 files and exits nonzero: 13 pass, 11 fail. These existing failures remain unresolved; migration does not claim full regression acceptance. The table records each failing file’s first observed assertion, not an exhaustive diagnosis. Browser and physical input checks remain necessary.

| Test file | Result | First observed reason |
|---|---|---|
| `piano-center-playhead-tests.cjs` | Pass | — |
| `piano-curriculum-tests.cjs` | Pass | — |
| `piano-dsp-tests.cjs` | Pass | — |
| `piano-early-holds-tests.cjs` | Pass | — |
| `piano-extension-tests.cjs` | Known failure | Expected 36 exercises; v5.26 has 68. |
| `piano-finger-tests.cjs` | Known failure | Expected body melody-fingers class is absent for the older selected lesson index. |
| `piano-games-info-tests.cjs` | Known failure | Expected 130 melodies; v5.26 has 142. |
| `piano-hold-coach-tests.cjs` | Known failure | Expected hold phase; current timing state is release. |
| `piano-independent-rhythm-tests.cjs` | Pass | — |
| `piano-level-tests.cjs` | Known failure | Expected 36 exercises; v5.26 has 68. |
| `piano-melody-cleanup-tests.cjs` | Pass | — |
| `piano-notation-sizing-tests.cjs` | Pass | — |
| `piano-quick-controls-tests.cjs` | Pass | — |
| `piano-readability-tests.cjs` | Known failure | Expected 132px dock; current compact dock is 64px. |
| `piano-release-window-tests.cjs` | Pass | — |
| `piano-repertoire-tests.cjs` | Known failure | Expected 130 melodies; v5.26 has 142. |
| `piano-replay-midi-tests.cjs` | Pass | — |
| `piano-results-key-tests.cjs` | Known failure | Old melody index 36 remains exercise 36; expected next index 37. |
| `piano-rhythm-tests.cjs` | Known failure | Expected 75 quarter-note melody entries; current count is 87. |
| `piano-speed-tests.cjs` | Known failure | Old melody range starts at exercise 36; speed control remains hidden for exercises. |
| `piano-tests.cjs` | Pass | — |
| `piano-timing-option-tests.cjs` | Pass | — |
| `piano-timing-sync-tests.cjs` | Pass | — |
| `piano-timing-tests.cjs` | Known failure | Expected one mistake; current early-release/velocity state records two. |
