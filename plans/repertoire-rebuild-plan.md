# Aria: source-first classical piano rebuild

Status: implementation brief, 29 October 2026. Owner: Astra (direction and spot checks). Sol/Terra/Luna own implementation, source preparation and independent review. This replaces the v5 generated curriculum approach; it is not a promise that all 37 book arrangements have been obtained.

## Outcome and boundaries

Teach the user to read and perform real, pre-existing simplified classical piano scores, progressing toward works in the supplied 37-piece contents image, particularly Strauss II's Blue Danube, Op.314. Every playable note must come from an identified score edition. No composed filler, algorithmic pitch routes, automatic simplification, padded repeats, guessed fingering, or difficulty variants manufactured from one melody.

The book is a repertoire target, not a score source: a contents image and Amazon description do not identify its actual notation, fingering or arrangements. Do not claim a source matches Mauro Costa's edition without comparing the supplied score. Some contents entries are ambiguous or name multi-movement works; retain that uncertainty.

Retain the single downloadable HTML, local progress, MIDI/BLE, mic and touch input, fixed-center playhead, full-page readable sheet, quick tempo/hands menus and responsive tablet/phone controls. Authentic source rhythm takes precedence over old timing/array shortcuts.

## Source policy and catalog

Each work contains only individually verified variants. A variant records composer/work identity, original instrumentation, edition title, arranger/editor, score URL and original file, file checksum, per-edition reuse license, scope, key/meter, source fingering availability, exact notation and source bar numbering. Difficulty is assessed from the actual variant, not inferred from a filename or fabricated to populate a menu.

Simple / Intermediate / Expert buttons appear only for different real arrangements. Original is a provenance badge on the matching piano variant, not a duplicate choice. An orchestral/choral original must not be presented as an original solo-piano score. Never add harder embellished versions beyond the original. One available version is shown without a redundant selector.

Use Mutopia per-file PD/CC editions and appropriate historical PD sources as first imports. IMSLP is useful for edition verification and historical scans; verify each specific score. G Major Music Theory has genuine graded beginner arrangements but its current terms require permission for embedding/redistribution: link them as references until authorized. Treat MuseScore/PDMX/OpenScore records as candidates requiring per-score provenance, license and musical checks, not as automatically cleared or correct.

Status values: candidate, source verified, import verified, playable, reference only, ambiguous. Only playable entries enter training. Catalog counts must separate playable variants from future target works.

## Curriculum: work backward from the actual score

No arbitrary target lesson count. Each lesson has one observable playing/reading aim, precise variant/voice/bar range, its prerequisite skills, explanation of the source notation, optional sourced finger hints, and a clean transition to the next passage. A one-hand or smaller-range practice mode is not a newly invented simpler arrangement.

1. First reading: staff direction, repeated notes, steps, first rhythm values, releases. Exact short monophonic phrases, not generated C-position drills. Mutopia528 soprano line can serve as explicitly labelled melody-reading material; it is not a beginner piano arrangement of the symphony.
2. Phrase reading: longer source phrases, rests, repeated and contrasting endings; connect the same phrases into the whole available melody line.
3. Bass reading and coordination: exact left-hand passages from a verified piano edition; isolated hands first, then actual simultaneous and staggered entries. Do not substitute octave doubling.
4. Three-beat pulse and chord shapes: prepare the actual bass/chord waltz figure and right-hand thirds in the sourced Blue Danube arrangement.
5. Moving positions and held notes: source-defined register changes, chords, unequal hand durations, accidentals and dotted figures. Include the exact corresponding measures before asking for the complete section.
6. Section assembly: join source-aligned sections of Blue Danube, retaining pickup, written rests and final cadence. This is the complete published main-theme arrangement, not the complete Op.314 orchestral waltz.
7. Transfer to another verified classic: assess the next edition's new demands, such as independent lines in a Minuet or sustained melody over accompaniment. Source acquisition gates this stage; do not fill it with invented material.
8. Longer-term repertoire: more book targets and easier editions as they become verified. Gymnopedie, Fur Elise and Clair de lune originals may be catalogued without presenting them as first-week material.

Sol's detailed curriculum plan supplies source-specific bindings. No lesson may be marked ready while its claimed passage/skill does not exist in the source.

## Section and navigation flow

On a work page: choose an available edition, then Whole available score or a predefined named section with source bar range. On entering, practice listens immediately once the chosen input is ready.

Bottom controls place Previous, Replay, Next together. For lessons, move through real lesson passages, crossing a lesson boundary explicitly. For a selected melody section, move between sections without wrapping. In whole mode, keep navigation labels explicit rather than silently skipping notes. Disable a nonexistent previous/next target.

Section results offer Replay section, Next section and Play all sections. Finishing the last section offers a whole-score run. Completing individual sections does not automatically mark the whole piece as performed. Store section/whole, variant, hand and input progress separately. MIDI result shortcuts must target the same scoped actions as buttons. Reset held keys, scheduled audio, timers and attack tracking on every scope change.

## Required engine change

### Longer melodies and lesson examples — user requirement, 29 October 2026

Prefer complete, existing online piano arrangements over tiny tune fragments. Where a complete edition is not yet supported, expose a musically complete source passage with an explicit excerpt label and exact bar range; do not imply that it is the whole piece. Preserve the source's phrases, accompaniment, rests and written repeats. Never manufacture length through generated continuation, arbitrary looping or pasted unrelated phrases.

Use short source excerpts only to isolate a new skill. Build the next lesson stage into a longer coherent phrase or section, and the demonstration stage into the longest pedagogically suitable complete source section. Length must follow the actual score and the learner's prerequisites, not a fixed note-count quota.

Each longer arrangement must offer named source-aligned sections, individual section replay and progression, and Play all for the complete available arrangement. Show the available bar count and approximate duration at the selected tempo before practice. Keep notation readable through scrolling in practice and multiple systems/pages in full-sheet view; never shrink an entire long score into one screen.

Before importing additional long examples, verify the exact online edition, redistribution terms, source file and fidelity of the conversion. Prioritize the requested classical repertoire. Do not label a longer work playable until all its measures and section boundaries pass source and player validation.

Replace shared seq/left arrays with a measure-aware integer-tick notation model and separate performance timeline. Preserve rests, note spelling, key/time signatures, voices, chords, source durations, independent hands, pickup and tie semantics. Repeated notes need new attacks; tied continuations do not. Sustained bass must not be re-struck for each right-hand note. Rendering and playback derive from the same source model.

Use an explicit supported-notation validator. Reject unsupported source constructs instead of silently dropping them. Do not expose a score as playable until its import, renderer and event matcher support its content. Mic stays monophonic: restrict to an appropriate hand/voice; never pretend to grade chords through the existing pitch detector. Timing feedback must describe precisely what is measured; no posture/fingering quality claims.

## Work ownership

- Sol source lead: exact edition catalog, retained source files/hashes, faithful import and independent source comparison.
- Sol curriculum lead: repertoire-to-skill graph, exact passage boundaries, explanations and difficulty/source review.
- Terra engineering lead: event model, notation/playback/input integration, scope-aware progress and UI; tests and single-file packaging.
- Luna catalog/review: 37-item identification, ambiguous works, provenance/labels/count checks; independent validation and regression review.
- Astra: decisions, consolidated plan, spot checks, resolve gaps, release assessment. No root-written production music or implementation.

## Delivery order and release gates

A. Finish and retain plan, target catalog, source inventory and engine audit before production implementation.
B. Implement one complete verified vertical slice using Mutopia519 Blue Danube, not a generic fake fixture. Add source-exact beginner reading material and other piano scores only when validated.
C. Verify pitch, duration, rests, hands, chords, pickup/ties/repeats (if present), source fingerings and every section boundary. Confirm no arbitrary key-to-finger mapping remains.
D. Test repeated attacks, held bass, chord order, all note-off paths, early/late logic, pause/resume, whole vs section completion, previous/next boundaries, replay, input changes, static-sheet coverage, fixed bar alignment and layout sizes. Mock tests do not establish hardware correctness.
E. Preserve old local progress separately; never award mastery of a different sourced edition from legacy generated-exercise completion. Keep the prior downloadable v5.27 as an archive, not as source evidence.
F. Publish only the verified scope. Expose a readable source/credits record and honest missing-variant status. A future target or reference-only arrangement is not a playable lesson. If authentic rendering or source fidelity is not ready, deliver the plan/catalog and tested foundation without silently replacing the live app with an incomplete rebuild.

## Current verified anchor

Mutopia519: Johann Strauss II, The Blue Danube Waltz (main theme), Op.314, piano arrangement by N. Kouremenos; CC BY-SA4.0. Source comments identify C-major simplification of the main theme. Source bar1 is the one-beat pickup, followed by full bars2–34: 100 quarter-beats. This is a real pre-existing piano arrangement, not the entire orchestral work. Exact source: https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=519

The catalog may add further anchors only after matching real score assets, instrumentation and licenses. G Major Music Theory's print/teaching permission does not authorize copying its arrangements into Aria.
