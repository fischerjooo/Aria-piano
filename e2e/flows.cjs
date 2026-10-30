#!/usr/bin/env node
'use strict';
// Behavioral browser assertions complement (rather than duplicate) screenshot capture.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const http=require('node:http');
const root=path.resolve(__dirname,'..'),site=path.join(root,'_site');
const contentTypes={'.html':'text/html','.svg':'image/svg+xml','.png':'image/png','.webmanifest':'application/manifest+json','.js':'application/javascript'};
const server=http.createServer((req,res)=>{
  const p=path.resolve(site,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname==='/'?'/index.html':new URL(req.url,'http://localhost').pathname));
  if(!p.startsWith(site+path.sep)){res.writeHead(403).end();return;}
  fs.readFile(p,(err,bytes)=>{if(err){res.writeHead(404).end();return;}res.writeHead(200,{'Content-Type':contentTypes[path.extname(p)]||'application/octet-stream'}).end(bytes);});
});
async function test(browser,base,device,viewport){
  const ctx=await browser.newContext({viewport,hasTouch:true,isMobile:true,serviceWorkers:'block',permissions:[]});
  const page=await ctx.newPage();
  page.on('dialog',d=>d.dismiss());
  try {
    await page.goto(base);
    await page.locator('#courseScreen:not([hidden]) #resume').waitFor();
    assert.equal(await page.locator('#melodiesScreen').isVisible(),false);
    // Course filters must change their actual state, not merely open a screenshot.
    await page.locator('#filters [data-filter="reading"]').click();
    assert.equal(await page.locator('#filters [data-filter="reading"]').getAttribute('aria-pressed'),'true');
    await page.locator('#filters [data-filter="all"]').click();
    assert.equal(await page.locator('#filters [data-filter="all"]').getAttribute('aria-pressed'),'true');
    // Navigate to melodies, exercise a zero-result search, then restore the list.
    await page.locator('#melodyMenu').click();
    await page.locator('#melodiesScreen:not([hidden])').waitFor();
    const count=await page.locator('#melodyCards [data-lesson]').count();
    assert(count>100,'expected populated melodies collection');
    await page.locator('#melodySearch').fill('zz-no-such-aria-melody-991');
    assert.equal(await page.locator('#melodyCards [data-lesson]').count(),0);
    await page.locator('#melodySearch').fill('');
    assert.equal(await page.locator('#melodyCards [data-lesson]').count(),count);
    await page.locator('#melodyGroup').selectOption('classical');
    const classical=await page.locator('#melodyCards [data-lesson]').count();
    assert(classical>0&&classical<count,'collection filter should reduce melody list');
    await page.locator('#melodyGroup').selectOption('all');
    // Use a real melody and check navigation state, dialogs and control semantics.
    await page.locator('#melodyCards [data-lesson]').first().click();
    await page.locator('#studioScreen:not([hidden]) #scoreSvg').waitFor();
    await page.locator('#quickTempo').click();
    await page.locator('#quickTempoModal:not([hidden])').waitFor();
    await page.locator('#quickTempoModal [data-close="quickTempoModal"]').first().click();
    await page.locator('#quickTempoModal').waitFor({state:'hidden'});
    await page.locator('#quickHands').click();
    await page.locator('#quickHandsModal:not([hidden])').waitFor();
    await page.locator('#quickHandsModal [data-close="quickHandsModal"]').first().click();
    await page.locator('#quickHandsModal').waitFor({state:'hidden'});
    await page.locator('#settings').click();
    await page.locator('#settingsModal:not([hidden])').waitFor();
    await page.locator('#settingsModal [data-close="settingsModal"]').first().click();
    await page.locator('#scoreFocus').click();
    assert.equal(await page.locator('#scoreFocus').getAttribute('aria-pressed'),'true');
    await page.reload();
    await page.locator('#courseScreen:not([hidden])').waitFor();
    assert.equal(await page.evaluate(()=>localStorage.getItem('aria-score-focus-v1')),'true','focus preference must persist after reload');
    await page.locator('#melodyMenu').click();
    await page.locator('#melodyCards [data-lesson]').first().click();
    await page.locator('#studioScreen:not([hidden]) #scoreSvg').waitFor();
    assert.equal(await page.locator('#scoreFocus').getAttribute('aria-pressed'),'true','saved focus setting restored');
    await page.locator('#scoreFocus').click();
    assert.equal(await page.locator('#scoreFocus').getAttribute('aria-pressed'),'false');
    await page.locator('#liveSheet').click();
    await page.locator('#sheetScreen:not([hidden]) #staticScore svg').first().waitFor();
    await page.locator('#sheetClose').evaluate(el=>el.click());
    await page.locator('#studioScreen:not([hidden])').waitFor();
    await page.locator('#studioBack').evaluate(el=>el.click());
    await page.locator('#courseScreen:not([hidden])').waitFor();
    console.log('PASS '+device+': filters, search, selection, overlays, focus preference, reload and navigation');
  }finally{await ctx.close();}
}
(async()=>{
 if(!fs.existsSync(path.join(site,'index.html')))throw Error('Build _site before browser tests');
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const url='http://127.0.0.1:'+server.address().port+'/';
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  await test(browser,url,'tablet',{width:1280,height:800});
  await test(browser,url,'phone',{width:915,height:412});
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error(e);process.exitCode=1});
