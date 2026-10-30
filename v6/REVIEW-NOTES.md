# Aria v6 candidate review notes

This candidate includes Mutopia 519's published Blue Danube main-theme piano arrangement and the unchanged soprano line of Mutopia 528's SATB Ode to Joy setting, plus 23 source-bound lessons. It is a development candidate; it is available separately as the experimental v6 download. The stable root index remains v5.27 to preserve the established UI and features.

Practice offers note-wait and timed pulse. Timed mode starts on the first correct attack, freezes at an unplayed target, resumes from that target, counts a target more than 500 ms late once, and counts touch/MIDI note releases more than 150 ms early. Microphone onset detection is monophonic and restricted to E2–C6; it does not assess physical note release. Neither mode evaluates posture, fingering, dynamics, or musical expression.

The score renderer uses individually flagged eighth notes rather than source beams, and basic slur/accidental positioning rather than full engraving collision avoidance. The sheet systems scroll horizontally when needed. Independent visual inspection in a real browser remains necessary, especially for chord collisions, accidentals, slurs and mobile layout.

Input adapters and timing were tested with simulated devices and a controlled clock; actual MIDI, Bluetooth, microphone hardware and browser permissions have not been tested. Browser support for Web MIDI, Bluetooth, microphone and fullscreen varies. The linked source editions and licenses are shown in the app. Progress uses a new source-specific key and does not import old generated-exercise completion.
