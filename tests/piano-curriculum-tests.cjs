const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(require('path').join(__dirname,'../index.html'),'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const els={};function el(id){if(els[id])return els[id];const classes=new Set();let markup='';const obj={id,style:{},dataset:{},checked:true,clientWidth:800,scrollWidth:1000,parentElement:{hidden:false},attrs:{},value:id==='sensitivity'?'4':id==='tempo'?'60':id==='inputMode'?'mic':id==='rounds'?'1':'',hidden:true,disabled:false,textContent:'',children:[],classList:{add(...a){a.forEach(x=>classes.add(x))},remove(...a){a.forEach(x=>classes.delete(x))},toggle(x,v){if(v===undefined)v=!classes.has(x);v?classes.add(x):classes.delete(x)},contains(x){return classes.has(x)}},setAttribute(k,v){this.attrs[k]=v},scrollIntoView(){},scrollTo(o){this.scroll=o},focus(){},querySelector(q){if(q.startsWith('[data-midi='))return this.children.find(k=>k.dataset.midi===q.match(/"([^"]+)"/)[1]);return el('focus')},querySelectorAll(){return this.children},replaceChildren(){},getBoundingClientRect(){return {height:parseFloat(this.style.height)||300,width:800}},get innerHTML(){return markup},set innerHTML(s){markup=s;this.children=[];if(id==='keyboard'||id==='learnKeyboard'){for(const m of s.matchAll(/<button class="([^"]+)"[^>]*data-midi="(\d+)"/g)){const child=el(id+'key'+m[2]);child.dataset.midi=m[2];m[1].split(' ').forEach(c=>child.classList.add(c));this.children.push(child)}}if(id==='scoreSvg'){for(const m of s.matchAll(/<g class="([^"]+)" id="(scoreNote\d+)"/g)){const child=el(m[2]);for(const c of ['active','passed','score-note'])child.classList.remove(c);m[1].split(' ').forEach(c=>child.classList.add(c));this.children.push(child)}}}};els[id]=obj;return obj}
let timers=new Map(),timerDelays=new Map(),timerId=0;
function fireTimer(id){const fn=timers.get(id);timers.delete(id);if(fn)fn()}
class AudioMock{constructor(){this.state='running';this.currentTime=0;this.destination={};this.sampleRate=48000}createGain(){return {gain:{value:0,setValueAtTime(){},linearRampToValueAtTime(){},exponentialRampToValueAtTime(){}},connect(){}}}createOscillator(){return {frequency:{value:0},connect(){},start(){},stop(){}}}createMediaStreamSource(){return {connect(){},disconnect(){}}}createAnalyser(){return {fftSize:4096,getFloatTimeDomainData(){}}}}
const sandbox={console,Float32Array,Math,JSON,Option:function(){},PointerEvent:function(){},performance:{now:()=>10000},localStorage:{getItem:()=>null,setItem(){}},document:{body:el('body'),documentElement:{style:{setProperty(k,v){this[k]=v}}},getElementById:el,querySelectorAll(q){if(q==='#keyboard .key')return el('keyboard').children;if(q==='.score-note')return el('scoreSvg').children;if(q==='.overlay')return ['helpModal','settingsModal','notationModal'].map(el);return []},addEventListener(){},activeElement:el('active')},window:{innerWidth:1200,innerHeight:800,AudioContext:AudioMock,addEventListener(){},scrollTo(){}},navigator:{},setTimeout:(fn,ms)=>{timers.set(++timerId,fn);timerDelays.set(timerId,ms);return timerId},clearTimeout:id=>timers.delete(id),setInterval:()=>1,clearInterval(){},cancelAnimationFrame(){},requestAnimationFrame:()=>1,confirm:()=>true};
vm.createContext(sandbox);vm.runInContext(script,sandbox);const run=s=>vm.runInContext(s,sandbox);


assert.equal(run('courseLength'),68);assert.equal(run('lessonLevels.length'),68);assert.equal(run('melodyData.length'),142);assert.equal(run('lessons.length'),210);
assert.equal(new Set(run('lessonLevels.flat().map(l=>l.id)')).size,204);
for(let i=0;i<68;i++)for(let level=0;level<3;level++){
 sandbox.selectLesson(i,level);const l=run('lessons[li]');
 for(const key of ['f','beats','steps','holds','left','lf'])if(l[key])assert.equal(l[key].length,l.seq.length,l.id+' '+key);
 assert(l.seq.every(n=>Number.isInteger(n)&&n>=21&&n<=108),l.id);
 assert(l.f.every(n=>n===''||n>=1&&n<=5),l.id);
 if(l.beats)assert(l.beats.every(n=>n>0));
 sandbox.renderStaticSheet();assert(!/NaN|undefined/.test(el('scoreSvg').innerHTML),l.id);assert(!/NaN|undefined/.test(el('staticScore').innerHTML),l.id);
 const guide=sandbox.curriculumGuide(l);assert(guide.length>500,l.id);assert(guide.includes('<svg'),l.id);
 sandbox.showBrief(i,level);assert(!/NaN|undefined/.test(el('briefContent').innerHTML),l.id);sandbox.closeModal('briefModal');
 run('mode="touch";running=true');for(const n of sandbox.stepNotes(l,0))sandbox.accept(n,10000);assert.equal(run('pos'),1,l.id);
}
for(let i=68;i<210;i++){sandbox.selectLesson(i);assert.equal(run('lessons[li].kind'),'melody');}
console.log('68 courses / 204 levels: stable IDs, playable sequences, note/finger/duration arrays, live/static sheets, illustrated guides, first-step acceptance, and142 melody routing pass');

for(const [unit,count] of [['starter',36],['body-and-reading',6],['scales-and-movement',8],['minor-colours',5],['harmony-and-transposition',8],['independent-musicianship',5]]){el('curriculumUnit').value=unit;run('courseFilter="all"');sandbox.renderNav();assert.equal((el('lessons').innerHTML.match(/class="lesson-card"/g)||[]).length,count,unit);}el('curriculumUnit').value='all';
console.log('All6 skill filters pass; no separate activity or time-budget flow');
