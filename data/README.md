# Data authoring and deterministic builds

`python scripts/build.py` compiles the stable single-file application from these data files and `src/app/`. It never evaluates the old music generators. `aria-piano-v5.26.html` remains an immutable historical archive; `index.html` and `dist/index.html` are the data-driven build with the same interface, engine and materialized catalogue.

## Authored inputs

| Path | Authority and contents |
| --- | --- |
| `stable/midi/*.mid` | 346 Standard MIDI Files, one per distinct existing course level or melody. Canonical sounding pitches, onset spacing and key-contact durations. SMF format 0, PPQ 9600, primary lane channel 0 and simultaneous secondary lane channel 1, velocity 80, initial tempo and explicit end-of-track including final spacing. Primary lane can represent either hand; YAML hand descriptions define that distinction. |
| `stable/descriptions.yaml` | Existing titles, explanations, aims, hand and curriculum descriptions, tempo, display flags and historical provenance. No note arrays. |
| `stable/notation.json` | Written beat values and existing finger numbers, MIDI file references, lane/step mapping, final onset spacing, property-presence flags and bounded legacy sub-tick timing corrections. No duplicated pitch sequences or performance hold/step arrays. MIDI is not a notation format: fingerings and written values remain here. |
| `stable/bindings.json` | Ordered course, level and melody references, preserving progress IDs and all 68 × 3 course levels plus 142 melodies. |
| `experimental/learning-descriptions.yaml` | Text, goals and guides for the existing 23 source-bound tasks; path/stage/skill explanations and policies. These are tasks, not 23 compositions. |
| `experimental/learning-bindings.json` | Exact score IDs, source passages, prerequisites, scope, completion and evidence bindings for those tasks. |
| `experimental/score-descriptions.yaml` | Edition metadata, attribution, licenses and named source sections for the two verified imports. |
| `schemas/*.schema.json` | JSON Schema Draft 2020-12 contracts, enforced with the official pinned `jsonschema` validator, followed by semantic checks. |

No notes, fingerings, new arrangements or pedagogy were invented by this migration. The historical catalogue still contains generated variations and suggested fingerings with incomplete edition provenance. The migration does not promote them to authentic source scores or resolve the documented curriculum gaps. Existing attribution and license statements are preserved. The experimental imports retain their separate source rights.

The original publisher MIDI and LilyPond files remain unchanged under `src/repertoire/sources/`. Their independent fidelity checks remain part of the build checks. `src/repertoire/*.json` scores are generated full notation, including pitch spelling, measures, rests, ties and sections, from those retained editions. They are not interchangeable with the historical studies. `src/repertoire/learning-path.json` is generated from the experimental YAML/JSON inputs. Do not edit generated files as authoring inputs.

## Timing and exact compatibility

MIDI uses integer ticks. Most historical timing values fit PPQ 9600 exactly. A few old JavaScript values (for example `0.333333` and `0.31333301999999996`) cannot be represented exactly by any legal integer MIDI division. Explicit JSON corrections preserve those exact old runtime values after decoding the nearest MIDI tick. The compiler validates every correction against its corresponding tick and rejects corrections beyond half a tick. The maximum MIDI quantization is 1/19200 quarter beat, approximately 0.0521 ms at 60 BPM. MIDI alone does not claim exact retention of those old floating-point values.

Written note length, time to the next attack and physical key contact are separate. MIDI note-offs encode contact; the next onset and explicit spacing end encode pauses and trailing silence; JSON retains written values. No rest is filled with an invented note. The stable v5 engine supports step-aligned secondary notes of equal contact duration; imports reject staggered or unequal secondary notes. Such notation belongs to the separate experimental source model, which preserves those source constructs.

## Commands

Install the pinned build/validation dependencies once:

```sh
python -m pip install -r requirements-build.txt
python scripts/catalogue.py validate
python scripts/build.py
python scripts/test.py
```

Builds and validation run offline after dependency installation, from any working directory when passed absolute script paths. No npm packages or runtime network requests are required.

```sh
python scripts/catalogue.py export-midi lesson-1 /tmp/lesson-1.mid
python scripts/catalogue.py inspect-midi /tmp/lesson-1.mid
python scripts/catalogue.py import-midi lesson-1 /tmp/lesson-1.mid
python scripts/catalogue.py import-midi lesson-1 /tmp/lesson-1.mid --apply
```

Import validates a complete staged catalogue before writing; the default is a dry run. Identical MIDI is a byte-preserving no-op. Edited MIDI provides pitches, onsets, contact durations and tempo; import normalizes edited timing to its tick grid and clears migration-only corrections. Existing written beat values and finger numbers are retained. Supply `--written-values path/to/reviewed-values.json` with an explicit JSON beat array when the notation also changes; contact duration is never treated as evidence of a written note value. Imports require the existing step/lane counts, PPQ 9600, a single initial tempo and velocity 80; structural notation and fingering edits must be authored explicitly before importing a different shape.

After intentional changes, build and verify the app and its source attribution. The exact archive-parity checks are a migration regression gate: intentional later catalogue changes require a documented corresponding change to that gate, not silent regeneration of the archive.

`python scripts/migrate_stable_data.py` is the retained one-time migration utility. It reads the immutable archive through a read-only VM snapshot, materializes the historical data, and extracts the modular app sources. **Do not run it for routine editing:** it overwrites migrated authored inputs and app source with the historical snapshot. Build never invokes it.

Tests check every materialized property against the archive (204 course variants and 142 melodies), every MIDI performance round trip, unchanged import/dry-run/apply behavior, invalid schemas/references/fingerings/paths, duplicate YAML keys, malformed MIDI, repeated attacks, final silence and simultaneous lanes. Existing v5 and v6 suites remain active. This proves data/runtime parity, not real-device behavior or pedagogical quality.
