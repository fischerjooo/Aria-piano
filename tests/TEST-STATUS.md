# Maintained stable regression suite — 30 October 2026

**Current status: 24/24 maintained portable regression files pass in GitHub Actions.** `python scripts/test_snapshot.py` runs them all; `python scripts/test.py` invokes that runner in addition to stable app, MIDI, version, data, PWA, BLE and build-isolation checks. The former 13-file allowlist was removed.

All 11 previously failing portable regressions were reconciled with the actual stable application contract: 68 courses / 204 levels, 142 melodies, present lesson indices, current responsive sizing, release windows and score animation. No file was deleted or hidden. The 24 byte-identical **historical originals** remain under `archive/tests-v5.26-original/`, separate from the maintained portable tests.

| Maintained test file | Status | Coverage |
| --- | --- | --- |
| `piano-center-playhead-tests.cjs` | Pass | Score centering / timing |
| `piano-curriculum-tests.cjs` | Pass | Course structure and progression |
| `piano-dsp-tests.cjs` | Pass | Microphone DSP fixtures |
| `piano-early-holds-tests.cjs` | Pass | Early technique / short holds |
| `piano-extension-tests.cjs` | Pass — reconciled | All-catalogue rendering, BLE, navigation |
| `piano-finger-tests.cjs` | Pass — reconciled | Melody fingering and active key hints |
| `piano-games-info-tests.cjs` | Pass — reconciled | Game arrangements and lesson guides |
| `piano-hold-coach-tests.cjs` | Pass — reconciled | Early/late release, feedback and diagrams |
| `piano-independent-rhythm-tests.cjs` | Pass | Timing independent of pitch |
| `piano-level-tests.cjs` | Pass — reconciled | All 204 lesson levels, completion |
| `piano-melody-cleanup-tests.cjs` | Pass | Melody lifecycle cleanup |
| `piano-notation-sizing-tests.cjs` | Pass | Score layout bounds |
| `piano-quick-controls-tests.cjs` | Pass | Practice controls |
| `piano-readability-tests.cjs` | Pass — reconciled | Responsive budgets and narrow long scores |
| `piano-release-window-tests.cjs` | Pass | MIDI note-release timing |
| `piano-repertoire-tests.cjs` | Pass — reconciled | 142 melodies and two-hand input |
| `piano-replay-midi-tests.cjs` | Pass | Replay and MIDI hold handling |
| `piano-results-key-tests.cjs` | Pass — reconciled | Results keyboard navigation |
| `piano-rhythm-tests.cjs` | Pass — reconciled | Rhythm data, onset grid and score motion |
| `piano-speed-tests.cjs` | Pass — reconciled | Melody BPM presets and persistence |
| `piano-tests.cjs` | Pass | Core player state and rendering |
| `piano-timing-option-tests.cjs` | Pass | Timing preference and disable behavior |
| `piano-timing-sync-tests.cjs` | Pass | Score/timing synchronization |
| `piano-timing-tests.cjs` | Pass — reconciled | Velocity and timing penalties |

The archived v5.26 originals are **historical fixtures**, not tests guaranteed to pass unchanged against new app versions. CI also runs the Playwright tablet/mobile screenshot smoke tests and the functional navigation/persistence suite. Physical MIDI, BLE, and microphone hardware remain outside automated browser coverage.
