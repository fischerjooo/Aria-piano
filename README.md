# Aria-piano

Piano teach web app with a self-contained HTML download, sheet music, local progress, touch, microphone, MIDI and Bluetooth input.

**Stable default: v5.26.** The root `index.html`, `dist/index.html` and `aria-piano-v5.26.html` preserve the established interface and features. The v6 source-first rewrite is experimental: it has useful score provenance and timing work, but it is not a feature-complete replacement for v5.26. Its separate downloadable file is `aria-piano-v6.0-candidate.html`; the Pages build also exposes `experimental/v6.html`.

Next development direction: bring the verified v6 score model and source-bound learning path into the polished v5 experience, preserving existing controls, notation readability, learning flow and input options. Compare both versions in a real browser before changing the stable default. The experimental rewrite must not silently replace the stable app.

## Local development

Requires Python 3.12+ and Node.js 22+. No package installation, third-party Python modules or npm dependencies are needed.

```sh
python scripts/build.py
python scripts/test.py
python -m http.server 8000
```

Open `http://localhost:8000/` for stable v5.26 or `http://localhost:8000/aria-piano-v6.0-candidate.html` for the experimental candidate. Microphone, Web MIDI and Web Bluetooth depend on browser support, secure contexts and user permission. Actual hardware testing is still required.

`build.py` deterministically rebuilds the two canonical v6 score JSON files from retained LilyPond and assembles the v6 download from `v6/template.html`, `input.js`, `player.js`, the scores and learning path. It copies v5.26 to both stable entrypoints and stages a minimal deployment in `_site/`. Only this deployment directory is published, rather than the development workspace or archived tests.

`test.py` runs source/publisher-MIDI comparisons, all 23 curriculum bindings, the six experimental v6 test files, 13 passing stable v5.26 regression files (including the 89-case core suite), and entrypoint consistency checks. It does not certify browser appearance or hardware compatibility.

All 24 original v5.26 test files from commit `612273319a4e70a1b9b7b10ff7e5b6fc8f736b76` are preserved byte-for-byte under `archive/tests-v5.26-original/`. Portable copies in `tests/` target the stable root, use the retained v3.1 DSP fixture and write optional diagnostics to ignored `test-results/`. Run `python scripts/test_snapshot.py` to execute every file; it reports 13 passing files and 11 known historical failures, then exits nonzero. See `tests/TEST-STATUS.md`. Assertions were not rewritten to make those historical tests pass.

Later v5.27 releases/tests remain in `archive/`; v6 source, research and checks remain under their original development directories. Neither later version replaces the stable v5.26 entrypoint.

## GitHub Pages

The workflow `.github/workflows/pages.yml` builds and validates on pushes to `main`, then deploys `_site/` with the official Pages artifact actions. Pull requests run validation through `ci.yml`. Neither workflow uses a personal access token.

One-time repository setup: open **Settings → Pages → Build and deployment → Source → GitHub Actions**. After enabling this source, push to `main` or manually run **Build and deploy Pages** from the Actions tab. The expected project URL is `https://fischerjooo.github.io/Aria-piano/`; it becomes available only after Pages is enabled and deployment succeeds. Repository or organization policy may require an administrator to enable Actions or approve the `github-pages` environment.

## Source and development map

- `v6/`: experimental score engine, input adapters, template, builder, tests and review notes.
- `src/repertoire/`: retained source editions, hashes, canonical timed scores, conversion and independent source/curriculum validation.
- `plans/`: repertoire requirements, research catalog, book targets, release scope, engine audit and QA gates.
- `archive/`: earlier HTML releases from v3.1 through v5.27, release notes and legacy tests. Their generated lesson content is historical and must not be confused with verified source editions.
- `AGENTS.md`: development continuity and acceptance requirements.

## Repertoire and licenses

The experimental candidate imports one complete published main-theme piano arrangement of Blue Danube (Mutopia 519), one complete soprano extraction from an Ode to Joy SATB setting (Mutopia 528), and 23 exact-source practice tasks. This is not the complete orchestral Blue Danube, an original piano Ode arrangement, a complete beginner course, or all 37 book targets.

The repository's existing MIT `LICENSE` is preserved for application code. Music editions and derived score data retain their own terms and attribution; the repository license does not override them. Blue Danube's arrangement and typesetting are © 2014 Nikos Kouremenos, based on Christian Mondrup / WIMA, Mutopia-2014/03/24-519, CC BY-SA 4.0; conversion changes representation, not musical notes. Ode to Joy's SATB setting is typeset by Peter Chubb, Mutopia-2009/08/05-528, Public Domain; the soprano is extracted unchanged. Source headers, per-score `license`, `licenseUrl`, `sourceAttribution`, `sourceUrl`, and `source-manifest.json` are retained. Other editions in the research catalog have individual terms; reference status does not establish embedding permission.
