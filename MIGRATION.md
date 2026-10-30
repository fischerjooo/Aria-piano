# Migration provenance

The stable app was migrated from the v5.26 snapshot at commit `612273319a4e70a1b9b7b10ff7e5b6fc8f736b76`. `aria-piano-v5.26.html` remains a frozen historical archive; the live `index.html` and `dist/index.html` are generated from current `src/app/`, `data/stable/`, and `version.json`.

| Retained material | Origin and destination |
|---|---|
| v5.26 tests | All 24 originals from commit `612273319a4e70a1b9b7b10ff7e5b6fc8f736b76` in `archive/tests-v5.26-original/`; portable copies in `tests/` change fixture/output paths only. |
| Later v5.27 app | Commit `335828fe2e2b5fcf687bc28fd8743a819766bd04`; retained in `aria-piano-v5.27.html` and `archive/`. |
| Historical releases and notes | Supplied standalone versions and release notes retained under `archive/releases/`. |
| Later tests | Supplied historical tests retained under `archive/tests/`; maintained portable tests are in `tests/`. |

The original v5.26 snapshot contained 13 passing and 11 outdated test cases. The current maintained 24 portable tests have been reconciled and all run under `scripts/test.py`; see `tests/TEST-STATUS.md`. Historical originals remain untouched. Only the production app and stable authoring inputs are part of the active build.

The existing remote MIT application license is preserved. Retained music sources keep their individual terms. Credentials, hosting identity/state, dependency caches and generated QA/deployment directories are excluded from migration.
