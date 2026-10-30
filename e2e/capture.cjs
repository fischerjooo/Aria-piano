#!/usr/bin/env node
'use strict';
/*
 * Capture real app states in Chromium. The same script runs CI smoke checks and
 * release gallery capture, without stubbing the UI or inventing screenshots.
 */
const { chromium, devices } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const root = path.resolve(__dirname, '..');
const output = path.join(root, 'docs', 'screenshots');
const capture = process.argv.includes('--capture');
const profiles = {
  mobile: { viewport: {width: 412, height: 915}, deviceScaleFactor: 1, isMobile: true, hasTouch: true },
  tablet: { viewport: {width: 800, height: 1280}, deviceScaleFactor: 1, isMobile: true, hasTouch: true }
};
const types = {'.html':'text/html','.js':'application/javascript','.css':'text/css','.svg':'image/svg+xml','.png':'image/png','.json':'application/json','.webmanifest':'application/manifest+json'};
const site = path.resolve(root, '_site');
function server() {
  return http.createServer((req, res) => {
    const url = new URL(req.url, 'http://localhost');
    const name = decodeURIComponent(url.pathname === '/' ? '/index.html' : url.pathname);
    const file = path.resolve(site, '.' + name);
    if (!(file === site || file.startsWith(site + path.sep))) { res.writeHead(403).end(); return; }
    fs.readFile(file, (err, data) => {
      if (err) {res.writeHead(404).end();return;}
      res.writeHead(200, {'Content-Type':types[path.extname(file)]||'application/octet-stream', 'Cache-Control':'no-store'}).end(data);
    });
  });
}
async function visible(page, selector) {
  await page.locator(selector).waitFor({state:'visible',timeout:12000});
}
async function shot(page, folder, name) {
  if (capture) {
    const target = path.join(output, folder, name + '.png');
    fs.mkdirSync(path.dirname(target), {recursive:true});
    await page.screenshot({path:target, animations:'disabled', fullPage:false});
  }
}
async function flow(browser, profile, options) {
  const context = await browser.newContext({...options, permissions:[], serviceWorkers:'block', reducedMotion:'reduce'});
  const page = await context.newPage();
  page.on('dialog', async dialog => dialog.dismiss());
  try {
    await page.goto(profile, {waitUntil:'domcontentloaded'});
    await visible(page, '#courseScreen:not([hidden]) #resume');
    await shot(page, options.viewport.width===412?'mobile':'tablet', 'home');
    await page.locator('#melodyMenu').click();
    await visible(page, '#melodiesScreen:not([hidden]) #melodyCards [data-lesson]');
    await shot(page, options.viewport.width===412?'mobile':'tablet', 'lesson-selection');
    // Start a known melody; its sheet view is longer than the introductory exercise.
    await page.locator('#melodyCards [data-lesson]').last().click();
    await visible(page, '#studioScreen:not([hidden]) #scoreSvg');
    const dir=options.viewport.width===412?'mobile':'tablet';
    await shot(page, dir, 'lesson-running');
    await page.locator('#settings').click();
    await visible(page, '#settingsModal:not([hidden])');
    await shot(page, dir, 'settings');
    await page.locator('#settingsModal [data-close="settingsModal"]').click();
    await page.locator('#liveSheet').click();
    await visible(page, '#sheetScreen:not([hidden]) #staticScore');
    await shot(page, dir, 'long-song-sheet');
    if (capture) {
      for (const name of ['home','lesson-selection','lesson-running','settings','long-song-sheet']) {
        if (!fs.existsSync(path.join(output,dir,name+'.png'))) throw new Error('Missing '+dir+'/'+name);
      }
    }
    console.log('PASS '+dir+' home, selection, practice, settings and sheet');
  } finally { await context.close(); }
}
(async()=>{
  if (!fs.existsSync(path.join(site,'index.html'))) throw new Error('Run python scripts/build.py first');
  const httpServer=server();
  await new Promise(resolve=>httpServer.listen(0,'127.0.0.1',resolve));
  const port=httpServer.address().port;
  const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
  try {
    for (const [name,profile] of Object.entries(profiles)) {
      await flow(browser,'http://127.0.0.1:'+port+'/',profile);
    }
  } finally {
    await browser.close();
    await new Promise(resolve=>httpServer.close(resolve));
  }
})().catch(e=>{console.error(e);process.exitCode=1;});
