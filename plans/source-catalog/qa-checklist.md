# Independent QA checklist for the source-first rebuild

Use this checklist against each commit/candidate. Static data validation does not prove that notation matches the score; manually compare the playable rendering and performance against the retained source edition.

## Catalog and rights

- [ ] Target works (37 book contents) are separate from sourced score variants and from playable variant count.
- [ ] Each variant names the exact score/edition, composer, instrumentation, arranger/editor, URL, source file/hash, reuse license, scope, key/meter and fingering provenance.
- [ ] Mutopia records point to the exact licensed score/file; a Mutopia homepage URL is insufficient evidence.
- [ ] G Major Music Theory records remain external-link-only until embedding permission is recorded.
- [ ] No orchestral/choral source is labeled as an original solo-piano score. Mutopia528 is a soprano reading line from an SATB setting; Mutopia519 is the published piano arrangement of the main theme, not all of Op. 314.
- [ ] “Original” is a provenance label for the matching piano variant. It does not appear as a selectable duplicate or turn an orchestral work into a piano arrangement.
- [ ] Simple/Intermediate/Expert selectors appear only when separately sourced, musically verified variants exist. One variant has no redundant selector.
- [ ] A piece marked playable has passed import, notation-rendering and event-matcher support checks; candidate/reference-only/ambiguous records cannot enter practice.
- [ ] Catalog UI and copy distinguish complete available score/arrangement, excerpt, movement, and complete original work. “Whole” means the whole available variant unless it is explicitly the whole named original work.

## Score model and unsupported notation

- [ ] All event positions and durations are integer ticks, with one declared ticks-per-quarter value; no float-beat timing shortcuts.
- [ ] Every measure has the correct source duration, including pickup convention; source bar numbers remain mapped to visible/UI numbering.
- [ ] Notes preserve MIDI pitch, diatonic spelling, alteration and octave. Chords are simultaneous pitch sets, never sequentialized.
- [ ] Each staff/voice keeps its own notes, rests and durations. A sustained LH event overlaps RH events without retriggering.
- [ ] Repeated notes have distinct attacks; tied continuations are shown and sustained without a new attack.
- [ ] Source rests, accidentals, ties, dotted values, tuplets, repeats, ornaments, articulations, dynamics and multi-voice details are compared with the file. Any construct the parser/renderer/matcher does not fully support blocks playability; it is never omitted or approximated silently.
- [ ] Section start/end boundaries follow source measures/beats and do not orphan a tie. Excerpt scope and boundary are visible.
- [ ] Static score and moving score display all events in range. Wrapping occurs only at measure boundaries and the fixed-center playhead remains aligned.
- [ ] Optional fingerings are source-provided or separately attributed/reviewed editorial suggestions. Missing source fingers stay missing; no MIDI-pitch-to-finger generator or blank/undefined finger bubble.

## Curriculum, input and feedback

- [ ] Every lesson names one observable aim, exact variant, staff/voice and source passage, prerequisite and source-based explanation.
- [ ] RH/LH practice filters events from the same canonical source passage; no octave-doubled melody or invented easier arrangement.
- [ ] Microphone mode is restricted to a supported monophonic hand/voice. Chords, both-hand/polyphonic and independent duration grading are disabled or clearly unavailable.
- [ ] Feedback states only what the chosen input and timing mode actually measure. No claim of fingering, posture, legato, expression or full rhythm quality when not assessed.
- [ ] Note-wait/pitch-finding practice is labeled and does not claim rhythm mastery.
- [ ] Demo playback, visible notation and input matching derive from the same event timeline.

## Scope, navigation and progress

- [ ] Whole available score and named section are explicit session scopes. Section/whole, variant, hand and input progress are stored separately.
- [ ] Finishing a section never marks the full score performed; finishing all sections never auto-awards a whole run.
- [ ] The last section offers a separate whole-score run. Prev/Replay/Next are grouped, disabled at boundaries and never wrap silently.
- [ ] MIDI result shortcuts invoke the same scoped actions as visible buttons.
- [ ] Scope/input changes cancel scheduled audio, timers and held-note/attack state. Pause/resume, replay and note-off cleanup do not leak attacks across passages.
- [ ] Legacy generated-course completion is preserved separately and cannot award mastery for a different sourced edition.

## Release verification

- [ ] Source-to-event and source-to-engraving comparisons cover every measure for pitch, spelling, rhythm, rests, voices, chord membership, ties, pickup, hand and source fingering.
- [ ] Tests cover repeated attacks, held bass, chord order, rests, independent note-offs, ties, early/late behavior, pause/resume, replay, hand/input changes, scope boundaries, progress reload and cancellation.
- [ ] Invalid/unsupported data is rejected before appearing playable. Include a fixture with a chord, rest, tie, unequal hand durations, staggered onsets and absent fingering.
- [ ] Browser smoke checks cover desktop and phone/tablet widths, static sheet coverage, scrolling, source details, keyboard/touch, MIDI and download. Real hardware/permissions are reported separately from VM tests.
- [ ] Downloadable HTML works without network requests; source attribution and missing-target status are visible.

## Current audit notes

- The existing page has 100 classical `melodyData` entries and appends 42 distinct game/pop-culture motifs at runtime (142 melody records altogether). The 100 base records all point to the Mutopia homepage and identify themselves as simplified pitch studies with original rhythm omitted; none establishes authentic complete-score or exact book-edition coverage.
- Current source research catalogs 20 exact score/arrangement candidates: 8 local Mutopia LilyPond sources and 12 G Major external-only arrangements. This is not 20 playable variants. Only the Blue Danube arrangement and Ode soprano line have conversion data ready for direct event validation; Ode must remain a soprano reading line, not a piano arrangement.
- Do not call the build release-ready from schema validation alone. The plan requires source comparison, notation support, playable UI, scope-aware progress and device checks.
