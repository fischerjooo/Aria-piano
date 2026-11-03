const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'src/app/runtime.js'),'utf8');
const template=fs.readFileSync(path.join(root,'src/app/template.html'),'utf8');
assert.equal((template.match(/data-input-choice=/g)||[]).length,4);
assert.match(template,/data-input-choice="usb"/);
assert.match(template,/id="usbConnect"/);
assert.doesNotMatch(template,/id="micFallback"/);
assert.match(source,/function isMidiMode\(\)\{return mode==='ble'\|\|mode==='usb'\}/);
assert.match(source,/if\(isMidiMode\(\)&&midi&&targets\.includes\(m\)/);
assert.match(source,/if\(isMidiMode\(\)&&\(mode==='ble'\?bleReady\(\):usbReady\(\)\)/);
const start=source.indexOf('let usbAccess=null');
const stop=source.indexOf('function decodeBLE(value,emit)',start);
assert(start>0&&stop>start,'USB engine must be available in the app runtime');
const code=source.slice(start,stop);
const dom=new Map(),events=[],accessListeners={};
function el(id){if(!dom.has(id))dom.set(id,{id,textContent:'',hidden:false,disabled:false,attrs:{},classList:{toggle(){}} ,setAttribute(k,v){this.attrs[k]=v}});return dom.get(id)}
function port(id,name){const handlers=new Map();return{id,name,state:'connected',addEventListener(k,fn){handlers.set(k,fn)},removeEventListener(k,fn){if(handlers.get(k)===fn)handlers.delete(k)},emit(data){handlers.get('midimessage')?.({data:Uint8Array.from(data)})},get listening(){return handlers.has('midimessage')}}}
const inputA=port('p1','Piano USB'),inputB=port('p2','Second keyboard');
const access={inputs:new Map([['p1',inputA]]),addEventListener(type,fn){accessListeners[type]=fn}};
let requests=0,runsStopped=0,resetCount=0;
const ctx={console,Map,Promise,Uint8Array,mode:'mic',screen:'studio',resultReplay:null,document:{querySelectorAll:()=>[],hidden:false},window:{isSecureContext:true},navigator:{requestMIDIAccess(opts){requests++;assert.equal(opts.sysex,false);return Promise.resolve(access)}},midiHeld:new Set(),midiPedals:new Set(),stepHits:new Set(),bleReleaseTimer:null,clearTimeout(){},stopRun(){runsStopped++},initialiseResultsReplay(){},syncConnectionPicker(){},receiveMidi(status,note,velocity){events.push([status,note,velocity])},chooseMode(value){this.mode=value;resetCount++;},$:el};
vm.createContext(ctx);
// Top-level state in the extracted code is evaluated in the same realm as the mocks.
vm.runInContext(code,ctx);
function run(expr){return vm.runInContext(expr,ctx)}
(async()=>{
 assert.equal(await run('connectUSBMidi()'),true);
 assert.equal(requests,1);
 assert.equal(run('mode'),'usb','USB must win at startup when detected');
 assert.equal(resetCount,1);
 assert.equal(run('usbReady()'),true);
 assert.equal(inputA.listening,true);
 assert.match(el('usbStatus').textContent,/Piano USB/);
 inputA.emit([0x90,60,100]);inputA.emit([0x80,60,0]);inputA.emit([0xb0,64,127]);
 assert.deepEqual(events,[[0x90,60,100],[0x80,60,0],[0xb0,64,127]]);
 run('mode="mic"');
 inputA.emit([0x90,61,100]);assert.equal(events.length,3,'ignore USB while another input mode is selected');
 access.inputs.set('p2',inputB);accessListeners.statechange();
 assert.equal(run('mode'),'usb','new hotplugged port must activate USB automatically');
 assert.equal(resetCount,2);
 assert.equal(inputB.listening,true);
 ctx.midiHeld.add('0:60');ctx.midiPedals.add(0);
 access.inputs.clear();accessListeners.statechange();
 assert.equal(run('usbReady()'),false);
 assert.equal(inputA.listening,false);assert.equal(inputB.listening,false);
 assert.equal(ctx.midiHeld.size,0);assert.equal(ctx.midiPedals.size,0);
 assert.equal(runsStopped,1,'unplug pauses current practice');
 assert.match(el('usbStatus').textContent,/disconnected/);
 access.inputs.set('p1',inputA);accessListeners.statechange();
 assert.equal(run('mode'),'usb');
 assert.equal(inputA.listening,true);
 assert.equal(requests,1,'hotplug must reuse an existing MIDI permission');
 console.log('PASS USB MIDI startup auto-selection, message routing, hotplug, unplug, reconnection and connection UI');
})().catch(e=>{console.error(e);process.exitCode=1});
