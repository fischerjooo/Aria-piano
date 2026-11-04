# Automatic fingering benchmark

Aria's fingering engine is calibrated against a curated corpus of public-domain/common teaching melodies in `tests/fingering_corpus.py`.

The purpose is not to claim that every passage has one uniquely correct fingering. Piano fingering depends on hand size, articulation, phrasing, tempo, and editorial intent. Instead, the suite separates:

- **Canonical cases**: fixed five-finger positions, standard scale/turn patterns, or passages whose source gives a strong finger-by-finger pedagogical recommendation. These are hard regression gates.
- **Editorial reference cases**: published, reasonable fingerings where another ergonomic fingering can also be valid. These contribute to the aggregate agreement score but do not individually fail the build.

## Coverage

The corpus currently contains 61 cases across 50 distinct melodies: 51 short/medium reference cases plus 10 long-form phrase/melody cases.

1. Hot Cross Buns
2. Mary Had a Little Lamb
3. Ode to Joy (right hand)
4. When the Saints Go Marching In
5. Lightly Row
6. Yankee Doodle
7. Row Row Row Your Boat
8. Au Clair de la Lune
9. Happy Birthday
10. Twinkle Twinkle Little Star
11. Jingle Bells
12. Frere Jacques
13. London Bridge
14. In the Hall of the Mountain King
15. Fur Elise
16. Turkish March
17. Minuet in G
18. The Entertainer
19. Amazing Grace
20. Silent Night
21. Ode to Joy (left hand)
22. Old MacDonald Had a Farm
23. Brahms' Lullaby
24. Auld Lang Syne
25. Away in a Manger
26. Deck the Halls
27. God Rest Ye Merry Gentlemen
28. Joy to the World
29. O Christmas Tree
30. O Come All Ye Faithful
31. Hark the Herald Angels Sing
32. Carol of the Bells
33. The First Noel
34. We Three Kings
35. We Wish You a Merry Christmas
36. O Holy Night
37. Eine kleine Nachtmusik
38. Greensleeves
39. Gymnopédie No. 1
40. Here Comes the Bride
41. Swan Lake
42. Wedding March
43. William Tell Overture
44. Canon in D
45. Habanera
46. Prelude in C Major, BWV 846
47. America the Beautiful
48. Itsy Bitsy Spider
49. Jesus Loves Me
50. The Star-Spangled Banner
51. Good King Wenceslas

Long-form duplicates used specifically to test hand-position stability over 25–64 notes:

52. Ode to Joy — long form
53. Lightly Row — long form
54. Jingle Bells — long form
55. Old MacDonald Had a Farm — long form
56. Amazing Grace — long form
57. Happy Birthday — long form
58. Minuet in G — long form
59. Mary Had a Little Lamb — long form
60. Row Row Row Your Boat — long form
61. Yankee Doodle — long form

This exercises fixed positions, skips, repeated notes, six-note stretches, octave-range shifts, phrase repositioning, black keys, chromatic turns, left-hand mirroring, large intervals, thumb crossings, minor-key positions, chromatic descent, broken-chord patterns, repeated-note fanfares, and explicit scale crossings.

## Current quality gate

The benchmark reports both individual note agreement and exact case agreement. The current calibration target is:

- 100% exact agreement for all canonical/high-confidence cases;
- at least 80% finger-by-finger agreement across the heterogeneous full corpus;
- at least 85% finger-by-finger agreement across the 10 long-form references;
- at least 40 exact cases overall and at least 5/10 exact long-form cases;
- standard one-octave C-major scale fingering in both hands;
- no hard-coded fingering arrays in the shipped lesson/song packages.

These aggregate floors are regression baselines, not claims that one publisher's fingering is uniquely correct. The current calibrated result after adding the long-form corpus is **766/911 = 84.1%** overall and **337/386 = 87.3%** on long-form references, with **40/61** cases exact and **5/10** long-form cases exact. The **30 canonical/high-confidence cases are all exact (30/30)**; long arrangements with legitimate publisher-specific shift choices are retained as reference-only cases so their disagreement remains visible in the aggregate score.

The corpus is deliberately stored as reviewable data rather than hidden inside cost weights. New fingering rules should be justified by adding or updating benchmark evidence first.

## Research basis

The optimizer follows the same broad direction as established automatic fingering research:

- Parncutt et al., *An Ergonomic Model of Keyboard Fingering for Melodic Fragments* — relaxed, comfortable, and practical finger spans; next-note-next-finger preference; black/white key geometry.
- Yonebayashi, Kameoka & Sagayama, *Automatic Decision of Piano Fingering Based on Hidden Markov Models* — global sequence optimization using Viterbi search rather than greedy note-by-note choices.
- Yamaha keyboard fingering guidance — economy of motion, stable hand coverage, use of all fingers, and contextual rather than absolute avoidance of the thumb on black keys.

Reference URLs for every melody case are kept alongside the expected sequence in `tests/fingering_corpus.py`.
