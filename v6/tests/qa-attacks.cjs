// Independent regression checks against the retained source export and synthetic edge cases.
const fs = require('fs'), vm = require('vm'), assert = require('assert'), path = require('path');
const player = fs.readFileSync(path.join(__dirname, '../player.js'), 'utf8').split('function stopAll()')[0];
const ctx = {document:{getElementById:()=>({})},localStorage:{getItem:()=>null},console};
vm.createContext(ctx); vm.runInContext(player+'\nthis.qa={validateScore,buildAttacks};',ctx);
const score=JSON.parse(fs.readFileSync(path.join(__dirname,'../../src/repertoire/mutopia-519-blue-danube.json')));
assert.deepEqual(Array.from(ctx.qa.validateScore(score)), [], 'source score must pass supported-notation validator');
assert.equal(score.measures.length,34); assert.equal(score.measures[0].duration,480);
assert.equal(score.measures.at(-1).start+score.measures.at(-1).duration,48000);
const attacks=ctx.qa.buildAttacks(score.events);
const expected=new Map();
for(const e of score.events) if(e.type==='note') for(const p of e.pitches) if(!p.tieStop) {
  if(!expected.has(e.tick)) expected.set(e.tick,[]); let length=e.duration, next=e.tick+e.duration, tied=p.tieStart; while(tied){const continuation=score.events.find(z=>z.staff===e.staff&&z.voice===e.voice&&z.tick===next&&z.pitches.some(q=>q.midi===p.midi&&q.tieStop)); assert(continuation,'source tie resolves'); const q=continuation.pitches.find(q=>q.midi===p.midi&&q.tieStop);length+=continuation.duration;next+=continuation.duration;tied=q.tieStart;} expected.get(e.tick).push(`${e.staff}:${p.midi}:${length}`);
}
assert.equal(attacks.length,expected.size);
for(const a of attacks) assert.deepEqual(Array.from(a.notes,n=>`${n.staff}:${n.midi}:${n.duration}`).sort(),expected.get(a.tick).sort());
const pitch=(m,extra={})=>({midi:m,...extra});
const ev=(id,tick,duration,staff,pitches)=>({id,tick,duration,staff,type:'note',pitches});
const example=[ev('held',0,1440,'LH',[pitch(48)]),ev('chord',0,480,'RH',[pitch(60),pitch(64)]),ev('repeat',480,480,'RH',[pitch(60)]),ev('tie1',960,480,'RH',[pitch(62,{tieStart:true})]),ev('tie2',1440,480,'RH',[pitch(62,{tieStop:true})])];
const a=ctx.qa.buildAttacks(example);
assert.deepEqual(Array.from(a,x=>x.tick),[0,480,960]);
assert.deepEqual(Array.from(a[0].notes,n=>n.midi).sort((x,y)=>x-y),[48,60,64]);
assert.deepEqual(Array.from(a[1].notes,n=>n.midi),[60], 'repeated note is a fresh attack');
assert.equal(a[2].notes[0].midi,62); assert.equal(a[2].notes[0].duration,960); assert.equal(a.length,3,'tie continuation is not re-attacked');
console.log('QA source timeline and attack regression checks passed');
