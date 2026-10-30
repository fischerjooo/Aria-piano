# Aria Piano — requested rework

## Baseline and non-regression requirement

- [ ] Continue from the complete v5.26 interface and feature set. Do not replace it with the reduced v6 candidate.
- [ ] Rework curriculum and repertoire incrementally while preserving the established UI, input options, settings, timing behavior, lesson flow, responsive layouts and sheet controls.
- [ ] Keep later v5.27/v6 work available separately for reference and selective integration.

The following two requests are copied verbatim from the conversation, including spelling. They describe the requested rework; they are not claims that it has been completed.

## Request 1 — lesson progression after v5.26

> Some lessons title say undefined also the lessons seems not deep enough individual and overall progression questionable in some cases what is played in individual lessons are very similar or only need same set of skill, rethink the lessons and circular keepxit detailed enough but have good clear progression

## Request 2 — classical repertoire and source-based curriculum

> i am very unhappy with the lessons and their progressions and example notes and seuqences and how it is progressing and focusing on, also also about he melodies, instead rework the progression and skills teached towards the goal to be able to read and play songs like: from the book: 37 vereinfachte klassische Stücke für Klavier: Einfache Partituren zeitloser Stücke für Anfänger. Spielen Sie die Stücke, die Geschichte geschrieben ... Sie Ihre Fähigkeiten nach und nach\![https://www.amazon.de/vereinfachte-klassische-St%C3%BCcke-f%C3%BCr-Klavier/dp/B0B3S6BGZH](https://www.amazon.de/vereinfachte-klassische-St%C3%BCcke-f%C3%BCr-Klavier/dp/B0B3S6BGZH) also rework the lessons plan and what melodies are used in the training, the melodies shall be always if possible be sections of those classic songs so even during lessons the user learns parts of those classics and learns the skills one by one to be able to play sections of htem and over time build up the skills to be able to play  all sections and able to read the notes related to them. Also i am very unhappy with the melodies too you added, many of them are way too just computer generated and the finger numbering is looks weird and unnesesary complex or unnatural, so i dont want any auto generated notes from you, instead you should always base your melodies some actual melodies and simplified version found on the interned, also in the melodies list for a given melody have option if possible, for a given melodidy to play a simplified version, or intermediate , or expert version, or original in some cases the original is the same as the simple or intermediate or expert, then no need for original option to show, also some meldied only have intermediate or expert version then only show those, if some only simple thenon ly simple available so have these options and vairant where makes sense and actual different version are avaialble if a song is already have a given dififculty level, then look for simpler if needed, but if never look for more expert/dificult version, the originals dificulty dictate the max diifculty avaialble. so now we rework the notes reading skills and playing skills to build up towards these classics like i refenced in the book , i want to to see better skill progression like towards to able to play An schöner bluen danube op etc.. and again please scan only first for datebases for already created version and versions available online, also rework your existing melodies to actual version found online, what you have already created and present is just way to simple or artifical or short

The accompanying book contents are transcribed with identification caveats in `plans/source-catalog/book-targets.json`. The book's specific arrangements have not been acquired or imported.

## Implementation checklist derived from the requests

- [ ] Fix undefined lesson titles and validate every displayed title.
- [ ] Audit repeated skill demands; make each lesson's purpose and prerequisites explicit.
- [ ] Build a clear progression from beginner reading and playing to the requested classical pieces.
- [ ] Use genuine existing scores and arrangements, retaining exact edition URLs and reuse terms.
- [ ] Teach actual source passages, then longer phrases, sections and complete available arrangements.
- [ ] Replace artificial short melodies; do not generate filler or arbitrary fingering.
- [ ] Offer only independently sourced difficulty variants that actually exist; do not manufacture harder versions beyond the original.
- [ ] Keep section practice and whole-arrangement practice with readable notation and existing polished controls.
- [ ] Review source fidelity, musical progression and feature parity independently before replacing the stable version.

Existing research, candidate code and validation results are retained in `plans/`, `src/repertoire/` and `v6/`; these are inputs to the rework, not proof that the full requests are finished.
