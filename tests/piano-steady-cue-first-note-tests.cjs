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
sandbox.selectLesson(0);run('mode="touch";screen="studio";studioPhase="practice";running=false;progressionWaitMode=false;clearTiming();pos=0');
el('allowEarlyNotes').checked=false;
run('lessons[li]={...lessons[li],seq:[60,62,64,65,67],f:[1,2,3,4,5],beats:[1,1,1,1,1],steps:[1,1,1,1,1],holds:[1,1,1,1,1]}');
sandbox.renderNotes();sandbox.startPractice();
assert.equal(run('steadyClock'),null);assert.equal(run('timingDueTimer'),null);
now=12000;sandbox.accept(62,now);assert.equal(run('steadyClock'),null);assert.equal(run('pos'),0);
now=15000;sandbox.accept(60,now);assert.equal(run('pos'),1);assert.equal(run('steadyClock.started'),15000);
assert.equal(run('steadyCueIndex(15000)'),1);assert(el('scoreNote1').classList.contains('active'),'next note highlights immediately');assert(el('scoreNote0').classList.contains('passed'));
const clock=run('steadyClock'),due=run('timingState.due');
now=15020;sandbox.accept(64,now);assert.equal(run('pos'),1);assert.equal(run('pendingEarlyStep'),null,'two-ahead note never buffered');
now=15200;sandbox.accept(62,now);assert.equal(run('pos'),1);assert.equal(run('pendingEarlyStep.pos'),1);
now=15300;sandbox.accept(64,now);assert.equal(run('pos'),1);assert.equal(run('pendingEarlyStep.pos'),1);assert.equal(run('steadyClock'),clock);
now=due;fireTimer(run('timingDueTimer'));assert.equal(run('pos'),2);assert.equal(run('steadyClock'),clock);assert.equal(run('steadyCueIndex('+(due+1)+')'),2);assert(el('scoreNote2').classList.contains('active'));
const due2=run('timingState.due');now=due2;fireTimer(run('timingDueTimer'));assert.equal(run('pos'),2);
sandbox.tickSteadyClock(due2+50);assert(el('scoreNote3').classList.contains('active'),'cue advances regardless of late grace');assert(!el('scoreNote2').classList.contains('active'));assert.equal(run('pos'),2);
now=due2+500;fireTimer(run('timingDueTimer'));assert.equal(run('pos'),3);assert.equal(run('steadyClock'),clock);
sandbox.seekLesson(2);assert.equal(run('pos'),2);assert.equal(run('steadyClock'),null);assert.equal(run('timingState'),null);assert(el('scoreNote2').classList.contains('active'));
now=19000;sandbox.accept(64,now);assert.equal(run('pos'),3);assert.equal(run('steadyClock.first'),2);assert.equal(run('steadyClock.started'),19000);assert(el('scoreNote3').classList.contains('active'));
sandbox.stopRun();assert.equal(run('steadyClock'),null);
console.log('Steady mode cue leads by one note; only direct next input can be buffered; first and seek require real note');
