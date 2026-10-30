// Controlled clock integration: only engine logic, not a browser or physical piano.
const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');let now=0;
const els=new Map();function el(id){if(!els.has(id))els.set(id,{value:id==='tempo'?'60':id==='timing'?'timed':'',hidden:false,style:{},innerHTML:'',textContent:'',querySelector:()=>({disabled:false}),click(){this.onclick?.()},addEventListener(){}});return els.get(id)}
let options;const ctx={console,CATALOG:[],LEARNING:{lessons:[]},Date:{now:()=>now},document:{getElementById:el,querySelectorAll:()=>[]},localStorage:{getItem:()=>null,setItem(){}},requestAnimationFrame(){},setTimeout:()=>1,clearTimeout(){},AriaInput:{create:o=>(options=o,{reset(){},bindKeyboard(){}})}};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(path.join(__dirname,'../player.js'),'utf8')+'\nthis.qa={state,selectScore,accept,releaseNote,timedLoop};',ctx);
const {state,selectScore,accept,releaseNote,timedLoop}=ctx.qa;
const note=(id,tick,duration,midi)=>({id,tick,duration,measure:1,staff:'RH',voice:1,type:'note',pitches:[{midi,step:'C',alter:0,octave:4}]});
const s={id:'fake',title:'Test',composer:'Test',scope:'test',key:{fifths:0},meter:{beats:4,beatType:4},measures:[{number:1,start:0,duration:1920}],sections:[],events:[note('a',0,480,60),note('b',480,480,62),note('c',960,480,64)]};
selectScore(s);now=100000;assert.equal(state.anchor,null);assert.equal(state.timers.length,0,'does not start clock before playing');accept(70);assert.equal(state.mistakes,1);assert.equal(state.anchor,null,'wrong note does not start clock');accept(60);assert.equal(state.anchor,now);assert.equal(state.index,1);
now+=200;accept(62);assert.equal(state.index,2);assert.equal(state.anchor,now-1000,'early note moves pulse to new target');
now+=200;releaseNote(62);assert.equal(state.releases,1,'early release recorded');releaseNote(62);assert.equal(state.releases,1,'release counted once');
now+=4000;timedLoop();assert.equal(state.cursor,960,'cursor freezes at overdue target');assert.equal(state.late,1);timedLoop();assert.equal(state.late,1,'late target counted once');accept(64);assert.equal(state.index,3);assert.equal(state.late,1);assert.equal(state.anchor,now-2000,'pulse resumes from frozen target');
now+=900;timedLoop();assert(state.running,'final note and trailing rest must elapse');now+=1101;timedLoop();assert(!state.running,'completion after range end');assert(!el('result').hidden);
options.onNoteOn(21,100,'midi');assert(el('result').hidden&&!el('sheetModal').hidden,'A0 opens sheet');el('closeSheet').click();assert(!el('result').hidden,'closing result sheet returns to result');options.onNoteOn(50,100,'midi');assert(el('result').hidden&&state.index===0&&state.running,'lower MIDI key replays scope');
console.log('QA timed pulse controlled-clock checks passed');
