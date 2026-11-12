import { chromium } from '@playwright/test';
import { fileURLToPath } from 'node:url';
import {readFile,writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const root=fileURLToPath(new URL('../../../', import.meta.url)).replace(/\/$/, '');
const project='91884a98-0f32-4e73-b2ef-b6f075f18ce6';
const en=JSON.parse(await readFile(`${root}/apps/web/src/app/locales/en.json`)).scheduleImport;
const fa=JSON.parse(await readFile(`${root}/apps/web/src/app/locales/fa.json`)).scheduleImport;
const xml=await readFile(new URL('./fixtures/browser-schedule.xml', import.meta.url));
const browser=await chromium.launch({executablePath:process.env.PLAYWRIGHT_EXECUTABLE_PATH,headless:true});
const notes=[];
let authState;
try {
for(const width of [1280,390]) for(const lang of ['en','fa']) {
 console.log('starting',width,lang);
 const c=await browser.newContext({viewport:{width,height:844},storageState:authState}); const p=await c.newPage(); const t=lang==='en'?en:fa;
 if (!authState) {
   if (process.env.IMPORT_TEST_AUTH_FILE) {
     const auth=JSON.parse(await readFile(process.env.IMPORT_TEST_AUTH_FILE));
     await c.addCookies([{name:'auth_token',value:auth.access,domain:'127.0.0.1',path:'/'}]);
     await p.goto('http://127.0.0.1:5173/login');
     await p.evaluate(auth=>{
       localStorage.setItem('auth_access_token',auth.access);
       localStorage.setItem('auth_refresh_token',auth.refresh);
       localStorage.setItem('auth_user',JSON.stringify(auth.user));
     },auth);
     await p.goto(`http://127.0.0.1:5173/projects/${project}/wbs`);
   } else {
     await p.goto('http://127.0.0.1:5173/login');
     await p.getByTestId('login-phone-input').fill(process.env.IMPORT_TEST_PHONE ?? '+10000000001');
     await p.getByTestId('login-password-input').fill(process.env.IMPORT_TEST_PASSWORD ?? 'devpass123');
     await p.getByRole('button',{name:/ورود|Sign in/}).click();
     await p.waitForURL(u=>!u.pathname.startsWith('/login'));
   }
   authState=await c.storageState();
 } else {
   await p.goto(`http://127.0.0.1:5173/projects/${project}/wbs`);
 }
 await p.locator(`#button-language-${lang}`).click();
 await p.goto(`http://127.0.0.1:5173/projects/${project}/wbs`);
 await p.getByTestId('msp-import-btn').focus(); await p.keyboard.press('Enter');
 const dialog=p.getByRole('dialog');
 // File chooser is supplied by automation; all subsequent actions are keyboard activated.
 await dialog.locator('input[type=file]').setInputFiles({name:'wrong.txt',mimeType:'text/plain',buffer:Buffer.from('wrong')});
 await p.getByText(t.wrongExtension,{exact:true}).waitFor();
 await dialog.locator('input[type=file]').setInputFiles({name:'schedule-with-a-long-file-name-for-bidirectional-reading-برنامه.xml',mimeType:'application/xml',buffer:xml});
 let release; const held=new Promise(r=>release=r); let previewRequests=0;
 await p.route('**/import/msp/preview/',async route=>{previewRequests++; await held; await route.continue();});
 await dialog.getByRole('button',{name:t.preview,exact:true}).focus(); await p.keyboard.press('Enter');
 await p.waitForFunction(()=>document.querySelector('input[type=file]')?.disabled);
 // A genuine DataTransfer/drop while the real preview request is held.
 const dt=await p.evaluateHandle(()=>{const d=new DataTransfer();d.items.add(new File(['wrong'],'second.xml',{type:'application/xml'}));return d;});
 await dialog.locator('[class*="border-dashed"]').dispatchEvent('drop',{dataTransfer:dt});
 assert.match(await dialog.getByTestId('msp-import-filename').innerText(),/schedule-with-a-long/);
 release();
 await dialog.getByText(t.kindLabel+':',{exact:false}).waitFor();
 assert.equal(previewRequests,1);
 await dialog.getByTestId('msp-import-warnings').waitFor();
 await dialog.getByLabel(t.replace,{exact:true}).focus(); await p.keyboard.press('Space');
 await dialog.getByTestId('msp-import-refusal').waitFor(); assert.equal(await dialog.getByRole('button',{name:t.confirm,exact:true}).isDisabled(),true);
 await dialog.getByLabel(t.append,{exact:true}).focus(); await p.keyboard.press('Space');
 let starts=0; let task;
 p.on('request',r=>{if(/\/import\/msp\/$/.test(r.url())&&r.method()==='POST')starts++;});
 p.on('response',async r=>{if(/\/import\/msp\/$/.test(r.url())&&r.request().method()==='POST'){task=(await r.json()).task_id;}});
 await p.route('**/import/msp/status/**',route=>route.abort());
 await dialog.getByRole('button',{name:t.confirm,exact:true}).focus(); await p.keyboard.press('Enter');
 await dialog.getByTestId('msp-import-interrupted').waitFor({timeout:60000});
 assert.equal(starts,1);
 await p.unroute('**/import/msp/status/**');
 await dialog.getByRole('button',{name:t.retryStatus,exact:true}).focus(); await p.keyboard.press('Enter');
 await dialog.getByText(/Nothing in the schedule changed|The schedule was imported|برنامه تغییری نکرد|برنامه وارد شد/).waitFor({timeout:60000});
 assert.equal(starts,1); assert.ok(task);
 await dialog.getByRole('link',{name:t.viewActivities,exact:true}).waitFor();
 await p.screenshot({path:`${root}/specs/054-a7-p4-import-experience/evidence/screenshots/recheck-${width}-${lang}.png`});
 await dialog.getByRole('button',{name:t.chooseAnother,exact:true}).focus(); await p.keyboard.press('Enter');
 await dialog.locator('input[type=file]').waitFor();
 assert.equal(await p.evaluate(()=>Object.keys(sessionStorage).filter(k=>k.startsWith('schedule-import-attempt:')).length),0);
 const formats=[];
 await p.unroute('**/import/msp/preview/');
 for (const [kind,path] of [
   ['mpp', `${root}/real-data/plan.mpp`],
   ['xer', `${root}/specs/054-a7-p4-import-experience/evidence/fixtures/browser-schedule.xer`],
 ]) {
   console.log('format',width,lang,kind);
   await dialog.locator('input[type=file]').setInputFiles(path);
   await dialog.getByRole('button',{name:t.preview,exact:true}).focus(); await p.keyboard.press('Enter');
   await dialog.getByText(t.kinds[kind],{exact:false}).waitFor({timeout:60000}).catch(async e=>{console.log(await dialog.innerText());await p.screenshot({path:`${root}/specs/054-a7-p4-import-experience/evidence/screenshots/format-error-${width}-${lang}.png`});throw e;});
   await dialog.getByRole('button',{name:t.confirm,exact:true}).focus(); await p.keyboard.press('Enter');
   await dialog.getByText(/Nothing in the schedule changed|The schedule was imported|برنامه تغییری نکرد|برنامه وارد شد/).waitFor({timeout:60000});
   formats.push(kind);
   await p.screenshot({path:`${root}/specs/054-a7-p4-import-experience/evidence/screenshots/recheck-${width}-${lang}-${kind}.png`});
   await dialog.getByRole('button',{name:t.chooseAnother,exact:true}).click();
   await dialog.locator('input[type=file]').waitFor();
 }
 console.log('main passed',width,lang);
 // Close during a held preview, then release: the stale response cannot reopen preview.
 await p.unroute('**/import/msp/preview/');
 let releaseLate; const lateHeld=new Promise(r=>releaseLate=r);
 await p.route('**/import/msp/preview/',async route=>{await lateHeld; await route.continue();});
 await dialog.locator('input[type=file]').setInputFiles({name:'late.xml',mimeType:'application/xml',buffer:xml});
 await dialog.getByRole('button',{name:t.preview,exact:true}).click();
 await p.waitForFunction(()=>document.querySelector('input[type=file]')?.disabled);
 await p.locator('#button-closeMspImportModal').click();
 await dialog.waitFor({state:'hidden'});
 releaseLate();
 await p.getByTestId('msp-import-btn').click();
 await dialog.locator('input[type=file]').waitFor().catch(async e=>{await p.screenshot({path:`${root}/specs/054-a7-p4-import-experience/evidence/screenshots/late-failure-${width}-${lang}.png`});console.log(await dialog.innerText());throw e;});
 await p.waitForFunction(()=>!document.querySelector('input[type=file]')?.disabled);
 assert.equal(await dialog.getByRole('button',{name:t.confirm,exact:true}).count(),0);
 notes.push({width,lang,task,starts,previewRequests,stalePreviewDiscarded:true,formats,success:true});console.log(JSON.stringify(notes.at(-1)));
 await c.close();
}
} finally {await browser.close();await writeFile(new URL('./browser-results.json', import.meta.url),JSON.stringify(notes,null,2));}
