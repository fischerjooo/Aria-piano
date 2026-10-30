# Migration provenance

The stable default is v5.26 from commit `612273319a4e70a1b9b7b10ff7e5b6fc8f736b76`. `aria-piano-v5.26.html`, `index.html`, and `dist/index.html` are byte-identical to that commit’s app. Build and Pages retain this default.

| Retained material | Origin and destination |
|---|---|
| v5.26 tests | All 24 originals from commit `612273319a4e70a1b9b7b10ff7e5b6fc8f736b76` in `archive/tests-v5.26-original/`; portable copies in `tests/` change fixture/output paths only. |
| Later v5.27 app | Commit `335828fe2e2b5fcf687bc28fd8743a819766bd04`; retained in `aria-piano-v5.27.html` and `archive/`. |
| Experimental v6 candidate | Introduced in commit `7f8e1efa34a050377686a9f625a24e06b2de8016`; latest source workspace at commit `5b050b06246f4abd6f8764ea702909b60421d556`, retained under `v6/`, `src/`, and the separate candidate HTML. |
| Historical releases and notes | Supplied standalone versions and release notes retained under `archive/releases/`. |
| Later tests and research | Supplied later tests retained under `archive/tests/`; repertoire plans, catalog, source editions and validators retained under `plans/` and `src/repertoire/`. |

The complete v5.26 snapshot has 13 passing test files and 11 existing failures; see `tests/TEST-STATUS.md`. CI runs the passing stable baseline and experimental v6/source checks. `python scripts/test_snapshot.py` executes all 24 and returns nonzero for unresolved historical failures. No test assertions were changed to hide these failures.

The existing remote MIT application license is preserved. Retained music sources keep their individual terms. Credentials, hosting identity/state, dependency caches and generated QA/deployment directories are excluded from migration.
