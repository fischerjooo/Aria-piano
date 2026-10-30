# Source scope and remaining repertoire gaps

Verified 29 October 2026. Source/import evidence is distinct from player release readiness. Run the player notation gate, source validator and browser/input checks before describing either import as playable.

## What is actually imported

| Canonical import | Complete available musical scope | Written duration | Named source sections | Teaching use |
|---|---|---|---|---|
| Mutopia 519, N. Kouremenos, Blue Danube | Entire published main-theme piano arrangement, not the full orchestral Op. 314 | 34 source bars: one-beat pickup plus 33 full 3/4 bars; 100 quarter beats | Six sections spanning bars 1–5, 6–9, 10–17, 18–25, 26–30, 31–34 | Exact bass/chord waltz, upper dyads, changing harmony, ties, accidental and cadence |
| Mutopia 528, Peter Chubb, Ode to Joy | Complete 16-bar soprano extraction from SATB; not a published solo-piano arrangement | 16 full 4/4 bars; 64 quarter beats | Four consecutive four-bar source phrases | Monophonic reading, dotted-quarter/eighth rhythm, changed endings and register change |

At 60 quarter beats per minute these available scopes last approximately 100 seconds and 64 seconds. Actual selected tempo determines duration; nothing is lengthened by a loop or generated continuation.

The learning path has 23 source-preserving tasks: short new-skill isolates, complete four-bar phrases, two longer eight-bar Ode assemblies, 17-bar Blue Danube section assemblies and whole available scopes. RH-only tied-line preparation precedes the same two-hand source passage. Hand isolation selects existing events; it is never another arrangement.

## Source comparisons and guarantees

`src/repertoire/validate_sources.py` checks retained asset hashes and compares every Blue Danube sounding note against publisher MIDI: 96 RH and 151 LH attacks, including merged tie durations. All 62 soprano notes appear unchanged in the original Ode upper MIDI track; the source track also contains alto, which is deliberately not imported. Explicit tie-start/stop regressions cover Blue Danube source bars 27–28 and 29–30.

`src/repertoire/validate_curriculum.py` checks all 23 distinct bar/part bindings, complete whole scopes, source duration/event evidence, tie-safe excerpt boundaries, monophonic microphone claims and specific notation statements shown in guides. These checks do not certify physical technique or pedagogy effectiveness.

The standalone exporter rebuilds both canonical JSON files directly from retained LilyPond, avoiding stale converted intermediates. Source assets, per-edition licenses, SHA256 values and original SATB provenance remain in `src/repertoire`. Neither included source provides fingering. No finger numbers have been generated.

## Unfilled content gates

- There is one complete imported piano arrangement and one complete extracted vocal reading line. These are two source imports, not two complete original piano works or a complete beginner course.
- Eight licensed Mutopia editions have retained original LilyPond files and hashes. The other six have no verified playable conversion. Twenty catalog entries and 37 book-target titles are never playable counts.
- Schumann Mélodie, Mutopia 647, is a complete 20-written-bar pedagogical piano original; its four-bar opening repeat makes 24 performed bars. Its CC BY-SA 2.5 edition and actual fingerings are retained. It stays blocked until repeat traversal, simultaneous upper voices at bars 8 and 16, lower treble clef, source finger substitutions and expressions are supported and independently compared with publisher MIDI. A flattened or stripped conversion is not acceptable.
- Petzold Minuet, Gymnopédie, Für Elise, Clair de lune and Mountain King remain source-verified references. Ornamental/polyphonic/repeat and difficulty demands need per-score support checks; familiarity does not establish beginner suitability.
- Twelve G Major Music Theory arrangements remain external-only because their teaching/printing terms do not authorize embedding in this app. Do not copy their note data without permission.
- The mono-to-Blue-Danube progression has a documented coordination/dyad gap. This starter path must not promise a complete primer, automatically award mastery from old generated lessons, or hide this gap behind manufactured exercises.
- No edition has been established as matching Mauro Costa's book. The contents photo establishes repertoire goals only.
