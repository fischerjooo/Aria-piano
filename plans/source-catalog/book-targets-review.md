# Contents-image transcription and repertoire audit

## Image transcription

`book-targets.json` contains 37 numbered titles transcribed from the attached contents image. German wording and catalog numbers are retained in `image_title`; the normalized work/composer fields identify only likely or unambiguous works. In particular:

- No composer or work is inferred for the two generic entries **Wiegenlied** (#4) and **Menuett** (#22).
- **Das 2. Klavierkonzert K 488** (#27) is preserved exactly as printed even though K. 488 identifies Mozart's Piano Concerto No. 23.
- **Sonate Nr. 11, K 331 / 300** (#10), **Eine kleine Nachtmusik K. 525** (#23), **Schwanensee** (#30), **Der Nussknacker Op. 71** (#34), and **Suite Nr. 3 BWV 1068** (#36) name a larger work without specifying the movement/excerpt.
- #19's G-minor Adagio attribution is contested; #37's “Mondglanz” is treated as likely referring to “Clair de lune,” not as confirmed.

## Existing `piano/index.html` melody data

Parsed the static `const melodyData` array in `piano/index.html`:

- **100 classical repertoire records** in the base `melodyData` array. The page adds 30 `gameMelodies` and 12 `NEW_MELODY_MOTIFS` at runtime, for **142 total melody records**. The 42 additions are separate game/pop-culture motif content, so “100” is not the page-wide total.
- **100/100** use the same generic `https://www.mutopiaproject.org/` source homepage; no record links to an identified score, edition, page, or arrangement.
- **100/100** state `arrangement: "Simplified pitch study · original rhythm not reproduced"`; their instructions describe a short, transposed recognizable opening study and explicitly say it is not a complete original score.
- These records are short, simplified pitch/sequence exercises (14–37 notes in this data set), including many studies that use popular songs and famous classical themes. They do not establish a full, authentic composition score or validate that a named book edition contains the same arrangement.

Treat the existing melody records as generated/curated motif studies for practice, not as source-backed complete works and not as evidence of exact book-score coverage. Any source-first replacement needs a score-level source and arrangement match for each target; this audit does not establish those matches.
