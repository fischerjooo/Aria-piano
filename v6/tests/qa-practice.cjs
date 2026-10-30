// Practice state integration in a minimal DOM; this does not substitute for browser or hardware testing.
const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const score=JSON.parse(fs.readFileSync(path.join(__dirname,'../../src/repertoire/mutopia-519-blue-danube.json')));
const elements=new Map(); function element(id){if(!elements.has(id))elements.set(id,{id,value:id==='tempo'?'90':id==='timing'?'pitch':'',style:{},hidden:false,disabled:false,innerHTML:'',textContent:'',querySelector:(q)=>q.includes('data-lesson')?null:{disabled:false},appendChild(){},click(){if(this.onclick)this.onclick()},addEventListener(){}});return elements.get(id)}
const ode=JSON.parse(fs.readFileSync(path.join(__dirname,'../../src/repertoire/mutopia-528-ode-satb.json')));
const learning=JSON.parse(fs.readFileSync(path.join(__dirname,'../../src/repertoire/learning-path.json')));
const persisted={}; let resets=0, scheduled=[];
const ctx={CATALOG:[score,ode],LEARNING:learning,console,document:{getElementById:element,querySelectorAll:()=>[],createElement:()=>({dataset:{}})},localStorage:{getItem:()=>null,setItem:(k,v)=>persisted[k]=v},requestAnimationFrame:()=>{},setTimeout:(fn)=>{scheduled.push(fn);return scheduled.length},clearTimeout:()=>{},AriaInput:{create:()=>({reset(){resets++},bindKeyboard(){},selectMode(){},connectMidi(){},connectBluetooth(){},connectMicrophone(){}})}};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(path.join(__dirname,'../player.js'),'utf8')+'\nthis.qa={state,selectScore,setScope,accept,scoreMarkup,openLesson};',ctx);
const {state,selectScore,setScope,accept,scoreMarkup}=ctx.qa;
selectScore(score); assert(state.running); assert.equal(state.index,0); assert.equal(state.timers.length,0,'no pre-play timeout');
const a=state.attacks[0]; for(const n of a.notes)accept(n.midi);assert.equal(state.index,1);element('start').click();assert.equal(state.index,0,'restart resets position');
setScope(score.sections[0].id);assert(element('previous').disabled);assert(!element('next').disabled);
for(const a of state.attacks)for(const n of a.notes)accept(n.midi);
assert(element('result').hidden,'wait mode observes final written duration');scheduled.at(-1)();
assert(!element('result').hidden);let progress=JSON.parse(persisted['aria-source-progress-v1']);assert(progress[`${score.id}|${score.sections[0].id}|both|touch|pitch`]);assert(!progress[`${score.id}|whole|both|touch|pitch`]);
element('resultNext').click();assert.equal(state.section,score.sections[1].id);assert.equal(state.index,0);assert(state.running);
setScope(score.sections.at(-1).id);assert(element('next').disabled);element('resultAll').click();assert.equal(state.section,null);assert.equal(state.index,0);assert(resets>=4,'scope changes reset inputs');
const dotted=score.events.find(e=>e.type==='rest'&&e.duration===1440);assert(dotted);const markup=scoreMarkup();const group=markup.match(new RegExp(`<g class="event" data-id="${dotted.id}">([\\s\\S]*?)</g>`))[1];assert(group.includes('<circle'),'dotted half rest has augmentation dot');
for(const lesson of learning.lessons){ctx.qa.openLesson(lesson);const s=state.score, first=s.measures.find(m=>m.number===lesson.binding.sourceBarStart),last=s.measures.find(m=>m.number===lesson.binding.sourceBarEnd);assert.equal(lesson.sourceEvidence.startTick,first.start,lesson.id);assert.equal(lesson.sourceEvidence.endTick,last.start+last.duration,lesson.id);assert(state.attacks.length>0,lesson.id);assert(state.attacks.every(a=>a.tick>=first.start&&a.tick<last.start+last.duration),lesson.id);}
console.log('QA practice state and real-source dotted-rest checks passed');
