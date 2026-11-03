const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.join(__dirname,'..'),source=fs.readFileSync(path.join(root,'src/app/runtime.js'),'utf8');
const template=fs.readFileSync(path.join(root,'src/app/template.html'),'utf8');
const built=fs.readFileSync(path.join(root,'index.html'),'utf8');
for(const id of ['connectionMicPanel','connectionSensitivity','connectionSensitivityValue','connectionMicMeter','connectionMicLevel','connectionDetectedNote','quickSpeedCustom','quickCustomSpeed','quickCustomSpeedValue']) {
 assert(template.includes('id="'+id+'"')&&built.includes('id="'+id+'"'),id+' must appear in the source and built app');
}
assert(template.includes('id="quickCustomSpeed" type="range" min="10" max="50"'));
assert(template.includes('id="tempo" type="range" min="5"'),'under-20-BPM custom values must not be clipped');
assert(source.includes("$('connectionMicPanel').hidden=mode!=='mic'"),'mic settings only visible in mic mode');
assert(source.includes("$('connectionSensitivity').oninput"),'picker threshold must update the actual detector');
assert(source.includes("processPitch(p.freq,p.rms,t,{confidence:p.confidence"),'mic monitor receives pitch confidence');
assert(source.includes('class="score-finger-label"')&&source.includes('class="score-name-label"'));
assert(source.includes('class="score-finger-label" x="${x}" y="${scoreFingerY(y,clef)}" text-anchor="middle" font-size="14"'));
assert(source.includes('class="score-name-label" x="${x}" y="${scoreNameY(y,clef)}" text-anchor="middle" font-size="14"'));
const elements={};function el(id){return elements[id]||(elements[id]={value:id==='sensitivity'?4:0,textContent:'',style:{},attrs:{},setAttribute(k,v){this.attrs[k]=v}})}
const sandbox={$:el,listeningOptions:()=>({tuning:440,tolerance:45}),noteName:m=>m===60?'C4':m===62?'D4':String(m),Math,Number,String};
vm.createContext(sandbox);
vm.runInContext("let stream={};let micPreviewNote=-1,micPreviewSince=0,micPreviewQuietSince=0;\n"+source.split('\n').filter(l=>l.startsWith('function syncMicSensitivity(')||l.startsWith('function updateMicConnectionMonitor(')).join('\n'),sandbox);
sandbox.syncMicSensitivity(8);assert.equal(+el('connectionSensitivity').value,8);assert.equal(+el('sensitivity').value,8);
assert.equal(el('connectionSensitivityValue').textContent,'8 / 30');
sandbox.updateMicConnectionMonitor(261.6256,.1,1000,{confidence:.95});
assert(!el('connectionDetectedNote').textContent.includes('C4'),'first uncertain frame must not announce a note');
sandbox.updateMicConnectionMonitor(261.6256,.1,1100,{confidence:.95});
assert.equal(el('connectionDetectedNote').textContent,'Detected note: C4');
assert(+el('connectionMicMeter').attrs['aria-valuenow']>0,'live input meter should update');
sandbox.updateMicConnectionMonitor(293.6648,.1,1200,{confidence:.5});
assert.equal(el('connectionDetectedNote').textContent,'Detected note: C4','noisy low-confidence pitch must not flash a wrong note');
sandbox.updateMicConnectionMonitor(0,0,1300,{confidence:0});
sandbox.updateMicConnectionMonitor(0,0,1500,{confidence:0});
assert.match(el('connectionDetectedNote').textContent,/no clear note detected/);
console.log('Microphone picker sensitivity, live meter, stable note text, low-confidence filtering and larger score labels pass');
