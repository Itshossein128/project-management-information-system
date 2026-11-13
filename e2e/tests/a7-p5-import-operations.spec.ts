import { expect, test } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
const fixture = JSON.parse(fs.readFileSync(process.env.A7P5_BROWSER_FIXTURES!, 'utf8'));
const root = path.resolve(__dirname, '../..');
const xml = Buffer.from('<Project xmlns="http://schemas.microsoft.com/project"><Tasks><Task><UID>1</UID><Name>Package</Name><OutlineLevel>1</OutlineLevel><OutlineNumber>1</OutlineNumber><WBS>1</WBS><Summary>1</Summary></Task><Task><UID>2</UID><Name>Work</Name><OutlineLevel>2</OutlineLevel><OutlineNumber>1.1</OutlineNumber><WBS>1.1</WBS><Summary>0</Summary><Duration>PT8H0M0S</Duration></Task></Tasks></Project>');
for (const item of fixture.cases) {
  test(`real retry ${item.lang} ${item.width}`, async ({ page, context }) => {
    const t = JSON.parse(fs.readFileSync(path.join(root, `apps/web/src/app/locales/${item.lang}.json`), 'utf8')).scheduleImport;
    await page.setViewportSize({ width: item.width, height: item.width === 390 ? 844 : 800 });
    await context.addCookies([{ name: 'auth_token', value: fixture.auth.access, domain: '127.0.0.1', path: '/' }]);
    await page.addInitScript(({ auth, item }) => {
      localStorage.setItem('auth_access_token', auth.access);
      localStorage.setItem('auth_refresh_token', auth.refresh);
      localStorage.setItem('auth_user', JSON.stringify(auth.user));
      localStorage.setItem('app-language', item.lang);
      localStorage.setItem('i18nextLng', item.lang);
      sessionStorage.setItem(`schedule-import-attempt:${auth.user.id}:${item.project}`, JSON.stringify({user_id:auth.user.id,project_id:item.project,task_id:item.predecessor,file_name:'plan.xml',recognized_kind:'xml',replace:false}));
    }, { auth: fixture.auth, item });
    await page.goto(`/projects/${item.project}/wbs`);
    await page.locator(`#button-language-${item.lang}`).click();
    await page.getByTestId('msp-import-btn').focus(); await page.keyboard.press('Enter');
    const dialog = page.getByRole('dialog');
    await expect(dialog.getByTestId('msp-import-fatal-error')).toBeVisible();
    await dialog.getByTestId('msp-import-business-retry').focus(); await page.keyboard.press('Enter');
    await expect(dialog.getByTestId('msp-import-retry-hint')).toBeVisible();
    await dialog.getByTestId('msp-import-file').setInputFiles({name:'retry-plan.xml',mimeType:'application/xml',buffer:xml});
    await dialog.getByRole('button',{name:t.preview,exact:true}).focus(); await page.keyboard.press('Enter');
    await dialog.getByLabel(t.append,{exact:true}).check();
    const sent = page.waitForRequest(r => r.method()==='POST' && /\/import\/msp\/$/.test(r.url()));
    const accepted = page.waitForResponse(r => r.request().method()==='POST' && /\/import\/msp\/$/.test(r.url()));
    let starts=0;
    page.on('request',r=>{if(r.method()==='POST' && /\/import\/msp\/$/.test(r.url()))starts++;});
    const readBody = (request: { postDataBuffer: () => Buffer | null, postData: () => string | null }) => {
      const bytes = request.postDataBuffer();
      return bytes ? bytes.toString('utf8') : (request.postData() ?? '');
    };
    // Keep the route installed. page.unroute detaches Chromium's buffered body,
    // so a later multipart postDataBuffer() becomes empty.
    let abortStatus = true;
    await page.route('**/import/msp/status/**', route => abortStatus ? route.abort() : route.continue());
    await dialog.getByRole('button',{name:t.confirm,exact:true}).focus(); await page.keyboard.press('Enter');
    const request=await sent; const body=readBody(request);
    expect(body).toContain('name="intent"'); expect(body).toContain('retry');
    expect(body).toContain('name="retry_of"'); expect(body).toContain(item.predecessor);
    const response=await accepted; expect(response.status()).toBe(202);
    const result=await response.json(); expect(result.task_id).not.toBe(item.predecessor);
    await expect(dialog.getByTestId('msp-import-interrupted')).toBeVisible();
    abortStatus = false;
    await dialog.getByRole('button',{name:t.retryStatus,exact:true}).focus(); await page.keyboard.press('Enter');
    await expect(dialog.getByRole('button',{name:t.chooseAnother,exact:true})).toBeVisible({timeout:60_000});
    expect(starts).toBe(1);
    const status=await context.request.get(`http://127.0.0.1:18000/api/v1/projects/${item.project}/import/msp/status/${result.task_id}/`,{headers:{Authorization:`Bearer ${fixture.auth.access}`}});
    expect((await status.json()).status).toBe('done');
    await page.screenshot({path:path.join(root,`specs/055-a7-p5-import-operations/evidence/runtime/browser-${item.lang}-${item.width}.png`),fullPage:true});
    await dialog.getByRole('button',{name:t.chooseAnother,exact:true}).click();
    await expect(dialog.getByTestId('msp-import-retry-hint')).toHaveCount(0);
    await dialog.getByTestId('msp-import-file').setInputFiles({name:'fresh-plan.xml',mimeType:'application/xml',buffer:Buffer.from(xml.toString().replaceAll('<WBS>1','<WBS>2').replaceAll('<OutlineNumber>1','<OutlineNumber>2'))});
    const previewed = page.waitForResponse(r => r.request().method()==='POST' && /\/import\/msp\/preview\/$/.test(r.url()));
    await dialog.getByRole('button',{name:t.preview,exact:true}).click();
    expect((await previewed).status()).toBe(200);
    await dialog.getByLabel(t.append,{exact:true}).check();
    const freshSent=page.waitForRequest(r=>r.method()==='POST' && /\/import\/msp\/$/.test(r.url()));
    const freshAccepted=page.waitForResponse(r=>r.request().method()==='POST' && /\/import\/msp\/$/.test(r.url()));
    await dialog.getByRole('button',{name:t.confirm,exact:true}).click();
    const freshBody=readBody(await freshSent);
    expect(freshBody).toContain('name="intent"');expect(freshBody).toContain('\r\nnew\r\n');
    expect(freshBody).not.toContain('name="retry_of"');
    const freshResponse=await freshAccepted;
    expect(freshResponse.status()).toBe(202);
    const freshTask=(await freshResponse.json()).task_id as string;
    await expect.poll(async () => {
      const polled=await context.request.get(`http://127.0.0.1:18000/api/v1/projects/${item.project}/import/msp/status/${freshTask}/`,{headers:{Authorization:`Bearer ${fixture.auth.access}`}});
      return (await polled.json()).status;
    }, {timeout:60_000}).toBe('done');
    await expect(dialog.getByRole('button',{name:t.chooseAnother,exact:true})).toBeVisible();
    expect(starts).toBe(2);
    const invalid=await context.request.post(`http://127.0.0.1:18000/api/v1/projects/${item.project}/import/msp/`,{
      headers:{Authorization:`Bearer ${fixture.auth.access}`},
      multipart:{file:{name:'plan.xml',mimeType:'application/xml',buffer:xml},replace:'false',intent:'retry'},
    });
    expect(invalid.status()).toBe(400);
  });
}
