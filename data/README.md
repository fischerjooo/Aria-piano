# Editable lesson and song packages

Aria's library is **folder-based**. There are no central song/lesson JSON, YAML or MIDI catalogues.
`python scripts/build.py` discovers packages, validates them and compiles the one stable player
(`index.html` and `dist/index.html`). Source data is entirely within each item folder.

## On-disk structure

```text
data/
  lessons/
    meet-middle-c/
      lesson.yaml                 # immutable id; difficulty: 1..100
      metadata.yaml               # title, instructions, finger guidance, source, tempo
      notation.json               # written beats, finger numbers and MIDI timing corrections
      performance.mid             # actual sounding pitches and timings
      levels/
        2/
          metadata.yaml
          notation.json
          performance.mid
        3/
          metadata.yaml
          notation.json
          performance.mid
  songs/
    mary-had-a-little-lamb/
      song.yaml                   # id, libraryOrder, optional gameOrder
      metadata.yaml
      notation.json
      performance.mid
  provenance.yaml                 # frozen archive provenance only, not a catalogue
  schemas/                        # validation contracts, not lesson data
```

**68 lessons** each contain three independent level records; **142 songs** are individually
editable. All **346** canonical MIDI files are byte-for-byte the same as before the migration.
No alternative score engine or second song database is created.

### Adding, editing and removing items

- **Lesson:** copy one folder under `data/lessons/`; give it a unique stable `id` in
  `lesson.yaml` (the readable folder name can change without changing this ID) and its level-1 `metadata.yaml`. Provide all three level folders/files and
  different record IDs for each variant. Choose `difficulty` between **1 (easiest)** and
  **100 (hardest)**. The builder discovers it automatically and sorts lessons by difficulty,
  then by ID for deterministic ties; no central binding or course-index list to update.
- **Song:** copy one folder under `data/songs/`, provide `song.yaml` with a unique stable `id` independent of the folder name
  and a positive `libraryOrder` (tie-breaking is alphabetical), and put YAML, JSON and
  `performance.mid` alongside it. To include a game song in the game-library picker,
  additionally assign `gameOrder`. The builder discovers every song folder automatically.
- **Edit:** change only the desired item's metadata, notation or MIDI; unrelated items
  are not rewritten. Run `python scripts/catalogue.py validate` before committing.
- **Remove:** delete the entire item folder. Never recycle IDs used by released records:
  users' locally saved progress keys depend on those IDs. Folder names may change independently. Migration preserves all
  existing lesson/song IDs and their original order via the 1..100 difficulty and
  `libraryOrder` values.

Metadata holds lesson instructions, attribution, hand, level and display flags. Notation
holds fingerings, written beat values, timing-correction flags and references only its local
`performance.mid`. MIDI holds exact sounding pitches, onsets and key-contact durations;
the builder never guesses fingers or written notation from a MIDI performance.
`data/provenance.yaml` retains the original frozen archive hash, without storing
duplicated per-item records. Original repertoire studies have historical/generated
arrangements; this migration does not assert certified score-edition provenance.

## Build and import

```sh
python -m pip install -r requirements-build.txt
python scripts/catalogue.py validate
python scripts/build.py
python scripts/test.py

python scripts/catalogue.py export-midi lesson-1 /tmp/lesson-1.mid
python scripts/catalogue.py import-midi lesson-1 /tmp/lesson-1.mid
python scripts/catalogue.py import-midi lesson-1 /tmp/lesson-1.mid --apply
```

An import validates a temporary copy of the whole package library before replacing
the selected item's MIDI, notation and metadata. `--apply` is required to write.
Use `--written-values path/to/values.json` only when supplying independently reviewed
written beat values. Preserve the existing PPQ 9600 MIDI format and two-lane boundary:
staggered/unequal secondary parts are unsupported by the current stable engine.

The one-off `scripts/migrate_stable_data.py` is **historical** and must never be rerun:
it generates the removed central legacy files from a frozen snapshot.
Keep the `aria-piano-v5.26.html` archive unchanged. Built catalogue parity is checked
against that archive before accepting migrations, but legitimate future repertoire
changes must update the expected parity test explicitly rather than silently rewriting
the archive. The GitHub Actions checks include full regressions and responsive browser tests.
