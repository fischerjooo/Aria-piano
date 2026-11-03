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
assert(index>=0,'requires a real rhythm-mapped song');
sandbox.selectLesson(index);
run('screen="studio";studioPhase="practice";mode="touch";progressionWaitMode=false;running=true;pos=0;clearTiming()');
el('allowEarlyNotes').checked=false;
assert.equal(sandbox.songSteadyMode(),true);
const notes=run('lessons[li].seq.slice(0,6)');
sandbox.accept(notes[0],now);
assert.equal(run('pos'),1);
let state=run('timingState');const firstDue=state.due,firstTimer=run('timingDueTimer'),firstStep=state.stepMs;
assert.equal(state.started,now,'first note starts a complete song beat');
assert.equal(state.visualStart,run('scoreLayout(lessons[li])[0].x'));
const lead=run('scoreGuidePosition('+(firstDue-firstStep*.08)+')'),nextX=run('scoreLayout(lessons[li])[1].x');
assert(lead<nextX&&lead>run('scoreLayout(lessons[li])[0].x'),'the guide interpolates continuously');
now=firstDue-firstStep*.08;
sandbox.accept(notes[1],now);
assert.equal(run('pos'),1,'slightly early song notes wait for their written beat rather than jumping forward');
assert.equal(run('timingDueTimer'),firstTimer);
assert.equal(run('pendingEarlyStep.pos'),1);
now=firstDue;fireTimer(firstTimer);
assert.equal(run('pos'),2,'buffered note advances at the written beat, not later');
state=run('timingState');
assert.equal(state.started,firstDue);
assert(Math.abs(state.visualStart-nextX)<.001,'new score animation starts where the previous beat ended');
assert.equal(state.due,firstDue+state.stepMs);
const secondDue=state.due,secondTimer=run('timingDueTimer');
now=secondDue;fireTimer(secondTimer);
assert.equal(run('pos'),2,'the guide allows a small lateness window before auto-skipping a note');
const graceTimer=run('timingDueTimer'),grace=run('songLateGrace(timingState.stepMs)');
assert(graceTimer!==secondTimer&&timers.has(graceTimer));
now=secondDue+grace*.5;sandbox.accept(notes[2],now);
assert.equal(run('pos'),3,'correct late note is accepted without auto-skipping');
assert(!timers.has(graceTimer),'late-note acceptance cancels the pending skip');
state=run('timingState');
assert.equal(state.started,now,'late song note starts a fresh full beat');
assert.equal(state.due,now+state.stepMs,'late chord/onset anchors do not compress the next interval');
const note2X=run('scoreLayout(lessons[li])[2].x');
assert(Math.abs(state.visualStart-note2X)<.001,'late note transition begins at current guide position');
const thirdDue=state.due,thirdTimer=run('timingDueTimer');
now=thirdDue;fireTimer(thirdTimer);
const skippedTimer=run('timingDueTimer');now=thirdDue+run('songLateGrace(timingState.stepMs)')+1;fireTimer(skippedTimer);
assert.equal(run('pos'),4,'unplayed song note still advances once after the grace window');
assert.equal(run('mistakes'),1,'missed note is counted once');
assert(Math.abs(run('timingState.visualStart')-run('scoreLayout(lessons[li])[4].x'))<.001,'auto advance starts at the end of the prior guide, without jumping');
const fourth=run('timingState.stepMs');
now+=20;sandbox.advanceTiming(4,now,now-fourth*5);
assert.equal(run('timingState.due'),now+fourth,'stale chord onset must never cause a zero-duration score jump in steady song mode');
assert.equal(el('scoreSvg').style.transition,'transform '+fourth+'ms linear');
run('progressionWaitMode=true');assert.equal(sandbox.songSteadyMode(),false,'other progression modes are unchanged');
console.log('Steady song guide stays continuous at slightly early/late notes, honors missed-note grace and avoids tempo collapses');
