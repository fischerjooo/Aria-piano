# Automated testing

Every supported regression check and browser flow runs in GitHub Actions before live publishing. No historical tests are excluded from the regular release gate.

| Layer | Command | Validates |
| --- | --- | --- |
| Source, unit and integration regressions | `python scripts/test.py` | Source/curriculum validation, MIDI import/export and negative cases, version/PWA/beta configuration, BLE recovery, experimental engine tests, and **all 24 maintained stable regression files** |
| Stable regression files, standalone | `python scripts/test_snapshot.py` | Runs all 24 maintained `tests/*-tests.cjs` cases and exits nonzero if any fail; already included in `test.py` |
| Responsive browser smoke and gallery | `node e2e/capture.cjs` | Phone and tablet screen navigation; `--capture` generates the release screenshot gallery |
| Behavioral Playwright flows | `node e2e/flows.cjs` | Filters and search, lesson selection, menus, persisted focus preference across reload, sheet navigation and returning to the correct collection |

Run `python scripts/build.py` before the tests. Install the pinned browser package and Chromium as configured in `.github/workflows/ci.yml` before running Playwright. Validation on PRs and branches and release verification both use the same supported regression and browser checks.

## Historical regression reconciliation

The 24 portable files in `tests/` have been updated to the current 68-course / 142-melody stable application and **passed 24/24 in GitHub Actions on 30 October 2026**. The 11 previously failing or excluded files were repaired, retained and included in the mandatory test runner. See [the current status](../tests/TEST-STATUS.md) and [file-by-file reconciliation](HISTORICAL-TEST-AUDIT.md).

The original v5.26 snapshot under `archive/tests-v5.26-original/` remains untouched as historical evidence. It is **not** the maintained regression suite; its original assumptions need not match the current app. No portable files were deleted and none is skipped by the supported regression runner.

## Remaining hardware and interaction limits

These green tests validate simulated inputs and app logic, not real USB MIDI, Bluetooth MIDI pairing or physical microphone acoustics. Full touch/MIDI song completion in a real browser, progress/results persistence after full sessions, and true visual baseline diffing would further strengthen coverage. Browser screenshots show rendering rather than guaranteeing physical-device behavior.
