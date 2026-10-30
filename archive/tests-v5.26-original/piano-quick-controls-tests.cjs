const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(require('path').join(__dirname,'../index.html'),'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const els={};function el(id){if(els[id])return els[id];const classes=new Set();let markup='';const obj={id,style:{},dataset:{},checked:true,clientWidth:800,scrollWidth:1000,parentElement:{hidden:false},attrs:{},value:id==='sensitivity'?'4':id==='tempo'?'60':id==='inputMode'?'mic':id==='rounds'?'1':'',hidden:true,disabled:false,textContent:'',children:[],classList:{add(...a){a.forEach(x=>classes.add(x))},remove(...a){a.forEach(x=>classes.delete(x))},toggle(x,v){if(v===undefined)v=!classes.has(x);v?classes.add(x):classes.delete(x)},contains(x){return classes.has(x)}},setAttribute(k,v){this.attrs[k]=v},scrollIntoView(){},scrollTo(o){this.scroll=o},focus(){},querySelector(q){if(q.startsWith('[data-midi='))return this.children.find(k=>k.dataset.midi===q.match(/"([^"]+)"/)[1]);return el('focus')},querySelectorAll(){return this.children},replaceChildren(){},getBoundingClientRect(){return {height:parseFloat(this.style.height)||300,width:800}},get innerHTML(){return markup},set innerHTML(s){markup=s;this.children=[];if(id==='keyboard'||id==='learnKeyboard'){for(const m of s.matchAll(/<button class="([^"]+)"[^>]*data-midi="(\d+)"/g)){const child=el(id+'key'+m[2]);child.dataset.midi=m[2];m[1].split(' ').forEach(c=>child.classList.add(c));this.children.push(child)}}if(id==='scoreSvg'){for(const m of s.matchAll(/<g class="([^"]+)" id="(scoreNote\d+)"/g)){const child=el(m[2]);for(const c of ['active','passed','score-note'])child.classList.remove(c);m[1].split(' ').forEach(c=>child.classList.add(c));this.children.push(child)}}}};els[id]=obj;return obj}
let timers=new Map(),timerDelays=new Map(),timerId=0;
function fireTimer(id){const fn=timers.get(id);timers.delete(id);if(fn)fn()}
class AudioMock{constructor(){this.state='running';this.currentTime=0;this.destination={};this.sampleRate=48000}createGain(){return {gain:{value:0,setValueAtTime(){},linearRampToValueAtTime(){},exponentialRampToValueAtTime(){}},connect(){}}}createOscillator(){return {frequency:{value:0},connect(){},start(){},stop(){}}}createMediaStreamSource(){return {connect(){},disconnect(){}}}createAnalyser(){return {fftSize:4096,getFloatTimeDomainData(){}}}}
const sandbox={console,Float32Array,Math,JSON,Option:function(){},PointerEvent:function(){},performance:{now:()=>10000},localStorage:{getItem:()=>null,setItem(){}},document:{body:el('body'),documentElement:{style:{setProperty(k,v){this[k]=v}}},getElementById:el,querySelectorAll(q){if(q==='#keyboard .key')return el('keyboard').children;if(q==='.score-note')return el('scoreSvg').children;if(q==='.overlay')return ['helpModal','settingsModal','notationModal'].map(el);return []},addEventListener(){},activeElement:el('active')},window:{innerWidth:1200,innerHeight:800,AudioContext:AudioMock,addEventListener(){},scrollTo(){}},navigator:{},setTimeout:(fn,ms)=>{timers.set(++timerId,fn);timerDelays.set(timerId,ms);return timerId},clearTimeout:id=>timers.delete(id),setInterval:()=>1,clearInterval(){},cancelAnimationFrame(){},requestAnimationFrame:()=>1,confirm:()=>true};
vm.createContext(sandbox);vm.runInContext(script,sandbox);const run=s=>vm.runInContext(s,sandbox);







(async()=>{
 sandbox.selectLesson(0);run('screen="studio";mode="touch";studioPhase="practice";running=true;pos=1');
 sandbox.openQuickMenu('tempo');assert.equal(run('running'),false);assert.equal(el('quickTempoModal').hidden,false);
 sandbox.chooseQuickTempo(50);await Promise.resolve();await Promise.resolve();
 assert.equal(+el('tempo').value,40);assert.equal(el('quickTempoModal').hidden,true);assert.equal(run('running'),true);assert.equal(run('pos'),1);
 sandbox.openQuickMenu('tempo');sandbox.chooseQuickTempo(0);await Promise.resolve();await Promise.resolve();assert.equal(sandbox.timingEnabled(),false);assert.equal(el('quickTempoLabel').textContent,'Wait');
 sandbox.openQuickMenu('tempo');sandbox.chooseQuickTempo(100);await Promise.resolve();await Promise.resolve();assert.equal(+el('tempo').value,80);assert.equal(sandbox.timingEnabled(),true);
 const index=run('lessons.findIndex(l=>l.left)');assert(index>=0);sandbox.selectLesson(index);run('screen="studio";mode="touch";studioPhase="practice";running=true;pos=3');
 sandbox.openQuickMenu('hands');assert.equal(el('quickHandLeft').disabled,false);sandbox.chooseQuickHand('left');await Promise.resolve();await Promise.resolve();
 assert.equal(run('practiceHand'),'left');assert.equal(run('pos'),0);assert.equal(run('running'),true);assert.equal(run('stepNotes(lessons[li],0).length'),1);
 sandbox.selectLesson(0);sandbox.openQuickMenu('hands');assert.equal(el('quickHandLeft').disabled,true);assert.equal(el('quickHandBoth').disabled,true);assert.equal(el('quickHandRight').disabled,false);
 sandbox.closeModal('quickHandsModal');assert.equal(run('running'),false,'previously paused practice remains paused');
 sandbox.selectLesson(0);run('screen="studio";mode="touch";demoing=true;demoIndex=2');sandbox.openQuickMenu('tempo');assert.equal(el('quickTempo').attrs['aria-expanded'],'true');sandbox.chooseQuickTempo(75);await Promise.resolve();await Promise.resolve();assert.equal(run('demoing'),true);assert.equal(run('demoIndex'),2);assert.equal(el('quickTempo').attrs['aria-expanded'],'false');sandbox.stopDemo();
 sandbox.selectLesson(run('courseLength'));const melodyDock=sandbox.viewportMetrics().dock;sandbox.selectLesson(0);assert(sandbox.viewportMetrics().dock>melodyDock);
 console.log('Example resumes at current note; melody dock removes unused row; Tempo presets, wait mode, automatic resume, position preservation, hand reset/filtering and single-hand guards pass');
})().catch(e=>{console.error(e);process.exitCode=1});
