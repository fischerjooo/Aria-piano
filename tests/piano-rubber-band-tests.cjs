const fs=require('fs'),path=require('path'),assert=require('assert');
const root=path.join(__dirname,'..');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const runtime=fs.readFileSync(path.join(root,'src/app/runtime.js'),'utf8');
const template=fs.readFileSync(path.join(root,'src/app/template.html'),'utf8');
const styles=fs.readFileSync(path.join(root,'src/app/styles.css'),'utf8');

assert(template.includes('id="lessonScrubber"'), 'practice room must expose the full-width lesson scrubber');
assert(styles.includes('.lesson-scrubber'), 'lesson scrubber must have dedicated full-width styling');
assert(runtime.includes('function nextFollowRate('), 'rubber-band follower must smooth its playback rate');
assert(runtime.includes('function animateScoreCatchup('), 'rubber-band follower must animate from the current visual position');
assert(runtime.includes('cubic-bezier(.22,.61,.36,1)'), 'catch-up movement must ease rather than jump');
assert(!runtime.includes('if(jumpAhead){scrollScore(pos)'), 'early notes must not hard-jump the score');
assert(runtime.includes("$('lessonScrubber').oninput"), 'scrubber drag must preview the selected position');
assert(runtime.includes("$('lessonScrubber').onchange"), 'scrubber release must seek the lesson');
assert(html.includes('id="lessonScrubber"')&&html.includes('function nextFollowRate('), 'generated app must include the feature');
console.log('Rubber-band follower and full-width lesson scrubber regressions pass');
