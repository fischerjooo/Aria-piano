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
 assert.equal(+el('tempo').value,40);assert.equal(el('quickTempoModal').hidden,false,'tempo choices do not dismiss the menu');assert.equal(run('running'),false,'practice stays paused while choosing');assert.equal(run('pos'),1);
 assert.equal(el('quickSpeed50').attrs['aria-pressed'],'true');sandbox.chooseQuickTempo(75);assert.equal(el('quickSpeed75').attrs['aria-pressed'],'true');assert.equal(el('quickSpeed50').attrs['aria-pressed'],'false');assert.equal(el('quickTempoModal').hidden,false);
 sandbox.closeModal('quickTempoModal');await Promise.resolve();await Promise.resolve();assert.equal(run('running'),true);assert.equal(run('pos'),1);
 sandbox.openQuickMenu('tempo');assert.equal(sandbox.waitModeEnabled(),true);assert.equal(sandbox.quickModeEnabled(),true);sandbox.toggleQuickWait();assert.equal(sandbox.waitModeEnabled(),false);assert.equal(sandbox.timingEnabled(),true);assert.equal(el('quickTempoLabel').textContent,'60 BPM');sandbox.toggleQuickMode();assert.equal(sandbox.quickModeEnabled(),false);sandbox.closeModal('quickTempoModal');await Promise.resolve();await Promise.resolve();
 sandbox.openQuickMenu('tempo');sandbox.chooseQuickTempo(100);assert.equal(el('quickTempoModal').hidden,false);sandbox.closeModal('quickTempoModal');await Promise.resolve();await Promise.resolve();assert.equal(+el('tempo').value,80);assert.equal(sandbox.timingEnabled(),true);
 const index=run('lessons.findIndex(l=>l.left)');assert(index>=0);sandbox.selectLesson(index);run('screen="studio";mode="touch";studioPhase="practice";running=true;pos=3');
 sandbox.openQuickMenu('hands');assert.equal(el('quickHandLeft').disabled,false);sandbox.chooseQuickHand('left');await Promise.resolve();await Promise.resolve();
 assert.equal(run('practiceHand'),'left');assert.equal(run('pos'),0);assert.equal(run('running'),false,'hand choices remain paused until the menu is closed');assert.equal(el('quickHandsModal').hidden,false);assert.equal(el('quickHandLeft').attrs['aria-pressed'],'true');assert.equal(el('quickHandRight').attrs['aria-pressed'],'false');
 sandbox.chooseQuickHand('right');assert.equal(el('quickHandsModal').hidden,false);assert.equal(el('quickHandRight').attrs['aria-pressed'],'true');sandbox.chooseQuickHand('left');assert.equal(el('quickHandLeft').attrs['aria-pressed'],'true');sandbox.closeModal('quickHandsModal');await Promise.resolve();await Promise.resolve();
 assert.equal(run('running'),true);assert.equal(run('stepNotes(lessons[li],0).length'),1);
 sandbox.selectLesson(0);sandbox.openQuickMenu('hands');assert.equal(el('quickHandLeft').disabled,true);assert.equal(el('quickHandBoth').disabled,true);assert.equal(el('quickHandRight').disabled,false);
 sandbox.closeModal('quickHandsModal');assert.equal(run('running'),false,'previously paused practice remains paused');
 sandbox.selectLesson(0);run('screen="studio";mode="touch";demoing=true;demoIndex=2');sandbox.openQuickMenu('tempo');assert.equal(el('quickTempo').attrs['aria-expanded'],'true');sandbox.chooseQuickTempo(75);assert.equal(el('quickTempoModal').hidden,false);assert.equal(run('demoing'),false,'demo waits while menu remains open');sandbox.closeModal('quickTempoModal');await Promise.resolve();await Promise.resolve();assert.equal(run('demoing'),true);assert.equal(run('demoIndex'),2);assert.equal(el('quickTempo').attrs['aria-expanded'],'false');sandbox.stopDemo();
 sandbox.selectLesson(run('courseLength'));const melodyDock=sandbox.viewportMetrics().dock;sandbox.selectLesson(0);const lessonDock=sandbox.viewportMetrics().dock;assert(lessonDock>=melodyDock,'songs must reserve at least as much dock height as lessons when extra controls are present');

 // Custom range must include 10% without clamping up to 20 BPM and preserve the chosen mode.
 sandbox.selectLesson(0);sandbox.openQuickMenu('tempo');el('quickCustomSpeed').oninput({target:{value:'10'}});
 assert.equal(el('quickCustomSpeedValue').textContent,'10%');
 el('quickCustomSpeed').onchange({target:{value:'10'}});await Promise.resolve();await Promise.resolve();
 assert.equal(+el('tempo').value,Math.round(run('normalTempo(lessons[li])')*.1));
 assert.equal(el('quickTempoModal').hidden,false);assert.equal(el('quickSpeedCustom').attrs['aria-pressed'],'true');
 sandbox.chooseQuickTempo(50);assert.equal(el('quickTempoModal').hidden,false);assert.equal(el('quickSpeed50').attrs['aria-pressed'],'true');
 assert.equal(+el('tempo').value,Math.round(run('normalTempo(lessons[li])')*.5));sandbox.closeModal('quickTempoModal');await Promise.resolve();await Promise.resolve();
 // Playing on tempo must never increase quick-follow playback rate.
 el('allowEarlyNotes').checked=true;assert.equal(sandbox.quickModeEnabled(),true,'enable Quick mode for the follower tests');
 sandbox.selectLesson(0);run('mode="touch";running=true;pos=1;stopQuickFollow()');sandbox.startQuickFollow(0);
 for(let i=0;i<35;i++)sandbox.tickQuickFollow(2000+i*16.67);
 assert.equal(run('quickFollowRate'),1,'normal tempo keeps the guide at exactly 1x');
 assert.equal(run('quickFollowDebt'),0,'normal tempo creates no catch-up debt');
 // A real player lead should accelerate smoothly, then pay down the distance.
 sandbox.stopQuickFollow();run('running=true;pos=1;quickFollowX=scoreLayout(lessons[li])[0].x-(scoreLayout(lessons[li])[1].x-scoreLayout(lessons[li])[0].x)*.8');
 sandbox.startQuickFollow(0);const initialDebt=run('quickFollowDebt');assert(initialDebt>0);
 let peakCatchupRate=1;
 for(let i=0;i<14;i++){sandbox.tickQuickFollow(4000+i*16.67);peakCatchupRate=Math.max(peakCatchupRate,run('quickFollowRate'));}
 assert(peakCatchupRate>1.025,'significant lead must still trigger a gentle catch-up');
 assert(peakCatchupRate<1.45,'speed increase must ramp gradually, not jump at the first detected lead');
 assert(run('quickFollowDebt')<initialDebt,'catch-up debt must decay rather than perpetually speeding up');
 // Even with outstanding lead, start easing off well before the target note.
 const gap=run('scoreLayout(lessons[li])[1].x-scoreLayout(lessons[li])[0].x'),target=run('scoreLayout(lessons[li])[1].x');
 run('quickFollowX='+String(target-gap*.6)+';quickFollowDebt='+String(gap*.7)+';quickFollowRate=1.6;quickFollowLast=6000');
 sandbox.tickQuickFollow(6016.67);assert(run('quickFollowRate')<1.6,'follower must brake while lead still exists and target is approaching');
 assert(run('quickFollowRate')>1,'braking must not go below the configured tempo');
 run('quickFollowX='+String(target-gap*.06)+';quickFollowDebt='+String(gap*.2)+';quickFollowRate=1.3;quickFollowLast=7000');
 sandbox.tickQuickFollow(7016.67);
 assert(run('quickFollowRate')<=1.005,'follower must return to the configured tempo just before catch-up');
 assert(run('quickFollowRate')>=1,'the configured tempo is the lower bound while following');
 console.log('Quick mode eases into real lead, brakes early and returns to selected 1x tempo; tempo presets, custom range and menu controls pass');
})().catch(e=>{console.error(e);process.exitCode=1});
