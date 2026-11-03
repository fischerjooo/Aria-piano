const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(require('path').join(__dirname,'../index.html'),'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const els={};function el(id){if(els[id])return els[id];const classes=new Set();let markup='';const obj={id,style:{},dataset:{},checked:true,clientWidth:800,scrollWidth:1000,parentElement:{hidden:false},attrs:{},value:id==='sensitivity'?'4':id==='tempo'?'60':id==='inputMode'?'mic':id==='rounds'?'1':'',hidden:true,disabled:false,textContent:'',children:[],classList:{add(...a){a.forEach(x=>classes.add(x))},remove(...a){a.forEach(x=>classes.delete(x))},toggle(x,v){if(v===undefined)v=!classes.has(x);v?classes.add(x):classes.delete(x)},contains(x){return classes.has(x)}},setAttribute(k,v){this.attrs[k]=v},scrollIntoView(){},scrollTo(o){this.scroll=o},focus(){},querySelector(q){if(q.startsWith('[data-midi='))return this.children.find(k=>k.dataset.midi===q.match(/"([^"]+)"/)[1]);return el('focus')},querySelectorAll(){return this.children},replaceChildren(){},getBoundingClientRect(){return {height:parseFloat(this.style.height)||300,width:800}},get innerHTML(){return markup},set innerHTML(s){markup=s;this.children=[];if(id==='keyboard'||id==='learnKeyboard'){for(const m of s.matchAll(/<button class="([^"]+)"[^>]*data-midi="(\d+)"/g)){const child=el(id+'key'+m[2]);child.dataset.midi=m[2];m[1].split(' ').forEach(c=>child.classList.add(c));this.children.push(child)}}if(id==='scoreSvg'){for(const m of s.matchAll(/<g class="([^"]+)" id="(scoreNote\d+)"/g)){const child=el(m[2]);for(const c of ['active','passed','score-note'])child.classList.remove(c);m[1].split(' ').forEach(c=>child.classList.add(c));this.children.push(child)}}}};els[id]=obj;return obj}
let timers=new Map(),timerDelays=new Map(),timerId=0;
function fireTimer(id){const fn=timers.get(id);timers.delete(id);if(fn)fn()}
class AudioMock{constructor(){this.state='running';this.currentTime=0;this.destination={};this.sampleRate=48000}createGain(){return {gain:{value:0,setValueAtTime(){},linearRampToValueAtTime(){},exponentialRampToValueAtTime(){}},connect(){}}}createOscillator(){return {frequency:{value:0},connect(){},start(){},stop(){}}}createMediaStreamSource(){return {connect(){},disconnect(){}}}createAnalyser(){return {fftSize:4096,getFloatTimeDomainData(){}}}}
const sandbox={console,Float32Array,Math,JSON,Option:function(){},PointerEvent:function(){},performance:{now:()=>10000},localStorage:{getItem:()=>null,setItem(){}},document:{body:el('body'),documentElement:{style:{setProperty(k,v){this[k]=v}}},getElementById:el,querySelectorAll(q){if(q==='#keyboard .key')return el('keyboard').children;if(q==='.score-note')return el('scoreSvg').children;if(q==='.overlay')return ['helpModal','settingsModal','notationModal'].map(el);return []},addEventListener(){},activeElement:el('active')},window:{innerWidth:1200,innerHeight:800,AudioContext:AudioMock,addEventListener(){},scrollTo(){}},navigator:{},setTimeout:(fn,ms)=>{timers.set(++timerId,fn);timerDelays.set(timerId,ms);return timerId},clearTimeout:id=>timers.delete(id),setInterval:()=>1,clearInterval(){},cancelAnimationFrame(){},requestAnimationFrame:()=>1,confirm:()=>true};
vm.createContext(sandbox);vm.runInContext(script,sandbox);const run=s=>vm.runInContext(s,sandbox);








let now=10000;sandbox.performance.now=()=>now;
const index=run('lessons.findIndex(l=>(l.kind==="melody"||l.application)&&l.rhythmReady&&l.seq.length>=6)');
assert(index>=0,'requires a real rhythm-mapped song');sandbox.selectLesson(index);
run('screen="studio";studioPhase="practice";mode="touch";progressionWaitMode=false;running=false;pos=0;clearTiming()');
el('allowEarlyNotes').checked=false;assert.equal(sandbox.songSteadyMode(),true);
const notes=run('lessons[li].seq.slice(0,6)');
sandbox.startPractice();assert.equal(run('steadyClock'),null,'song waits indefinitely at first note');assert.equal(run('timingDueTimer'),null);
now=10050;sandbox.accept(notes[0],now);assert.equal(run('pos'),1);
let state=run('timingState'),firstDue=state.due,firstTimer=run('timingDueTimer'),firstStep=state.stepMs;
assert.equal(state.started,now);assert.equal(run('steadyClock.started'),now);
const clock=run('steadyClock'),firstX=run('scoreLayout(lessons[li])[0].x'),nextX=run('scoreLayout(lessons[li])[1].x');
assert.equal(run('steadyCueIndex('+(now+1)+')'),1,'next note highlighted one beat ahead');
assert(el('scoreNote1').classList.contains('active'),'next note highlighted immediately on first onset');
const halfway=run('steadyPosition('+(now+firstStep*.5)+')');
assert(halfway>firstX&&halfway<nextX,'continuous guide moves between notes independently of scoring');
now=firstDue-firstStep*.08;sandbox.accept(notes[1],now);
assert.equal(run('pos'),1,'early direct-next note is buffered instead of jumping');
assert.equal(run('timingDueTimer'),firstTimer);assert.equal(run('pendingEarlyStep.pos'),1);
now=firstDue;fireTimer(firstTimer);assert.equal(run('pos'),2);assert.equal(run('steadyClock'),clock);
state=run('timingState');assert.equal(state.started,firstDue-firstStep);assert.equal(state.due,firstDue+state.stepMs);
assert.equal(run('steadyCueIndex('+(firstDue+1)+')'),2);
const secondDue=state.due,secondTimer=run('timingDueTimer');
now=secondDue;fireTimer(secondTimer);assert.equal(run('pos'),2,'late note grace does not skip immediately');
const graceTimer=run('timingDueTimer'),grace=run('songLateGrace(timingState.stepMs)');
assert(graceTimer!==secondTimer&&timers.has(graceTimer));
assert.equal(run('steadyCueIndex('+(secondDue+grace*.5)+')'),3,'highlight moves ahead while scoring still in grace');
now=secondDue+grace*.5;sandbox.accept(notes[2],now);assert.equal(run('pos'),3,'late correct note is accepted');
assert(!timers.has(graceTimer));assert.equal(run('steadyClock'),clock,'late notes never restart the guide');
state=run('timingState');assert.equal(state.started,secondDue);assert.equal(state.due,secondDue+state.stepMs,'late note does not compress next beat');
const thirdDue=state.due,thirdTimer=run('timingDueTimer');now=thirdDue;fireTimer(thirdTimer);
const skippedTimer=run('timingDueTimer');now=thirdDue+run('songLateGrace(timingState.stepMs)')+1;fireTimer(skippedTimer);
assert.equal(run('pos'),4);assert.equal(run('mistakes'),1);assert.equal(run('steadyClock'),clock);
state=run('timingState');assert.equal(state.due,thirdDue+state.stepMs);
now+=20;sandbox.advanceTiming(4,now,now-state.stepMs*5);
assert.equal(run('timingState.due'),thirdDue+state.stepMs,'legacy late onset cannot reset the fixed beat');
assert.equal(run('steadyClock'),clock);
sandbox.stopRun();run('progressionWaitMode=true');assert.equal(sandbox.songSteadyMode(),false);
console.log('Steady song starts on first note, highlights next beat early, buffers early input, and never resets for late/missed notes');
