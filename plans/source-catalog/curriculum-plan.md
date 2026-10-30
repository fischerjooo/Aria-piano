# Aria: source-first classical piano curriculum proposal

Status: curriculum design and audit, 29 October 2026. This is a replacement plan, not a claim that the current app provides a complete beginner piano course. No app code changed by this review.

## The central correction

Teach a small collection of already-published, progressively suitable piano arrangements through their actual music. A lesson is a source-preserving passage, a listening or reading task about that passage, and one achievable performance goal. A changed pitch-index route is not a new musical lesson. Three copies of an exercise with arbitrary note permutations are not three educational levels.

The learner's goals are recognisable classical themes, especially Ode to Joy and The Blue Danube, and eventually pieces represented by the supplied book contents photograph. Start with a few genuinely suitable variants and deepen the learner's ability to read and play those scores. Do not manufacture a large catalogue or claim the famous originals are beginner works.

Use only already-created online variants. Do not create new Aria arrangements, transpose the selected edition, replace difficult notes, assign a new generated accompaniment, or change the written rhythm to make a level easier. A clearly labelled exact excerpt, one-hand mode, or slower tempo is a practice mode of the same edition. It is not a separate easier arrangement.

## What the current implementation gets wrong

These findings refer to the pre-migration `index.html` inspected during this review.

- `reviseBeginnerCourse()` around lines 551–608 applies `assignRoute()` to pitch, finger number, note value, hand part, and duration arrays using arbitrary index paths. Preserving the old finger number at each selected index does not produce a phrase-appropriate fingering for the reordered music.
- A challenge can be the same material with another path appended. Applications can concatenate path fragments, receive the name “Original miniature,” and claim a complete musical phrase without a source score or an actual composition review.
- The function cycles rhythm arrays over unrelated pitches. Earlier lessons overwrite existing note values, choose detached holds, and round rhythms. This removes the rhythmic identity of the tune even where the title survives.
- `handMoves()` near line 373 infers a crossing or shift from pitch and finger deltas. Such an inference is not evidence of a teacher-approved movement or fingering. A pitch contour alone cannot decide whether the pianist should cross, substitute, release and move, or choose a different starting finger.
- `l.left` uses one left-hand entry per right-hand step. That is not a general score model. Real music includes independent attacks, held melody over changing accompaniment, simultaneous chords, rests in one hand, and ties.
- The practice score is described as an “unbarred learning score.” Real 3/4 waltz teaching requires visible bars, meter, pickup, note values, rests, ties, and grouping. A series of pitches with hold proportions cannot substitute for those concepts.
- Dependencies ultimately become positions in a long course array. That can lock a target piece behind irrelevant scale exercises while failing to require its actual rhythm, chord, or coordination skill.

Recommendation: retire these generated curriculum payloads from the default course rather than polishing their descriptions. Preserve unrelated working MIDI, audio and UI infrastructure if useful. Retain any old progress only as “legacy practice”; never silently convert completion of arbitrary routes into mastery of a new score passage.

## Source status and truthful labels

The source review is maintained by `score_sources_sol`; its catalogue is the authority for URLs, attribution, permission, and variant identity. The following educational assignments are based on the sources examined so far.

| Variant | What it actually is | Curriculum use | Current status |
|---|---|---|---|
| Mutopia 519, The Blue Danube Waltz (main theme), N. Kouremenos | Published C-major piano arrangement of the main theme, derived from a four-hand piano reduction; not Strauss's entire orchestral waltz | Exact melody, actual bass/chord waltz accompaniment, phrase reading and coordination | Local LilyPond examined; CC BY-SA 4.0 attribution and share-alike requirements must accompany reuse |
| Mutopia 528, Ode to Joy SATB | Vocal/choral arrangement, not a novice solo-piano edition | Exact soprano-line reading study only, with the vocal origin visible; no claim of complete piano arrangement mastery | Local LilyPond examined: 16 full 4/4 bars, G major, 64 quarter-note beats; source states public domain |
| G Major Music Theory Ode to Joy “First Pieces” / 1A / 2B | Different published easy piano variants; the labels identify that publisher's levels | Promising early melody and later accompaniment tracks | External score links only unless permission is obtained; exact phrase ranges not yet verified here |
| G Major Music Theory Blue Danube 2B | A different published novice piano arrangement | Possible alternate milestone chosen by its actual notation and demands | External link only unless permission is obtained; do not merge notes with Mutopia 519 |
| G Major Spring 2A, Eine kleine Nachtmusik 2B, Für Elise 1B, Beethoven Fifth 1C, Brahms Lullaby 3B, Canon 3B | Specific published thematic arrangements, not their complete original works | Future repertoire candidates, after inspecting exact scores | External-reference candidates, not imported playable content |
| Mutopia original Gymnopédie No. 1, Für Elise, Clair de lune | Original piano works / source editions, not automatically beginner variants | Listening goals and later study; selected originals require an honest separate difficulty audit | Do not promote their full original scores as novice completion targets |

Do not display a candidate as playable until score, rights, events and pedagogy have all passed review. Permission-pending scores can be shown as external reading resources without importing their score files, note payloads, engraving or MIDI. Source discoverability and redistribution permission are separate questions.

## The reference book is a destination list, not a teaching order

The supplied contents image lists 37 recognisable themes. It shows titles and opus numbers but no edition, arranger, notation, keys, fingering, page layouts, difficulty statements or permission terms. It is good evidence of repertoire preferences, and insufficient evidence to reconstruct its arrangements.

Early candidates in an appropriate exact arrangement include Ode to Joy, a lullaby theme, a small part of Spring, or a short familiar theme. The Blue Danube is a motivating waltz milestone. Für Elise, Beethoven Fifth, Pachelbel Canon and Eine kleine Nachtmusik can have accessible published theme arrangements, but their originals or entire forms must not inherit an “easy” label from the theme's familiarity. Clair de lune, La Campanella, Chopin Nocturne Op. 9 No. 2, Mozart piano concertos and complete sonatas remain long-term listening/repertoire goals unless a separately sourced suitable simplified edition is selected.

Distinguish origin from playable variant in every card, for example: “The Blue Danube — main theme; piano arrangement by N. Kouremenos; C major; excerpt.” Spring is from a violin concerto; Ode to Joy is the theme from the finale of Beethoven's Ninth Symphony; the selected SATB source is a further vocal arrangement. A piano lesson must name the piano arranger when it has one. “Wiegenlied” and “Menuett” alone are ambiguous; do not assign a composer or work from the title alone.

## Difficulty and progression model

Use descriptions of the actual score demands instead of universal beginner/intermediate claims. Publisher levels such as 1A and 2B remain publisher-specific metadata. Assess each variant for: range and position changes; clefs; accidentals/key signature; shortest note value; meter and pickup; ties/rests; chord size and span; simultaneous and independent hands; articulation; and tempo. List the first new barrier explicitly.

A compact progression can contain the following stages. These are pedagogical stages, not fixed weeks and not a promise that currently available licensed content fills every stage.

| Stage | Concrete learner capability | Repertoire task and exact-score rule | Ready to continue when |
|---|---|---|---|
| 0. Hear and locate | Recognise keyboard groups; distinguish hands and finger numbers; find a starting key; feel a steady pulse | Listen to an approved exact passage, point to the phrase's first/last note, tap its beat and find its first key. No invented pitch exercise required | Can find the named starting note and keep the pulse for the excerpt while hearing it |
| 1. First melody reading | Read repeated notes and steps; distinguish note name from finger number; understand a written quarter note | Mutopia 528 soprano bars 1–3, an exact three-bar fragment in G4–D5. Bar 4 is deferred because its dotted-quarter/eighth rhythm is a new demand. Alternatively use a genuinely easy published Ode piano variant when rights permit | Plays the short fragment slowly with correct notes and pulse, and can explain repeated note versus step |
| 2. Landmarks and intervals | Read treble guide notes and nearby steps/skips; begin bass guide notes separately | Revisit an exact melody phrase; introduce a genuine bass passage from the selected arrangement as a separate reading task. Use clef and line/space reference, not “C always uses thumb” | Finds starting landmarks on both staves; predicts direction and a skip before playing; does not need every key highlighted |
| 3. Meter, silence and phrase endings | Count quarter/half/whole values when present; count rests; understand bars; hear question/answer | Select another exact passage with those values. Introduce each new notation item from an actual score location. Do not claim a whole note has been taught by a score that contains none | Can tap the notated rhythm, count through a rest and sustain a written value without adding attacks |
| 4. First coordination | Prepare both hands; align simultaneous attacks; sustain one hand while the other plays | Use an already-published suitable two-hand variant, each hand alone first, then a small intact phrase. Do not add a bass note to every melody note | Both hands keep their independent written durations in a slow count; can restart from a bar boundary |
| 5. Waltz foundation | Count “1 2 3,” understand pickup, read bass-note/chord accompaniment; distinguish beat from note | Mutopia 519 source bars 1–6, first listening/counting, then LH bars 3–6, then RH bars 1–5 when dyads and the register move are prepared. These are different tasks on the same score | Counts through all three beats; LH bass and chord attacks are distinct; does not force a fixed five-finger position through the RH jump |
| 6. Theme with changing harmony | Read fourths/fifths and dyads; prepare hand moves; change bass harmony while retaining waltz pulse | Mutopia 519 source bars 6–17, divided by actual motifs (6–9, 10–13, 14–17), then connected. Include the pickup note that belongs to the next motif in context | Can locate each destination before playing and connect the passage without an unplanned stop |
| 7. Longer holds, accidentals and rhythmic detail | Maintain accompaniment under tied melody; read an accidental, dotted-quarter/eighth grouping, and ending rests | Mutopia 519 source bars 18–34, split 18–21, 22–25, 26–30, 31–34. Teach F-sharp at source bar 28 and the dotted rhythm at bar 33 before joining | Holds the tied melody while the LH continues; performs the accidental and dotted rhythm as written; counts the final rest |
| 8. A complete selected arrangement | Plan a whole short arrangement, hear phrase structure, recover at phrase boundaries | Mutopia 519 entire main-theme piano arrangement. Reuse the source's dynamics and phrasing. Learning tempo can remain slower than printed MIDI tempo | Can play a coherent musical run, identify one improvement and demonstrate the correction. App success does not certify physical technique |
| 9. Transfer to another verified score | Recognise familiar skills in a different key, texture or phrase; read unfamiliar details | Choose the next inspected online variant from the user's classical themes. Its prerequisite set comes from its notes and rhythm; it is not automatically the next item in an array | Can preview key/meter, landmarks, largest movement and new rhythm; play a short first reading then isolate one difficulty |

Stages 1–4 currently expose a real source gap: a rights-cleared, genuinely early piano arrangement has not yet been established in this review. Do not fill that gap by composing fake examples or calling a later arrangement “Lesson 1.” External-score coaching can operate honestly while suitable in-app sources or permissions are established. A one-line choral excerpt can teach one-line reading, but cannot supply an entire piano foundation course.

No octave scale, harmonic/melodic minor sequence, arpeggio syllabus or transposition requirement is necessary merely because it looks like a complete piano method. Add a very short technique preparation only when the next actual score passage requires it, and retain its musical context. Such preparation must not mutate the source into a new supposed edition.

## Exact early reading slice: Mutopia 528 Ode to Joy soprano

Verified against `sources/ode-to-joy-satb.ly`, variable `sop`. The arrangement contains 16 complete 4/4 bars, with double bars after 4, 8 and 12. The soprano is transposed up an octave in the source; perform the final written pitches, not the lower untransposed tokens. Source playback tempo is quarter = 100. No fingering is supplied.

| Passage ID | Source bars / voice | Task and prerequisites |
|---|---|---|
| OJ528-sop-first-notes | 1–3, soprano only | Three-bar fragment: repeated notes and steps, all quarters; G4–D5 range. Learn B4 starting landmark and identify G4/D5 boundaries. Show G-major key signature honestly, while explaining that this fragment does not sound its F-sharp. This is an unchanged vocal melody played on piano, not a separate published piano edition |
| OJ528-sop-first-phrase | 1–4, soprano only | Complete first phrase. First clap/count source bar 4: dotted quarter, eighth, half. Keep the pulse and subdivisions rather than replacing the dotted rhythm with four quarters |
| OJ528-sop-answer | 5–8, soprano only | Compare same opening with different answer at bar 8; source supplies the musical variation. Read the changed ending before playing |
| OJ528-sop-middle | 9–12, soprano only | Read eighth-note groups at 10–11 and prepare the descent to D4 at 12. This passage leaves the G4–D5 five-note region, so introduce register reading and lateral movement; do not claim the entire tune fits one five-finger position |
| OJ528-sop-return | 13–16, soprano only | Read the return and compare its ending with 5–8, then connect the 16-bar line |

The first-notes fragment is a defensible small starting lesson, not evidence that the complete source is an absolute-beginner piano piece. The source's alto, tenor and bass must remain visible as contextual voices in a full-source view, but are not automatically assigned to the learner's left hand. Do not turn this SATB setting into a new two-hand arrangement or silently copy its bass into a beginner piano accompaniment. A published genuine early piano score is still needed for the first complete piano-arrangement track.

## Exact first vertical slice: Mutopia 519 Blue Danube

Verified against `sources/blue-danube.ly`. **The source's own comments call the quarter-note pickup bar 1. Bars 2–34 are 33 full 3/4 bars.** Thus the written music contains 100 quarter-note beats. This document uses those source-comment numbers. A UI using pickup bar 0 must keep an explicit mapping and must not silently subtract one from a saved passage identifier.

| Passage ID | Source bars | Main point | Not a claim that… |
|---|---|---|---|
| BD519-listen-opening | 1–5 | Hear the pickup, three-beat grouping, rising C–E–G idea and answering dyads | The whole passage is single-note five-finger material |
| BD519-rh-entry | 1–2 | Exact short opening fragment, one-hand note location and rising broken-triad contour | Two measures constitute a complete musical phrase or a full tune |
| BD519-lh-first-waltz | 3–6, lower staff only | C bass followed by E/G dyads on beats 2 and 3; prepare and release the actual chord shapes | The learner is playing an invented C note under every melody step |
| BD519-rh-first-phrase | 1–5, upper staff only | Actual upper-register move and repeated dyads; sustained values | Removing one note from each dyad is the same edition |
| BD519-both-first-phrase | 1–5, both staves | LH enters at source bar 3 while RH has a half note and then a dyad | Hands always attack together |
| BD519-dominant-answer | 6–9 | Recognise repeated opening with changed harmony and dyads | Repeating a motif is a new arbitrary route |
| BD519-second-motif-a | 10–13 | B–D–A idea, changing hand location and true chord support | A prescribed thumb crossing can be deduced from pitch order |
| BD519-second-motif-b | 14–17 | Same motif with different answer | The ending may be rewritten to be easier |
| BD519-upper-phrases | 18–21 and 22–25 | Higher C-major outline, harmonic changes; LH changes and sustained chord at 25 | The whole arrangement fits a fixed home position |
| BD519-tied-line | 26–30 | D–F–A outline, ties spanning bars, F-sharp–G at 28, independent LH | The app may retrigger tied notes or drop ties from the score |
| BD519-cadence | 31–34 | Whole-bar LH chords, dotted-quarter/eighth detail at 33, final rest | A steady quarter-note pulse is the entire written rhythm |
| BD519-main-theme | 1–34 | Connect this published main-theme arrangement | This is the complete Op. 314 orchestral waltz |

The named segments follow the source's musical grouping. Some begin with the final beat in the preceding measure; the lesson should play or visually include that entry in context rather than teaching a mechanically isolated bar. Exact beat-level start/end boundaries must be reviewed in engraving before playback excerpts are finalized. None of the above authorizes omission of difficult notes, voice flattening or a changed key.

The source contains **no finger numbers**. Show “No fingering supplied by this edition” and allow hints to remain absent. Do not fabricate finger numbers or call them printed/source fingering. If a qualified pianist later supplies optional editorial suggestions, label their provenance and review the whole phrase, hand size, chord span, direction of motion and next destination. The app cannot verify the learner's finger or wrist movement from MIDI.

The source's MIDI tempo is quarter = 150. That is playback metadata, not an entry requirement. Count three quarter-note beats per bar at the learner's comfortable tempo; do not reinterpret it as one beat per whole measure. The music retains its meter when slowed.

## Passage and lesson specification

Before authoring learner instructions, store immutable `scoreVariantId`, composer/work, arranger/editor, exact source URL and edition/version, source hash, license and attribution, key, meter, pickup convention, and verified numbering map. A passage adds source staff/voice, start/end bars and beats, independent note/rest events per voice, expected total duration, and explicit practice goal. It must point back to that exact score; a title match is not enough.

A lesson may have “Listen and count,” “Read the right hand,” “Read the left hand,” “Join hands,” and “Play the phrase.” Only show modes appropriate to that passage. Do not require three modes or three levels by template. Every hand mode is a filter of the same canonical events; chord membership, ties, rests, bar position and duration survive the filter.

Instruction sequence:

1. Hear the recognisable phrase and locate it in the real score.
2. Identify the one new thing: an interval, duration, rest, hand move, chord, or coordination point.
3. Prepare its location silently, or tap/count its exact rhythm.
4. Play a short musical group at a comfortable pulse. Use a note-wait mode only as a clearly labelled note-finding aid.
5. Rejoin the group to the phrase. Listen for the phrase's arrival and take a specific result forward.

Do not tell a learner that a run with timing disabled proves correct rhythm. When a task is note finding, say so. A listening/reading question can teach notation without pretending that the input device assesses the answer.

## Completion and prerequisites

Completion is per exact score variant, passage, hand mode and task. Slow practice and note-wait completion remain distinct from a steady-pulse run. Display learning tempo honestly. A clean MIDI result supports correct pitches and the enabled timing checks; it does not establish fingering, posture, ease, legato quality or expression. Microphone pitch mode cannot certify polyphonic bass/chord coordination or independent durations. Touch input is useful exploration but must not be reported as piano performance.

Use small skill prerequisites: for BD519 hands-together opening, require its actual RH dyads/register preparation, its LH bass/chord pattern and 3/4 count. Do not require completing all harmonic minor scales, and do not infer readiness merely from a numerical course index. Provide a preview/diagnostic route so a learner with existing skills can enter the relevant passage directly.

A reasonable passage completion check is one coherent slow run followed by a second attempt or targeted correction that demonstrates the goal. Avoid unlimited mechanical repetitions or a fixed three-clean-runs policy applied to everything. The learner should be able to describe the change they made; comfortable movement and phrasing remain listening/self/teacher observations.

## Review checklist before anything is called a lesson

- The linked file is the exact edition used for all notes, rhythms, clefs and hands, not merely a page with the same title.
- Reuse permission and attribution are recorded. A free PDF is not automatically embeddable content.
- The app's event/engraving representation matches the score at the passage's start, end, pickup, ties, rests, accidentals and chords. Count each measure in each voice; do not repair mismatches by padding a generated rest silently.
- Every event retained its source onset and duration; no index path, cyclic rhythm, auto-transposition, fake bass, clipped chord or rounded note value has altered it.
- The musical excerpt is labelled correctly as a fragment, phrase, theme or complete selected arrangement; no fake total bar count or full-work claim.
- The difficulty describes this version and identifies its actual first barrier. “Famous” is not a difficulty level.
- Fingering is either truly present in the edition, explicitly reviewed and editorial, or absent. No pitch-delta movement generator writes physical technique instructions.
- Reading and rhythm features have been taught before they are required, or the passage contains a clear preparation task. Both clefs, rests and 3/4 are not hidden in generated prose.
- Hands are independent voices on a common musical timeline, and held notes survive other-hand attacks. A chord is simultaneous, not an arpeggio unless written.
- Playback, visible notation and input checking use the same canonical events. An app can pass software tests while teaching incorrect music; compare it with the actual score by listening and inspection.
- The lesson's task, feedback and completion statement agree with what the current input mode can assess.
- Each new lesson contributes a distinct musical learning objective. If it only changes an arbitrary note route, remove it.

## Pedagogy references and boundaries

This is a proposed repertoire-led design, not an endorsed Faber or Alfred syllabus. It does not copy their teaching pieces or import their notation.

- Faber's own Primer Q&A describes a progression from direction to guide notes, nearby notes and intervals: https://pianoadventures.com/piano-books/basic-piano-adventures/primer/q-and-a/ . This supports gradually expanding reading rather than immediately using every note of a long unfamiliar piece.
- Faber's own teaching explanation discusses varied fingerings so a note is not confused with a fixed finger, and concurrent interval/contour reading: https://pianoadventures.co.uk/resources/why-use-piano-adventures/ . This supports teaching staff-to-key relationships; it does not justify random generated finger changes.
- Faber's official pre-reading pedagogy discusses feeling pulse and musical direction before naming all symbols: https://primerguide.pianoadventures.com/units/the-pre-reading-process/ . This supports listening/counting the real target phrase as an entry point.

Those references inform sequencing only. The exact score and an honest barrier review determine each actual lesson. The urgent deliverable is a small, accurate, clearly attributed playable source slice and a visible source-gap list, followed by more verified online beginner variants—not another large generated course.
