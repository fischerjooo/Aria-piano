#!/usr/bin/env node
'use strict';
const {chromium} = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const root = path.resolve(__dirname, '..');
const output = path.join(root, 'docs', 'screenshots');
const capture = process.argv.includes('--capture');
const profiles = {
  mobile: { viewport:{width:915,height:412},deviceScaleFactor:1,isMobile:true,hasTouch:true },
  tablet: { viewport:{width:1280,height:800},deviceScaleFactor:1,isMobile:true,hasTouch:true }
};
const portraits = {mobile:{width:412,height:915},tablet:{width:800,height:1280}};
const names = [
 'home','home-scrolled','lessons','lessons-scrolled',
 'melodies','melodies-scrolled','melodies-filtered',
 'lesson-running','lesson-settings','lesson-tempo','lesson-hands','lesson-guide',
 'lesson-music-focus','lesson-sheet','sheet-controls',
 'sheet-portrait'
];
const types = {'.html':'text/html','.js':'application/javascript','.css':'text/css','.svg':'image/svg+xml','.png':'image/png','.json':'application/json','.webmanifest':'application/manifest+json'};
const site = path.resolve(root, '_site');
function server() {
  return http.createServer((req,res)=>{
    const url=new URL(req.url,'http://localhost');
    const name=decodeURIComponent(url.pathname==='/'?'/index.html':url.pathname);
    const file=path.resolve(site,'.'+name);
    if (!(file===site||file.startsWith(site+path.sep))) {res.writeHead(403).end();return;}
    fs.readFile(file,(err,data)=>{if(err){res.writeHead(404).end();return;}res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream','Cache-Control':'no-store'}).end(data)});
  });
}
async function visible(page,selector){await page.locator(selector).first().waitFor({state:'visible',timeout:15000});}
async function take(page,device,name) {
  if(!names.includes(name))throw new Error('Unknown capture '+name);
  if(capture){const target=path.join(output,device,name+'.png');fs.mkdirSync(path.dirname(target),{recursive:true});await page.screenshot({path:target,animations:'disabled',fullPage:false});}
  console.log(device+' '+name);
}
async function scroll(page,selector,pixels){
  await page.locator(selector).first().evaluate((el,amount)=>{
    let current=el;
    while(current){
      if(current.scrollHeight>current.clientHeight+50){current.scrollTop=amount;return;}
      current=current.parentElement;
    }
    window.scrollTo(0,amount);
  },pixels);
  await page.waitForTimeout(130);
}
async function close(page,id){
  await page.locator('#'+id+' [data-close="'+id+'"]').first().click();
  await page.locator('#'+id).waitFor({state:'hidden'});
}
async function flow(browser,url,device,options){
  const context=await browser.newContext({...options,permissions:[],serviceWorkers:'block',reducedMotion:'reduce'});
  const page=await context.newPage();
  page.on('dialog',async dialog=>dialog.dismiss());
  const original=options.viewport;
  try{
    await page.goto(url,{waitUntil:'domcontentloaded'});
    await visible(page,'#courseScreen:not([hidden]) #resume');
    await take(page,device,'home');
    await scroll(page,'#courseScreen .content',700);
    await take(page,device,'home-scrolled');
    await page.locator('#courseScreen #filters [data-filter="reading"]').click();
    await visible(page,'#courseScreen:not([hidden]) #lessons .lesson-card');
    await take(page,device,'lessons');
    await scroll(page,'#courseScreen .content',1150);
    await take(page,device,'lessons-scrolled');
    await page.locator('#melodyMenu').click();
    await visible(page,'#melodiesScreen:not([hidden]) #melodyCards [data-lesson]');
    await take(page,device,'melodies');
    await scroll(page,'#melodiesScreen .content',900);
    await take(page,device,'melodies-scrolled');
    await page.locator('#melodyGroup').selectOption('classical');
    await visible(page,'#melodyCards [data-lesson]');
    await take(page,device,'melodies-filtered');
    // Choose longest two-hand arrangement available in the actual live catalogue,
    // rather than a short motif or an invented demo score.
    const index=await page.evaluate(()=>{
      const all=typeof lessons==='undefined'?[]:lessons;
      const options=all.map((l,i)=>({i,n:l.seq?.length||0,both:!!l.left,melody:l.kind==='melody'||!!l.application}));
      const picked=options.filter(x=>x.both&&x.melody).sort((a,b)=>b.n-a.n)[0];
      if(!picked||picked.n<16)throw new Error('No suitably long two-hand melody in the catalogue');
      return picked.i;
    });
    await page.locator('#melodyGroup').selectOption('all');
    await page.locator('#melodyCards [data-lesson="'+index+'"]').click();
    await visible(page,'#studioScreen:not([hidden]) #scoreSvg');
    await take(page,device,'lesson-running');
    await page.locator('#settings').click();
    await visible(page,'#settingsModal:not([hidden])');
    await take(page,device,'lesson-settings');
    await close(page,'settingsModal');
    await page.locator('#quickTempo').click();
    await visible(page,'#quickTempoModal:not([hidden])');
    await take(page,device,'lesson-tempo');
    await close(page,'quickTempoModal');
    await page.locator('#quickHands').click();
    await visible(page,'#quickHandsModal:not([hidden])');
    await take(page,device,'lesson-hands');
    await close(page,'quickHandsModal');
    await page.locator('#guide').click();
    // The guide may open an overlay; capture only after it appears.
    await page.waitForTimeout(180);
    await take(page,device,'lesson-guide');
    // Dismiss any active informational overlay without guessing the dialog ID.
    await page.locator('.overlay:not([hidden]) [data-close]').first().click();
    await page.locator('#scoreFocus').click();
    await take(page,device,'lesson-music-focus');
    await page.locator('#scoreFocus').click();
    await page.locator('#liveSheet').click();
    await visible(page,'#sheetScreen:not([hidden]) #staticScore svg');
    await take(page,device,'lesson-sheet');
    await page.locator('#sheetSizing').click();
    await page.waitForTimeout(120);
    await take(page,device,'sheet-controls');
    await page.setViewportSize(portraits[device]);
    await page.waitForTimeout(350);
    await visible(page,'#sheetScreen:not([hidden]) #staticScore svg');
    await take(page,device,'sheet-portrait');
    await page.setViewportSize(original);
    if(capture)for(const name of names){
      const file=path.join(output,device,name+'.png');
      if(!fs.existsSync(file)||fs.statSync(file).size<1500)throw new Error('Missing screenshot '+device+'/'+name);
    }
    console.log('PASS '+device+' '+names.length+' states');
  }finally{await context.close();}
}
(async()=>{
  if(!fs.existsSync(path.join(site,'index.html')))throw new Error('Run python scripts/build.py first');
  const httpServer=server();
  await new Promise(resolve=>httpServer.listen(0,'127.0.0.1',resolve));
  const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
  try{for(const [device,options] of Object.entries(profiles))await flow(browser,'http://127.0.0.1:'+httpServer.address().port+'/',device,options);}
  finally{await browser.close();await new Promise(resolve=>httpServer.close(resolve));}
})().catch(e=>{console.error(e);process.exitCode=1;});
