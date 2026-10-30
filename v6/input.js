/* Aria input adapters. Hardware APIs are optional; only fresh attacks are emitted.
 * Microphone is monophonic and never infers an expected pitch or octave. */
(function(root){
'use strict';
const BLE_SERVICE='03b80e5a-ede8-4b33-a751-6ce34ec4c700',BLE_CHARACTERISTIC='7772e5db-3868-4112-a1a9-f2669d106bf3';
let pitchWorkspace;
function detectPitch(buf,sr){let energy=0,mean=0;for(let i=0;i<buf.length;i++)mean+=buf[i];mean/=buf.length;for(let i=0;i<buf.length;i++)energy+=(buf[i]-mean)**2;const rms=Math.sqrt(energy/buf.length);if(rms<.0005)return{freq:0,rms,confidence:0};
const stride=Math.max(1,Math.floor(sr/11000)),rate=sr/stride,n=Math.floor(buf.length/stride);if(!pitchWorkspace)pitchWorkspace=new Map();let workspace=pitchWorkspace.get(n);if(!workspace){const window=new Float32Array(n);let sum=0;for(let i=0;i<n;i++){window[i]=.5-.5*Math.cos(2*Math.PI*i/(n-1));sum+=window[i]}workspace={n,x:new Float32Array(n),diff:new Float32Array(Math.floor(n/2)+3),window,windowSum:sum};if(pitchWorkspace.size>=4)pitchWorkspace.clear();pitchWorkspace.set(n,workspace)}const x=workspace.x;for(let i=0;i<n;i++){let v=0;for(let k=0;k<stride;k++)v+=buf[i*stride+k]-mean;x[i]=v/stride}const min=Math.max(2,Math.floor(rate/1100)),max=Math.min(Math.ceil(rate/75),Math.floor(n/2)-2),half=Math.floor(n/2),diff=workspace.diff;let sum=0;for(let lag=1;lag<=max+1;lag++){let d=0;for(let j=0;j<half;j++){const delta=x[j]-x[j+lag];d+=delta*delta}sum+=d;diff[lag]=sum?d*lag/sum:1}
function valley(t){const a=diff[t-1],b=diff[t],c=diff[t+1],den=2*(a-2*b+c),shift=den?Math.max(-.5,Math.min(.5,(a-c)/den)):0;return{lag:t+shift,error:Math.max(0,b-(a-c)*shift/4)}}
const candidates=[];for(let t=min;t<max;t++)if(diff[t]<diff[t-1]&&diff[t]<=diff[t+1]&&diff[t]<.2)candidates.push(valley(t));if(!candidates.length)return{freq:0,rms,confidence:0};let best=candidates[0];
function bandPower(f){const coefficient=2*Math.cos(2*Math.PI*f/rate);let q1=0,q2=0;for(let i=0;i<n;i++){const q=x[i]*workspace.window[i]+coefficient*q1-q2;q2=q1;q1=q}return 2*(q1*q1+q2*q2-coefficient*q1*q2)/(workspace.windowSum*workspace.windowSum)}
let octaveAdjusted=false;for(let pass=0;pass<2;pass++){const lower=candidates.find(c=>Math.abs(c.lag/best.lag-2)<.06);if(!lower||lower.error>=best.error*.55||best.error-lower.error<.002)break;const f=rate/lower.lag,required=rms*rms*.0015;let odd=bandPower(f);if(odd<required)odd+=bandPower(f*3);if(odd<required)odd+=bandPower(f*5);if(odd<required)break;best=lower;octaveAdjusted=true}
return{freq:rate/best.lag,rms,confidence:1-best.error,octaveAdjusted};}
function createAttackTracker(){return{time:null,id:0,event:null,rms:0,high:0,initialised:false,lastOnset:-Infinity,fall:0,previous:0,previousHigh:0}}
function trackAttack(state,buf,sr,now,gate){const elapsed=state.time===null?16:Math.min(90,Math.max(0,now-state.time));state.time=now;const count=Math.min(buf.length,Math.round(sr*elapsed/1000)),windowSize=Math.max(64,Math.round(sr*.008));for(let start=buf.length-count;start+windowSize<=buf.length;start+=windowSize){let energy=0,highEnergy=0;for(let j=start;j<start+windowSize;j++){const v=buf[j],delta=v-(j?buf[j-1]:v);energy+=v*v;highEnergy+=delta*delta}const rms=Math.sqrt(energy/windowSize),high=Math.sqrt(highEnergy/windowSize),t=now-(buf.length-start-windowSize)/sr*1000;if(!state.initialised){state.rms=rms;state.high=high;state.initialised=true;state.previous=rms;state.previousHigh=high;continue}if(rms<state.previous*.99)state.fall++;const base=Math.max(state.rms,gate*.5,.0003),baseHigh=Math.max(state.high,.00001),energyRise=rms/base,highRise=high/baseHigh,brightness=(high/Math.max(rms,.0001))/(baseHigh/base);const newAttack=high/Math.max(rms,.0001)<.42&&rms>gate*1.5&&high/Math.max(rms,.0001)<.35&&((energyRise>.8&&highRise>1.55&&brightness>1.6)||(energyRise>1.18&&highRise>1.65&&brightness>1.2))&&t-state.lastOnset>=100&&(state.fall>=2||state.rms<gate);
if(newAttack){state.id++;state.event={id:state.id,time:t,beforeRms:state.previous,beforeHigh:state.previousHigh,tailHigh:high};state.lastOnset=t;state.fall=0}if(state.event)state.event.tailHigh=high;state.rms=.84*state.rms+.16*rms;state.high=.84*state.high+.16*high;state.previous=rms;state.previousHigh=high;}return state.event;}
function createMicTracker(on,off,options={}){
 const gate=options.gate||.003;let attack,used,candidate,note,since,held,quiet,released,envelope,lastEnvelope,envelopeEvent;
 function reset(){attack=createAttackTracker();used=0;candidate=null;note=null;since=0;held=null;quiet=null;released=true;envelope=0;lastEnvelope=-Infinity;envelopeEvent=null}
 function release(){if(held!==null)off(held);held=null}
 reset();
 function process(frame,rate,now){
  const pitch=detectPitch(frame,rate),strike=trackAttack(attack,frame,rate,now,gate);
  // Compare a short tail window with the decaying envelope. This detects a
  // same-pitch re-strike while the earlier piano note is still ringing.
  const tail=frame.subarray(Math.max(0,frame.length-Math.round(rate*.032)));
  let tailEnergy=0;for(const x of tail)tailEnergy+=x*x;
  const tailRms=Math.sqrt(tailEnergy/tail.length);
  if(envelope>gate&&tailRms>Math.max(gate*2,envelope*1.7)&&now-lastEnvelope>180){envelopeEvent={id:'envelope:'+now,time:now};lastEnvelope=now}
  envelope=envelope ? .85*envelope+.15*tailRms : tailRms;
  if(pitch.rms<Math.min(gate*.25,.0005)){if(quiet===null)quiet=now;if(now-quiet>=70){release();released=true;note=null;used=attack.id}candidate=null;return pitch}
  quiet=null;
  if(!pitch.freq||pitch.confidence<.88){note=null;return pitch}
  const raw=69+12*Math.log2(pitch.freq/(options.tuning||440)),m=Math.round(raw);
  if(m<21||m>108||Math.abs(raw-m)*100>45){note=null;return pitch}
  if(note!==m){note=m;since=now}
  // Require stable pitch after an envelope attack; estimator changes alone never
  // re-trigger the same held note. A sustained pitch change is a legato onset.
  const event=envelopeEvent&&now-envelopeEvent.time<220?envelopeEvent:strike;
  const fresh=!!event&&(event===envelopeEvent||event.id>used)&&now-event.time>=35&&now-event.time<260;
  if(fresh&&(!candidate||candidate.id!==event.id||candidate.m!==m))candidate={id:event.id,m,since:now};
  const retrigger=fresh&&candidate?.m===m&&now-candidate.since>=28;
  if(now-since>=65&&(released||held!==m||retrigger)){
   release();held=m;released=false;used=attack.id;envelopeEvent=null;candidate=null;on(m,Math.max(1,Math.min(127,Math.round(pitch.rms*1000))));
  }
  return pitch;
 }
 return{process,reset:()=>{release();reset()}};
}
// BLE-MIDI packets have a header followed by timestamp/status/data groups.
function createBLEDecoder(emit){let running=0;return{reset(){running=0},decode(value){
 const b=new Uint8Array(value.buffer,value.byteOffset,value.byteLength);if(b.length<3||!(b[0]&128))return;
 let i=1,status=0;while(i<b.length){if(b[i]&128)i++;if(i>=b.length)break;
 if(b[i]&128){status=b[i++];if(status>=0xf8)continue;if(status>=0xf0){running=0;return}running=status}else status=status||running;
 if(status<128||status>=240)return;const count=(status&0xe0)===0xc0?1:2,data=[];
 while(i<b.length&&data.length<count){const v=b[i++];if(v>=248)continue;if(v&128)return;data.push(v)}
 if(data.length!==count)return;emit(status,data[0],data[1]||0);
 }}}}
function create(options={}){
 const env=options.environment||root,nav=env.navigator||{},doc=env.document;
 const on=options.onNoteOn||(()=>{}),off=options.onNoteOff||(()=>{}),status=options.onStatus||(()=>{});
 let mode='touch',dead=false,epoch=0,access=null,device=null,characteristic=null,stream=null,source=null,raf=null,ctx=null,pending=false;
 const held=new Map(),pointers=new Map(),bindings=[],ports=new Map();
 const clock=()=>env.performance?.now()||Date.now();
 function down(m,v,s,key){if(dead||mode!==s||doc?.hidden||!Number.isInteger(m)||m<21||m>108||held.has(key))return;held.set(key,{m,s});on(m,v,s)}
 function up(key){const h=held.get(key);if(!h)return;held.delete(key);if(![...held.values()].some(x=>x.m===h.m&&x.s===h.s))off(h.m,h.s)}
 function reset(){for(const key of [...held.keys()])up(key);for(const [id,p]of pointers){p.key.classList?.remove('held');try{p.key.releasePointerCapture?.(id)}catch(e){}}pointers.clear();micTracker.reset();decoder.reset()}
 function stopMic(){if(raf!==null)env.cancelAnimationFrame?.(raf);raf=null;stream?.getTracks().forEach(t=>t.stop());stream=null;source?.disconnect();source=null;micTracker.reset()}
 function selectMode(next){if(!['touch','midi','ble','mic'].includes(next))return false;if(mode===next)return true;++epoch;pending=false;reset();stopMic();mode=next;options.onMode?.(mode);return true}
 function receive(s,key,statusByte,n,v){const channel=statusByte&15,type=statusByte&240,k=s+':'+key+':'+channel+':'+n;
  if(type===128||type===144&&!v){up(k);return}
  if(type===176&&(n===120||n===123)){for(const id of [...held.keys()])if(id.startsWith(s+':'+key+':'+channel+':'))up(id);return}
  if(type===144&&v)down(n,v,s,k);
 }
 const decoder=createBLEDecoder((s,n,v)=>receive('ble','piano',s,n,v));
 const notification=e=>decoder.decode(e.target.value);
 const micTracker=createMicTracker((m,v)=>{if(micAllowed()===true)down(m,v,'mic','mic:'+m)},m=>up('mic:'+m),options.microphone);
 function micAllowed(){const value=options.canUseMic?.();return value===undefined||value===true?true:(typeof value==='string'?value:'Choose a single monophonic hand or voice for microphone practice.')}
 function listen(target,event,fn){target?.addEventListener?.(event,fn);bindings.push(()=>target?.removeEventListener?.(event,fn))}
 function bindKeyboard(element){
  listen(element,'pointerdown',e=>{const key=e.target.closest?.('[data-midi]');if(!key||e.button>0||mode!=='touch')return;e.preventDefault();if(pointers.has(e.pointerId))return;const m=+key.dataset.midi;
   if([...pointers.values()].some(p=>p.m===m))return;
   pointers.set(e.pointerId,{key,m});key.classList?.add('held');try{key.setPointerCapture?.(e.pointerId)}catch(e){}down(m,96,'touch','touch:'+e.pointerId);
  });
  const end=e=>{const p=pointers.get(e.pointerId);if(!p)return;pointers.delete(e.pointerId);p.key.classList?.remove('held');up('touch:'+e.pointerId)};
  for(const event of ['pointerup','pointercancel','lostpointercapture'])listen(element,event,end);
  // Assistive technology activates buttons without pointer events.
  listen(element,'click',e=>{if(e.detail!==0||mode!=='touch')return;const key=e.target.closest?.('[data-midi]');if(!key)return;const id='accessible:'+key.dataset.midi;down(+key.dataset.midi,96,'touch',id);up(id)});
  return reset;
 }
 function unbindMidi(){if(access)access.onstatechange=null;for(const p of ports.values())p.onmidimessage=null;ports.clear();access=null}
 function bindMidiPorts(){for(const [id,p]of ports)if(!access.inputs.has(id)||p.state==='disconnected'){p.onmidimessage=null;ports.delete(id);for(const key of [...held.keys()])if(key.startsWith('midi:'+id+':'))up(key)}for(const p of access.inputs.values()){if(p.state==='disconnected')continue;ports.set(p.id,p);p.onmidimessage=e=>receive('midi',p.id,...e.data)}status(ports.size?'Web MIDI ready. Play your piano.':'Web MIDI enabled. Connect a MIDI piano.')}
 async function connectMidi(){if(dead)return false;selectMode('midi');if(!nav.requestMIDIAccess){status('Web MIDI is unavailable in this browser.');return false}const token=++epoch;try{const a=await nav.requestMIDIAccess({sysex:false});if(dead||token!==epoch)return false;unbindMidi();access=a;bindMidiPorts();a.onstatechange=bindMidiPorts;return true}catch(e){if(token===epoch)status('MIDI access failed: '+e.message);return false}}
 function detachBluetooth(){characteristic?.removeEventListener('characteristicvaluechanged',notification);if(characteristic?.stopNotifications)Promise.resolve(characteristic.stopNotifications()).catch(()=>{});characteristic=null;device?.removeEventListener('gattserverdisconnected',bleLost);device?.gatt?.disconnect();device=null;decoder.reset();for(const key of [...held.keys()])if(key.startsWith('ble:'))up(key)}
 function bleLost(){detachBluetooth();if(mode==='ble')status('Piano disconnected. Connect your piano to continue.');options.onDisconnect?.('ble')}
 async function connectBluetooth(){
  if(dead||pending)return false;selectMode('ble');if(!nav.bluetooth?.requestDevice||env.isSecureContext===false){status('Bluetooth MIDI needs a supported browser and a secure page. Use Web MIDI or touch input.');return false}
  const token=++epoch;pending=true;let d,c;
  try{
   // Call the chooser before awaiting anything to preserve the user's gesture.
   const request=nav.bluetooth.requestDevice({filters:[{services:[BLE_SERVICE]},{namePrefix:'YDP'}],optionalServices:[BLE_SERVICE]});
   d=await request;if(dead||token!==epoch){d.gatt?.disconnect();return false}detachBluetooth();device=d;d.addEventListener('gattserverdisconnected',bleLost);
   const server=await d.gatt.connect(),service=await server.getPrimaryService(BLE_SERVICE);c=await service.getCharacteristic(BLE_CHARACTERISTIC);
   if(dead||token!==epoch){d.gatt?.disconnect();return false}characteristic=c;c.addEventListener('characteristicvaluechanged',notification);await c.startNotifications();
   if(dead||token!==epoch){c.removeEventListener('characteristicvaluechanged',notification);d.gatt?.disconnect();return false}
   status('Bluetooth MIDI ready: '+(d.name||'piano')+'. Play a key.');return true;
  }catch(e){c?.removeEventListener('characteristicvaluechanged',notification);if(token!==epoch)d?.gatt?.disconnect();if(token===epoch){detachBluetooth();status(e.name==='NotFoundError'?'No piano selected. Connect your piano to try again.':'Bluetooth connection failed: '+e.message)}return false}finally{if(token===epoch)pending=false}
 }
 async function connectMicrophone(){
  if(dead)return false;const allowed=micAllowed();if(allowed!==true){status(allowed);return false}selectMode('mic');
  if(stream)return true;if(pending)return false;
  const policy=doc?.permissionsPolicy||doc?.featurePolicy;
  if(env.isSecureContext===false||!nav.mediaDevices?.getUserMedia||policy?.allowsFeature&&!policy.allowsFeature('microphone')){status('Microphone is unavailable here. Open the downloaded file directly in a browser, or use HTTPS.');return false}
  const token=++epoch;pending=true;let s;
  try{s=await nav.mediaDevices.getUserMedia({audio:{echoCancellation:false,noiseSuppression:false,autoGainControl:false}});
   if(dead||token!==epoch){s.getTracks().forEach(t=>t.stop());return false}
   if(micAllowed()!==true){s.getTracks().forEach(t=>t.stop());status(micAllowed());return false}
   ctx=options.audioContext?.()||ctx||new(env.AudioContext||env.webkitAudioContext)();await ctx.resume();
   if(dead||token!==epoch){s.getTracks().forEach(t=>t.stop());return false}
   stream=s;source=ctx.createMediaStreamSource(s);const analyser=ctx.createAnalyser();analyser.fftSize=8192;source.connect(analyser);const frame=new Float32Array(analyser.fftSize);
   function poll(){if(!stream||dead||token!==epoch)return;const ok=micAllowed();if(ok!==true){stopMic();status(ok);return}analyser.getFloatTimeDomainData(frame);micTracker.process(frame,ctx.sampleRate,clock());raf=env.requestAnimationFrame(poll)}
   raf=env.requestAnimationFrame(poll);status('Microphone ready for single notes E2–C6. Headphones prevent example audio being heard.');return true;
  }catch(e){s?.getTracks().forEach(t=>t.stop());if(token===epoch){stopMic();status('Microphone access failed: '+e.message)}return false}finally{if(token===epoch)pending=false}
 }
 function disconnect(){++epoch;pending=false;reset();stopMic();unbindMidi();detachBluetooth();options.onDisconnect?.(mode);status('Input disconnected.')}
 function destroy(){disconnect();dead=true;bindings.splice(0).forEach(fn=>fn());if(ctx&&!options.audioContext)Promise.resolve(ctx.close?.()).catch(()=>{})}
 listen(env,'blur',reset);listen(doc,'visibilitychange',()=>{if(doc.hidden){reset();if(stream){++epoch;stopMic();options.onDisconnect?.('mic');status('Microphone paused. Reconnect to continue.')}}});listen(env,'pagehide',disconnect);
 return{bindKeyboard,connectMidi,connectBluetooth,connectMicrophone,selectMode,reset,disconnect,destroy,get mode(){return mode},get ready(){return mode==='touch'||mode==='midi'&&ports.size>0||mode==='ble'&&!!characteristic&&!!device?.gatt?.connected||mode==='mic'&&!!stream}};
}
const api={create,detectPitch,createMicTracker,createBLEDecoder,BLE_SERVICE,BLE_CHARACTERISTIC};root.AriaInput=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof globalThis!=='undefined'?globalThis:this);
