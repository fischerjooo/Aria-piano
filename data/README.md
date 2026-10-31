# Lesson and song packages

Aria's authored music is package-based. There are no central lesson/song catalogues, binding files, migration layers, or compatibility schemas.

`python scripts/build.py` discovers every package under `data/lessons/` and `data/songs/`, validates it, orders it from package attributes, and builds `index.html` plus `dist/index.html`.

## Structure

```text
data/
  lessons/
    meet-middle-c/
      lesson.yaml
      metadata.yaml
      notation.json
      performance.mid
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
      song.yaml
      metadata.yaml
      notation.json
      performance.mid
```

Each lesson is self-contained and has exactly three levels. Each song is self-contained in one folder.

## Ordering

Lesson order comes only from `lesson.yaml`:

```yaml
id: lesson-1
difficulty: 1
```

- `difficulty` must be an integer from **1 to 100**.
- Every lesson difficulty must be unique.
- Lower difficulty values appear first.
- Folder names do not affect ordering.
- Duplicate IDs or difficulty values are validation errors.

Song order comes only from `song.yaml`:

```yaml
id: repertoire-mary-had-a-little-lamb
libraryOrder: 2
gameOrder: 4
```

- `libraryOrder` must be a unique positive integer.
- `gameOrder` is optional and must be a unique positive integer when present.
- Folder names do not affect ordering.
- Duplicate IDs, `libraryOrder`, or `gameOrder` values are validation errors.

## Package files

`metadata.yaml` contains display and teaching metadata. Base lesson records must include their own `nav` label; the UI does not provide position-based or title fallbacks.

`notation.json` contains fingering, written beat values, timing metadata, and the local MIDI filename. MIDI must be named `performance.mid` and live in the same package folder.

`performance.mid` contains sounding pitches, onset timing, durations, and optional second-hand lane data. The builder validates MIDI and notation together and does not infer written fingering or notation from MIDI.

## Validate and build

```sh
python -m pip install -r requirements-build.txt
python scripts/catalogue.py validate
python scripts/build.py
python scripts/test.py
```

To inspect or edit one package MIDI:

```sh
python scripts/catalogue.py export-midi lesson-1 /tmp/lesson-1.mid
python scripts/catalogue.py import-midi lesson-1 /tmp/lesson-1.mid
python scripts/catalogue.py import-midi lesson-1 /tmp/lesson-1.mid --apply
```

MIDI import validates a temporary copy of the complete package library before applying the selected package change. `--apply` is required to write.

## Add, edit, remove

To add content, create one new lesson or song folder with all required local files and a unique stable ID plus ordering attribute.

To edit content, modify only that package.

To remove content, delete the package folder. Do not reuse IDs that may already exist in saved user progress.
