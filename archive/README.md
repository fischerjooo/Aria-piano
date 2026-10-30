# Historical Aria releases and tests

`index.html` is the preserved v5.27 test target. `releases/` retains the supplied standalone releases and release notes, including v3.1 used by the historical DSP comparison. These are historical snapshots, not the verified v6 source curriculum.

Legacy tests read their sibling archive index. Their machine-specific output paths have been changed to the operating-system temporary directory, and the DSP comparison uses `releases/aria-piano-v3.1.html`. Run an individual test with `node archive/tests/<name>.cjs`. Some tests capture requirements from earlier releases and may fail against v5.27; they are not included in the v6 acceptance suite. `audit-melodies.cjs` is an informational audit rather than an acceptance test.

Generated SVG/JSON diagnostics go to the OS temporary directory. Do not commit them or use archived generated lessons as evidence of source-faithful repertoire.
