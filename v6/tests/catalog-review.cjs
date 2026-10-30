// Independent curriculum/catalog checks. Run with: node v6/tests/catalog-review.cjs
// Source/MIDI fidelity still requires the separate publisher comparison.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

const root = path.resolve(__dirname, '../..');
const json = (p) => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const plan = json('src/repertoire/learning-path.json');
const scores = [
  json('src/repertoire/mutopia-519-blue-danube.json'),
  json('src/repertoire/mutopia-528-ode-satb.json'),
];
const byId = new Map(scores.map((s) => [s.id, s]));

// Keep book identities separate from sourced playable scores. Ambiguous contents
// entries must remain unresolved until the book supplies more information.
const targets = JSON.parse(fs.readFileSync(path.resolve(root, 'plans/source-catalog/book-targets.json'), 'utf8'));
assert.equal(targets.items.length, 37, 'transcribed target count');
for (const n of [4, 22]) {
  const item = targets.items.find((x) => x.n === n);
  assert.ok(item, `target #${n} exists`);
  assert.equal(item.normalized_work, null, `generic target #${n} remains unresolved`);
  assert.equal(item.composer, null, `generic target #${n} has no inferred composer`);
}

assert.equal(plan.sourceNumbering['mutopia-519-blue-danube'].lastSourceBar, 34);
assert.equal(plan.sourceNumbering['mutopia-528-ode-satb'].lastSourceBar, 16);
for (const lesson of plan.lessons) {
  const b = lesson.binding;
  const score = byId.get(b.scoreId);
  assert.ok(score, `${lesson.id}: binding resolves to included source`);
  assert.ok(b.sourceBarStart >= score.measures[0].number, `${lesson.id}: starts in score`);
  assert.ok(b.sourceBarEnd <= score.measures.at(-1).number, `${lesson.id}: ends in score`);
  assert.ok(b.sourceBarStart <= b.sourceBarEnd, `${lesson.id}: ordered bar range`);
  assert.ok(b.parts.every((part) => score.parts.includes(part)), `${lesson.id}: source parts exist`);
}

for (const score of scores) {
  assert.equal(score.fingeringStatus, 'No source fingering; no fingering generated');
  assert.ok(score.events.every((e) => e.pitches.every((p) => p.finger === undefined)), `${score.id}: no invented fingering`);
  for (const section of score.sections) {
    const first = score.measures.find((m) => m.number === section.sourceBarStart);
    const last = score.measures.find((m) => m.number === section.sourceBarEnd);
    assert.ok(first && last, `${score.id}/${section.id}: source bars exist`);
    assert.equal(section.start, first.start, `${score.id}/${section.id}: starts on source bar`);
    assert.equal(section.end, last.start + last.duration, `${score.id}/${section.id}: ends on source bar`);
  }
}

// The retained Mutopia 519 LilyPond source has two explicit ties:
// bar 27 A dotted-half -> bar 28 A quarter; bar 29 E dotted-half -> bar 30 E quarter.
// Tie flags belong to pitches so a tied pitch in a chord remains distinguishable.
const danube = byId.get('mutopia-519-blue-danube');
for (const [bar, nextBar, spelling] of [[27, 28, 'A4'], [29, 30, 'E5']]) {
  const source = danube.events.find((e) => e.measure === bar && e.pitches.some((p) => p.spelling === spelling));
  const continuation = danube.events.find((e) => e.measure === nextBar && e.pitches.some((p) => p.spelling === spelling));
  assert.ok(source && continuation, `source tie ${spelling}: bars ${bar}-${nextBar} have both events`);
  assert.ok(source.pitches.some((p) => p.spelling === spelling && p.tieStart === true), `source tie ${spelling}: bar ${bar} carries tieStart`);
  assert.ok(continuation.pitches.some((p) => p.spelling === spelling && p.tieStop === true), `source tie ${spelling}: bar ${nextBar} carries tieStop`);
}

console.log('PASS independent catalog, source-range, section, fingering and tie checks');
