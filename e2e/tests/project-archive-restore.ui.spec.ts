import { expect, test } from "@playwright/test";
import { session, visit } from "../helpers/navigation";
const id = "11111111-1111-4111-8111-111111111111";
const base = `/api/v1/projects/${id}`;
const routePath = `/projects/${id}/overview`;
const project = {project_id:id, project_name:"Archive test project", project_code:"RESTORE", status:"archived", currency:"IRR", can_restore_from_archive:true, can_view_restore_history:false};
const labels = {en:{action:"Restore from archive",reason:"Reason",confirm:"Confirm restoration",cancel:"Cancel"},fa:{action:"خروج از بایگانی",reason:"دلیل",confirm:"تأیید بازگردانی",cancel:"لغو"}};
for (const language of ["fa","en"] as const) {
 test.describe(`${language} restoration`,()=>{
  test.beforeEach(async({page})=>{
   await session(page,[],language); // No frontend group role and no membership.
   await page.route(`**${base}/`,r=>r.fulfill({json:project}));
   await page.route(`**${base}/members/*/permissions/`,r=>r.fulfill({status:404,json:{}}));
   await page.route(`**${base}/restore-preview/`,r=>r.fulfill({json:{project_id:id,project_name:project.project_name,from_status:"archived",to_status:"completed",archive_cycle_id:id,lifecycle_version:1,confirmation_token:"signed",can_confirm:true,missing:[],remediation:[]}}));
  });
  test("nonmember server capability opens fixed target, requires reason, and cancels without a write",async({page})=>{
   let writes=0;await page.route(`**${base}/restore/`,r=>{writes++;return r.abort();});
   await visit(page,routePath,language);
   await page.getByRole("button",{name:labels[language].action,exact:true}).click();
   const dialog=page.getByRole("dialog");await expect(dialog).toContainText(project.project_name);
   await expect(dialog.getByTestId("restore-target")).toContainText(language==="fa"?"خاتمه‌یافته":"Completed");
   await expect(dialog.getByRole("button",{name:labels[language].confirm,exact:true})).toBeDisabled();
   await dialog.getByLabel(labels[language].reason,{exact:true}).fill("   ");
   await expect(dialog.getByRole("button",{name:labels[language].confirm,exact:true})).toBeDisabled();
   await dialog.getByRole("button",{name:labels[language].cancel,exact:true}).click();
   await expect(dialog).not.toBeVisible();expect(writes).toBe(0);
  });
 });
}

for(const language of ["fa","en"] as const) {
 test(`${language} incomplete active restoration links to executable manager and CR completion`,async({page})=>{
  await session(page,[],language);
  await page.route(`**${base}/`,r=>r.fulfill({json:{...project,can_edit_manager_for_restore:true,can_create_restore_remediation:true}}));
  await page.route(`**${base}/members/*/permissions/`,r=>r.fulfill({status:404,json:{}}));
  await page.route(`**${base}/change-requests/`,r=>r.fulfill({json:[]}));
  await page.route(`**${base}/restore-preview/`,r=>r.fulfill({json:{project_id:id,project_name:project.project_name,to_status:"active",confirmation_token:"signed",can_confirm:false,missing:["project_manager","scope_description","budget_approved"],remediation:[{field:"project_manager",action:"project_settings"},{field:"scope_description",action:"project_change_request"},{field:"budget_approved",action:"project_change_request"}]}}));
  await visit(page,routePath,language);
  await page.getByRole("button",{name:labels[language].action,exact:true}).click();
  const dialog=page.getByRole("dialog");
  await expect(dialog.getByRole("listitem")).toHaveCount(3);
  const manager=dialog.getByRole("link",{name:language==="fa"?"تکمیل مدیر پروژه":"Complete project manager",exact:true});
  await expect(manager).toHaveAttribute("href",`/projects/${id}/settings#restore-manager`);
  await manager.click();
  await expect(page.getByTestId("restore-manager-search")).toBeVisible();
  await expect(page.locator("#input-projectName")).toBeDisabled();
 });
}

test("stale remediation offers its permitted cancellation instead of a dead-end open request",async({page})=>{
 await session(page,[],"en");
 await page.route(`**${base}/`,r=>r.fulfill({json:{...project,can_create_restore_remediation:false}}));
 await page.route(`**${base}/members/*/permissions/`,r=>r.fulfill({status:404,json:{}}));
 await page.route(`**${base}/change-requests/`,r=>r.fulfill({json:[{id,status:"draft",reason:"Old archived correction",proposed_changes:{scope_description:"Scope"},restore_remediation_actions:["cancel"]}]}));
 await visit(page,`/projects/${id}/settings`,"en");
 await expect(page.getByTestId("cr-cancel-btn")).toBeVisible();
 await expect(page.getByTestId("cr-submit-btn")).toHaveCount(0);
});

for(const language of ["fa","en"] as const) {
 test(`${language} lost response survives reload and checks the original durable request`,async({page})=>{
  await session(page,[],language);let committed=false;let submitted:Record<string,string>|null=null;
  await page.route(`**${base}/`,r=>r.fulfill({json:{...project,status:committed?"active":"archived",can_restore_from_archive:!committed}}));
  await page.route(`**${base}/restore-preview/`,r=>r.fulfill({json:{project_id:id,project_name:project.project_name,to_status:"active",archive_cycle_id:id,lifecycle_version:1,confirmation_token:"signed",can_confirm:true,missing:[],remediation:[]}}));
  await page.route(`**${base}/restore/`,r=>{submitted=r.request().postDataJSON();committed=true;return r.abort();});
  await page.route(`**${base}/restore-attempts/*/`,r=>r.fulfill({json:{outcome:"completed",receipt:{id,project_id:id,project_name:project.project_name,archive_cycle_id:id,request_id:submitted?.request_id,actor:{id:"navigation-user",display_name:"Administrator"},restored_at:"2026-10-16T08:00:00Z",reason:submitted?.reason,from_status:"archived",to_status:"active"},current_project:{project_id:id,project_name:project.project_name,status:"active",archive_cycle_id:id,lifecycle_version:2}}}));
  await visit(page,routePath,language);await page.getByRole("button",{name:labels[language].action,exact:true}).click();
  const dialog=page.getByRole("dialog");await dialog.getByLabel(labels[language].reason,{exact:true}).fill("Preserve this exact reason");
  await dialog.getByRole("button",{name:labels[language].confirm,exact:true}).click();
  await expect(page.getByRole("alert").filter({hasText:language==="fa"?"نتیجهٔ درخواست مشخص نیست":"The result is unknown"})).toBeVisible();
  await page.reload();await page.locator(`#button-language-${language}`).click();
  await page.getByRole("button",{name:language==="fa"?"بررسی نتیجه":"Check result",exact:true}).click();
  await expect(page.getByTestId("restore-unresolved")).not.toBeVisible();
  expect(submitted?.reason).toBe("Preserve this exact reason");
 });
}

async function readyRecoveryMock(page: import("@playwright/test").Page) {
 await session(page,[],"en");
 await page.route(`**${base}/`,r=>r.fulfill({json:project}));
 await page.route(`**${base}/restore-preview/`,r=>r.fulfill({json:{project_id:id,project_name:project.project_name,to_status:"active",archive_cycle_id:id,lifecycle_version:1,confirmation_token:"signed",can_confirm:true,missing:[],remediation:[]}}));
}
async function sendRecoveryMock(page: import("@playwright/test").Page) {
 await visit(page,routePath,"en");await page.getByRole("button",{name:"Restore from archive",exact:true}).click();
 await page.getByRole("dialog").getByLabel("Reason",{exact:true}).fill("Frozen request content");
 await page.getByRole("dialog").getByRole("button",{name:"Confirm restoration",exact:true}).click();
}
function mockRestoreSuccess(payload:Record<string,string>) {
 return {outcome:"restored",receipt:{id,project_id:id,project_name:project.project_name,archive_cycle_id:id,request_id:payload.request_id,actor:{id:"navigation-user",display_name:"Administrator"},restored_at:"2026-10-16T08:00:00Z",reason:payload.reason,from_status:"archived",to_status:"active"},current_project:{project_id:id,project_name:project.project_name,status:"active",archive_cycle_id:id,lifecycle_version:2}};
}

test("not_recorded stays inconclusive and safe retry freezes the entire confirmed body",async({page})=>{
 await readyRecoveryMock(page);const bodies:Record<string,string>[]=[];
 await page.route(`**${base}/restore/`,r=>{const payload=r.request().postDataJSON();bodies.push(payload);return bodies.length===1?r.abort():r.fulfill({json:mockRestoreSuccess(payload)});});
 await page.route(`**${base}/restore-attempts/*/`,r=>r.fulfill({json:{outcome:"not_recorded",receipt:null,current_project:{status:"archived"}}}));
 await sendRecoveryMock(page);await expect(page.getByRole("alert").filter({hasText:"The result is unknown"})).toBeVisible();
 await page.getByRole("button",{name:"Check result",exact:true}).click();
 await expect(page.getByRole("alert").filter({hasText:"may still be running"})).toBeVisible();
 await page.getByRole("button",{name:"Retry same request",exact:true}).click();
 await expect(page.getByRole("dialog")).not.toBeVisible();
 expect(bodies).toHaveLength(2);expect(bodies[1]).toEqual(bodies[0]);
});

test("authentication refresh retries the exact restore payload",async({page})=>{
 await readyRecoveryMock(page);const bodies:Record<string,string>[]=[];
 await page.route("**/api/auth/token/refresh/",r=>r.fulfill({json:{access:"renewed-token",refresh:"navigation-test"}}));
 await page.route(`**${base}/restore/`,r=>{const payload=r.request().postDataJSON();bodies.push(payload);return bodies.length===1?r.fulfill({status:401,json:{detail:"Expired"}}):r.fulfill({json:mockRestoreSuccess(payload)});});
 await sendRecoveryMock(page);await expect(page.getByRole("dialog")).not.toBeVisible();
 expect(bodies).toHaveLength(2);expect(bodies[1]).toEqual(bodies[0]);
});

test("dismissal does not cancel a sent operation, and logout clears its retained reason",async({page})=>{
 await readyRecoveryMock(page);await page.route(`**${base}/restore/`,r=>r.abort());
 await sendRecoveryMock(page);await expect(page.getByRole("alert").filter({hasText:"The result is unknown"})).toBeVisible();
 await page.keyboard.press("Escape");await expect(page.getByTestId("restore-unresolved")).toBeVisible();
 expect(await page.evaluate(()=>Object.keys(sessionStorage).filter(k=>k.startsWith("velora:archive-restore:")).length)).toBe(1);
 await page.locator("#button-appHeaderSignOut").click();
 await expect(page).toHaveURL(/\/login/);
 await expect.poll(()=>page.evaluate(()=>Object.keys(sessionStorage).filter(k=>k.startsWith("velora:archive-restore:")).length)).toBe(0);
});

test("lost authority stops retry and clears the retained confirmation",async({page})=>{
 await readyRecoveryMock(page);await page.route(`**${base}/restore/`,r=>r.abort());
 await page.route(`**${base}/restore-attempts/*/`,r=>r.fulfill({status:403,json:{error:{code:"permission_denied",message:"Denied",details:{}}}}));
 await sendRecoveryMock(page);await expect(page.getByRole("alert").filter({hasText:"The result is unknown"})).toBeVisible();
 await page.getByRole("button",{name:"Check result",exact:true}).click();
 await expect(page.getByRole("button",{name:"Restore from archive",exact:true})).toHaveCount(0);
 await expect(page.getByRole("button",{name:"Retry same request",exact:true})).toHaveCount(0);
 expect(await page.evaluate(()=>Object.keys(sessionStorage).filter(k=>k.startsWith("velora:archive-restore:")).length)).toBe(0);
});

test("a late restoration response after logout does not disclose the old project",async({page})=>{
 await readyRecoveryMock(page);
 let deliver:(()=>Promise<void>)|undefined;
 await page.route(`**${base}/restore/`,async route=>{
  const payload=route.request().postDataJSON();
  await new Promise<void>(resolve=>{deliver=async()=>{await route.fulfill({json:mockRestoreSuccess(payload)});resolve();};});
 });
 await sendRecoveryMock(page);await expect.poll(()=>Boolean(deliver)).toBe(true);
 await page.keyboard.press("Escape");await page.locator("#button-appHeaderSignOut").click();
 await expect(page).toHaveURL(/\/login/);
 await expect.poll(()=>page.evaluate(()=>localStorage.getItem("auth_user"))).toBeNull();
 await deliver!();await page.waitForLoadState("networkidle");
 await expect(page.getByText("Archive test project was restored to Active.",{exact:true})).toHaveCount(0);
});

for(const language of ["fa","en"] as const) {
 test(`${language} history-only viewer sees safe paginated provenance and localized empty state`,async({page},testInfo)=>{
  await session(page,[],language);
  await page.route(`**${base}/`,r=>r.fulfill({json:{...project,status:"completed",can_restore_from_archive:false,can_view_restore_history:true}}));
  await page.route(`**${base}/members/*/permissions/`,r=>r.fulfill({status:404,json:{}}));
  await page.route(`**${base}/restore-history/*`,r=>{
   const second=new URL(r.request().url()).searchParams.get("page")==="2";
   return r.fulfill({json:{count:51,next:second?null:"?page=2",previous:second?"?page=1":null,results:second?[]:[{id,project_id:id,project_name:"Original project",archive_cycle_id:id,request_id:id,actor:{id,display_name:"Original administrator"},restored_at:"2026-10-16T08:00:00Z",reason:"Archived by mistake",from_status:"archived",to_status:"suspended"}]}});
  });
  await visit(page,routePath,language);
  const history=page.getByTestId("restore-history");await expect(history).toContainText("Original administrator");
  await expect(history).toContainText("Archived by mistake");await expect(history).toContainText("Original project");
  await expect(history).toContainText(language==="fa"?"تعلیق":"Suspended");
  await expect(history.locator("time")).toHaveAttribute("datetime","2026-10-16T08:00:00Z");
  await expect(page.getByRole("button",{name:labels[language].action,exact:true})).toHaveCount(0);
  await page.screenshot({path:testInfo.outputPath(`history-${language}.png`),fullPage:true});
  await history.getByRole("button",{name:language==="fa"?"صفحهٔ بعد":"Next page",exact:true}).click();
  await expect(history).toContainText(language==="fa"?"بازگردانی ثبت نشده است":"No restoration is recorded");
 });
}

for(const language of ["fa","en"] as const) {
 for(const code of ["restore_not_applied","archive_already_restored","permission_denied"] as const) {
  test(`${language} actionable ${code} outcome`,async({page})=>{
   await session(page,[],language);let ended=false;const bodies:Record<string,string>[]=[];
   await page.route(`**${base}/`,r=>r.fulfill({json:{...project,status:ended?"completed":"archived",can_restore_from_archive:!ended}}));
   await page.route(`**${base}/restore-preview/`,r=>r.fulfill({json:{project_id:id,project_name:project.project_name,to_status:"completed",confirmation_token:"signed",can_confirm:true,missing:[],remediation:[]}}));
   await page.route(`**${base}/restore/`,r=>{
    const payload=r.request().postDataJSON();bodies.push(payload);
    if(bodies.length===2)return r.fulfill({json:mockRestoreSuccess(payload)});
    ended=code==="archive_already_restored";
    return r.fulfill({status:code==="restore_not_applied"?503:code==="permission_denied"?403:409,json:{error:{code,message:"Contract error",details:{}}}});
   });
   await visit(page,routePath,language);await page.getByRole("button",{name:labels[language].action,exact:true}).click();
   await page.getByRole("dialog").getByLabel(labels[language].reason,{exact:true}).fill("Confirmed reason");
   await page.getByRole("dialog").getByRole("button",{name:labels[language].confirm,exact:true}).click();
   const text=code==="restore_not_applied"?(language==="fa"?"بازگردانی انجام نشد":"Restoration was not applied"):code==="permission_denied"?(language==="fa"?"فقط مدیر سیستم":"Only a system administrator"):(language==="fa"?"این دورهٔ بایگانی را بازگردانده":"already restored");
   await expect(page.getByRole("alert").filter({hasText:text}).first()).toBeVisible();
   if(code==="restore_not_applied") {
    await page.getByRole("dialog").getByRole("button",{name:language==="fa"?"تلاش مجدد همین درخواست":"Retry same request",exact:true}).click();
    await expect(page.getByRole("dialog")).not.toBeVisible();expect(bodies[1]).toEqual(bodies[0]);
   } else expect(await page.evaluate(()=>Object.keys(sessionStorage).filter(k=>k.startsWith("velora:archive-restore:")).length)).toBe(0);
  });
 }
 test(`${language} changed context requires a loaded fresh confirmation`,async({page})=>{
  await session(page,[],language);let previews=0;let release:(()=>Promise<void>)|undefined;
  await page.route(`**${base}/`,r=>r.fulfill({json:project}));
  await page.route(`**${base}/restore-preview/`,async r=>{
   previews++;const response={json:{project_id:id,project_name:project.project_name,to_status:"completed",confirmation_token:previews===1?"old":"fresh",can_confirm:true,missing:[],remediation:[]}};
   if(previews===1)await r.fulfill(response);else await new Promise<void>(resolve=>{release=async()=>{await r.fulfill(response);resolve();};});
  });
  const bodies:Record<string,string>[]=[];
  await page.route(`**${base}/restore/`,r=>{bodies.push(r.request().postDataJSON());return bodies.length===1?r.fulfill({status:409,json:{error:{code:"restore_context_changed",message:"Changed",details:{}}}}):r.fulfill({json:mockRestoreSuccess(bodies[1])});});
  await visit(page,routePath,language);await page.getByRole("button",{name:labels[language].action,exact:true}).click();
  const dialog=page.getByRole("dialog");await dialog.getByLabel(labels[language].reason,{exact:true}).fill("Reconfirmed changed context");
  const confirm=dialog.getByRole("button",{name:labels[language].confirm,exact:true});await confirm.click();
  await expect.poll(()=>Boolean(release)).toBe(true);await expect(confirm).toBeDisabled();
  await release!();await expect(confirm).toBeEnabled();await confirm.click();await expect(dialog).not.toBeVisible();
  expect(bodies[0].confirmation_token).toBe("old");expect(bodies[1].confirmation_token).toBe("fresh");expect(bodies[1].request_id).not.toBe(bodies[0].request_id);
 });
}

test("a different authenticated account removes the previous account's pending attempt",async({page})=>{
 await readyRecoveryMock(page);
 await page.addInitScript(({id})=>sessionStorage.setItem(`velora:archive-restore:previous-account:${id}`,JSON.stringify({user_id:"previous-account",project_id:id,request_id:id,confirmation_token:"private-old-token",reason:"Previous private reason"})),{id});
 await visit(page,routePath,"en");
 await expect.poll(()=>page.evaluate(()=>Object.keys(sessionStorage).filter(k=>k.startsWith("velora:archive-restore:")).length)).toBe(0);
 await expect(page.getByText("Previous private reason")).toHaveCount(0);
});

// Use the framework's mounted client router, preserving cached route content
// and QueryClient (raw popstate without router history metadata may reload).
async function cachedNavigate(page: import("@playwright/test").Page, path: string) {
 await page.evaluate(async path=>{
  const router=(window as unknown as {__reactRouterDataRouter:{navigate:(path:string)=>Promise<void>}}).__reactRouterDataRouter;
  await router.navigate(path);
 },path);
 await expect(page).toHaveURL(new RegExp(path+"$"));
}
const otherId="22222222-2222-4222-8222-222222222222";
for(const language of ["fa","en"] as const) {
 test(`${language} cached projects keep independent pending requests after a late response`,async({page})=>{
  await session(page,[],language);
  const other={...project,project_id:otherId,project_name:"Independent B"};
  await page.route(`**${base}/`,r=>r.fulfill({json:project}));
  await page.route(`**/api/v1/projects/${otherId}/`,r=>r.fulfill({json:other}));
  await page.route(`**${base}/restore-preview/`,r=>r.fulfill({json:{project_id:id,project_name:project.project_name,to_status:"active",confirmation_token:"signed-A",can_confirm:true,missing:[]}}));
  let deliver:(()=>Promise<void>)|undefined;
  await page.route(`**${base}/restore/`,async r=>{
   const payload=r.request().postDataJSON();
   await new Promise<void>(resolve=>{deliver=async()=>{await r.fulfill({json:mockRestoreSuccess(payload)});resolve();};});
  });
  const checks:string[]=[];
  await page.route(`**/api/v1/projects/${otherId}/restore-attempts/*/`,r=>{checks.push(r.request().url());return r.fulfill({json:{outcome:"not_recorded",receipt:null,current_project:other}});});
  await visit(page,`/projects/${otherId}/overview`,language); // Warm B's real project query.
  await expect(page.getByRole("button",{name:labels[language].action,exact:true})).toBeVisible();
  await page.evaluate(({otherId})=>sessionStorage.setItem(`velora:archive-restore:navigation-user:${otherId}`,JSON.stringify({user_id:"navigation-user",project_id:otherId,request_id:otherId,confirmation_token:"signed-B",reason:"Private B reason"})),{otherId});
  await cachedNavigate(page,routePath);await page.locator(`#button-language-${language}`).click();
  await page.getByRole("button",{name:labels[language].action,exact:true}).click();
  await page.getByRole("dialog").getByLabel(labels[language].reason,{exact:true}).fill("Independent A reason");
  await page.getByRole("dialog").getByRole("button",{name:labels[language].confirm,exact:true}).click();
  await expect.poll(()=>Boolean(deliver)).toBe(true);await page.keyboard.press("Escape");
  await cachedNavigate(page,`/projects/${otherId}/overview`);await page.locator(`#button-language-${language}`).click();
  await expect(page.getByTestId("restore-unresolved")).toBeVisible();
  await deliver!();await page.waitForLoadState("networkidle");
  await expect(page.getByTestId("restore-unresolved")).toBeVisible();
  const check=page.getByRole("button",{name:language==="fa"?"بررسی نتیجه":"Check result",exact:true});
  await expect(check).toBeEnabled();await check.click();await expect.poll(()=>checks.length).toBe(1);
  expect(checks[0]).toContain(otherId+"/restore-attempts/"+otherId);
  expect(await page.evaluate(otherId=>JSON.parse(sessionStorage.getItem(`velora:archive-restore:navigation-user:${otherId}`)!).reason,otherId)).toBe("Private B reason");
  await cachedNavigate(page,routePath);
  await expect(page.getByTestId("restore-unresolved")).toBeVisible(); // Origin still has a safe lookup.
 });
}
for(const language of ["fa","en"] as const) {
 test(`${language} late response cannot clear a newly signed-in account attempt`,async({page})=>{
  await session(page,[],language);
  let activeUser={id:"navigation-user",full_name:"Navigation tester",roles:[] as string[]};
  await page.route("**/api/auth/profile/",r=>r.fulfill({json:activeUser}));
  await page.route("**/api/auth/login/",r=>{activeUser={id:"second-account",full_name:"Second account",roles:[]};return r.fulfill({json:{access:"second-token",refresh:"second-refresh",user:activeUser}});});
  await page.route(`**${base}/`,r=>r.fulfill({json:project}));
  await page.route(`**${base}/restore-preview/`,r=>r.fulfill({json:{project_id:id,project_name:project.project_name,to_status:"active",confirmation_token:"first-account-token",can_confirm:true,missing:[]}}));
  let deliver:(()=>Promise<void>)|undefined;
  await page.route(`**${base}/restore/`,async r=>{const payload=r.request().postDataJSON();await new Promise<void>(resolve=>{deliver=async()=>{await r.fulfill({json:mockRestoreSuccess(payload)});resolve();};});});
  await visit(page,routePath,language);await page.getByRole("button",{name:labels[language].action,exact:true}).click();
  await page.getByRole("dialog").getByLabel(labels[language].reason,{exact:true}).fill("Old account secret reason");
  await page.getByRole("dialog").getByRole("button",{name:labels[language].confirm,exact:true}).click();
  await expect.poll(()=>Boolean(deliver)).toBe(true);await page.keyboard.press("Escape");
  await page.locator("#button-appHeaderSignOut").click();await expect(page).toHaveURL(/\/login/);
  await page.getByTestId("login-phone-input").fill("+10000000009");await page.getByTestId("login-password-input").fill("test-password");await page.getByTestId("login-submit-btn").click();
  await expect(page).not.toHaveURL(/\/login/);
  await page.evaluate(id=>sessionStorage.setItem(`velora:archive-restore:second-account:${id}`,JSON.stringify({user_id:"second-account",project_id:id,request_id:id,confirmation_token:"second-account-token",reason:"Second account private reason"})),id);
  await cachedNavigate(page,routePath);await expect(page.getByTestId("restore-unresolved")).toBeVisible();
  await deliver!();await page.waitForLoadState("networkidle");
  await expect(page.getByTestId("restore-unresolved")).toBeVisible();
  await expect(page.getByText(language==="fa"?"پروژهٔ Archive test project به وضعیت فعال بازگردانده شد.":"Archive test project was restored to Active.",{exact:true})).toHaveCount(0);
  expect(await page.evaluate(()=>Object.keys(sessionStorage).filter(k=>k.startsWith("velora:archive-restore:navigation-user:")).length)).toBe(0);
 });
}

for(const language of ["fa","en"] as const) {
 for(const cached of [false,true])for(const failure of [403,404,409,500,"network"] as const) {
  test(`${language} ${cached?"cached":"initial"} preview failure ${failure} offers a read-only retry`,async({page})=>{
   await session(page,[],language);let fail=false;let previews=0;const bodies:Record<string,string>[]=[];
   await page.route(`**${base}/`,r=>r.fulfill({json:project}));
   await page.route(`**${base}/restore-preview/`,r=>{
    previews++;
    if(fail)return failure==="network"?r.abort():r.fulfill({status:failure,json:{error:{code:failure===403?"permission_denied":"preview_error",message:"Server detail"}}});
    return r.fulfill({json:{project_id:id,project_name:project.project_name,to_status:"active",confirmation_token:previews===1?"old-preview":"fresh-preview",can_confirm:true,missing:[]}});
   });
   await page.route(`**${base}/restore/`,r=>{bodies.push(r.request().postDataJSON());return r.fulfill({json:mockRestoreSuccess(bodies[0])});});
   await visit(page,routePath,language);
   if(cached){
    await page.getByRole("button",{name:labels[language].action,exact:true}).click();
    await expect(page.getByRole("dialog").getByLabel(labels[language].reason,{exact:true})).toBeVisible();
    await page.getByRole("dialog").getByRole("button",{name:labels[language].cancel,exact:true}).click();
   }
   fail=true;await page.getByRole("button",{name:labels[language].action,exact:true}).click();
   const dialog=page.getByRole("dialog");
   const message=failure===403?(language==="fa"?"مجوز مشاهدهٔ پیش‌نمایش":"permission to preview"):failure===404||failure===409?(language==="fa"?"پروژه در دسترس نیست یا تغییر کرده":"project is unavailable or has changed"):(language==="fa"?"پیش‌نمایش بازگردانی بارگیری نشد":"preview could not be loaded");
   await expect(dialog.getByRole("alert")).toContainText(message);
   await expect(dialog.getByRole("button",{name:labels[language].confirm,exact:true})).toBeDisabled();
   expect(bodies).toHaveLength(0);expect(await page.evaluate(()=>Object.keys(sessionStorage).filter(k=>k.startsWith("velora:archive-restore:")).length)).toBe(0);
   fail=false;await dialog.getByRole("button",{name:language==="fa"?"تلاش دوباره برای پیش‌نمایش":"Retry preview",exact:true}).click();
   await expect(dialog.getByRole("alert")).toHaveCount(0);
   await dialog.getByLabel(labels[language].reason,{exact:true}).fill("Explicit confirmation after preview retry");
   await dialog.getByRole("button",{name:labels[language].confirm,exact:true}).click();
   await expect(dialog).not.toBeVisible();expect(bodies).toHaveLength(1);expect(bodies[0].confirmation_token).toBe("fresh-preview");
  });
 }
}

for(const language of ["fa","en"] as const)for(const remediation of ["manager","protected"] as const) {
 test(`${language} unsent reason survives ${remediation} remediation and requires fresh confirmation`,async({page})=>{
  await session(page,[],language);let ready=false;let previews=0;const bodies:Record<string,string>[]=[];
  await page.route(`**${base}/`,r=>r.fulfill({json:{...project,can_edit_manager_for_restore:true,can_create_restore_remediation:true}}));
  await page.route(`**${base}/change-requests/`,r=>r.fulfill({json:[]}));
  await page.route(`**${base}/members/*/permissions/`,r=>r.fulfill({status:404,json:{}}));
  await page.route(`**${base}/restore-preview/`,r=>{previews++;return r.fulfill({json:{project_id:id,project_name:project.project_name,to_status:"active",confirmation_token:`preview-${previews}`,can_confirm:ready,missing:ready?[]:["project_manager","scope_description","budget_approved"]}});});
  await page.route(`**${base}/restore/`,r=>{bodies.push(r.request().postDataJSON());return r.fulfill({json:mockRestoreSuccess(bodies[0])});});
  await visit(page,routePath,language);await page.getByRole("button",{name:labels[language].action,exact:true}).click();
  const reason="Unsent reason across "+remediation;await page.getByRole("dialog").getByLabel(labels[language].reason,{exact:true}).fill(reason);
  await page.getByRole("dialog").getByRole("link",{name:remediation==="manager"?(language==="fa"?"تکمیل مدیر پروژه":"Complete project manager"):(language==="fa"?"بررسی درخواست‌های تغییر":"Review change requests"),exact:true}).first().click();
  await expect(page).toHaveURL(/\/settings#/);
  await expect(page.getByTestId(remediation==="manager"?"restore-manager-search":"cr-reason")).toBeVisible();
  expect(bodies).toHaveLength(0);expect(await page.evaluate(()=>Object.keys(sessionStorage).filter(k=>k.startsWith("velora:archive-restore:")).length)).toBe(0);
  ready=true;await cachedNavigate(page,routePath);await page.locator(`#button-language-${language}`).click();
  expect(bodies).toHaveLength(0);await page.getByRole("button",{name:labels[language].action,exact:true}).click();
  const dialog=page.getByRole("dialog");await expect(dialog.getByLabel(labels[language].reason,{exact:true})).toHaveValue(reason);
  await expect.poll(()=>previews).toBe(2);expect(bodies).toHaveLength(0);
  await dialog.getByRole("button",{name:labels[language].confirm,exact:true}).click();await expect(dialog).not.toBeVisible();
  expect(bodies).toHaveLength(1);expect(bodies[0].reason).toBe(reason);expect(bodies[0].confirmation_token).toBe("preview-2");
 });
}

async function fetchActualPortfolioQueries(page:import("@playwright/test").Page) {
 return page.evaluate(async()=>{
  const clientPath="/src/app/lib/react-query.ts",summaryPath="/src/app/lib/api/central-data.ts",dashboardPath="/src/app/lib/api/dashboards.ts";
  const {queryClient}=await import(/* @vite-ignore */ clientPath);
  const {fetchPortfolioSummary}=await import(/* @vite-ignore */ summaryPath);
  const {fetchPortfolioDashboard}=await import(/* @vite-ignore */ dashboardPath);
  const before=["portfolio-summary","portfolio-dashboard"].map(key=>queryClient.getQueryState([key])?.isInvalidated??false);
  await Promise.all([queryClient.fetchQuery({queryKey:["portfolio-summary"],queryFn:fetchPortfolioSummary}),queryClient.fetchQuery({queryKey:["portfolio-dashboard"],queryFn:()=>fetchPortfolioDashboard()})]);
  return before;
 });
}
for(const language of ["fa","en"] as const)for(const outcome of ["restored","replayed","completed","cancel","not_recorded"] as const) {
 test(`${language} warmed portfolio queries refresh only on evidenced ${outcome}`,async({page})=>{
  await session(page,[],language);const counts={summary:0,dashboard:0};let payload:Record<string,string>={};
  await page.route("**/api/v1/portfolio/summary/",r=>{counts.summary++;return r.fulfill({json:{totals:{project_count:0},totals_by_currency:{}}});});
  await page.route("**/api/v1/portfolio/dashboard/",r=>{counts.dashboard++;return r.fulfill({json:{projects:[]}});});
  await page.route(`**${base}/`,r=>r.fulfill({json:project}));
  await page.route(`**${base}/restore-preview/`,r=>r.fulfill({json:{project_id:id,project_name:project.project_name,to_status:"active",confirmation_token:"signed",can_confirm:true,missing:[]}}));
  await page.route(`**${base}/restore/`,r=>{payload=r.request().postDataJSON();return outcome==="completed"||outcome==="not_recorded"?r.abort():r.fulfill({json:{...mockRestoreSuccess(payload),outcome}});});
  await page.route(`**${base}/restore-attempts/*/`,r=>r.fulfill({json:{...mockRestoreSuccess(payload),outcome:outcome==="completed"?"completed":"not_recorded"}}));
  await visit(page,routePath,language);await expect(page.getByRole("button",{name:labels[language].action,exact:true})).toBeVisible();
  await fetchActualPortfolioQueries(page);expect(counts).toEqual({summary:1,dashboard:1});
  await page.getByRole("button",{name:labels[language].action,exact:true}).click();
  const dialog=page.getByRole("dialog");
  if(outcome==="cancel")await dialog.getByRole("button",{name:labels[language].cancel,exact:true}).click();
  else {
   await dialog.getByLabel(labels[language].reason,{exact:true}).fill("Confirmed portfolio refresh");
   await dialog.getByRole("button",{name:labels[language].confirm,exact:true}).click();
   if(outcome==="completed"||outcome==="not_recorded") {
    await expect(dialog.getByRole("alert")).toContainText(language==="fa"?"نتیجهٔ درخواست مشخص نیست":"The result is unknown");
    await dialog.getByRole("button",{name:language==="fa"?"بررسی نتیجه":"Check result",exact:true}).click();
    if(outcome==="not_recorded")await expect(dialog.getByRole("alert")).toContainText(language==="fa"?"ممکن است":"may still be running");
   }
   if(outcome!=="not_recorded")await expect(dialog).not.toBeVisible();
  }
  const known=["restored","replayed","completed"].includes(outcome);
  const invalidated=await fetchActualPortfolioQueries(page);
  expect(invalidated).toEqual([known,known]);
  expect(counts).toEqual({summary:known?2:1,dashboard:known?2:1});
 });
}

for(const language of ["fa","en"] as const) {
 test(`${language} unsent drafts are account and project scoped and cleared on abandonment or logout`,async({page})=>{
  await session(page,[],language);
  await page.addInitScript(({id,otherId})=>{
   for(const [user,project,reason] of [["navigation-user",id,"Current draft"],["navigation-user",otherId,"Other project private draft"],["old-account",id,"Old account private draft"]])sessionStorage.setItem(`velora:archive-restore-draft:${user}:${project}`,JSON.stringify({user_id:user,project_id:project,reason}));
  },{id,otherId});
  await page.route(`**${base}/`,r=>r.fulfill({json:{...project,can_edit_manager_for_restore:true}}));
  await page.route(`**${base}/change-requests/`,r=>r.fulfill({json:[]}));
  await page.route(`**${base}/restore-preview/`,r=>r.fulfill({json:{project_id:id,project_name:project.project_name,to_status:"active",confirmation_token:"fresh",can_confirm:false,missing:["project_manager"]}}));
  await visit(page,routePath,language);await page.getByRole("button",{name:labels[language].action,exact:true}).click();
  const dialog=page.getByRole("dialog");await expect(dialog.getByLabel(labels[language].reason,{exact:true})).toHaveValue("Current draft");
  expect(await page.evaluate(()=>Object.keys(sessionStorage).some(k=>k.startsWith("velora:archive-restore-draft:old-account:")))).toBe(false);
  await dialog.getByRole("button",{name:labels[language].cancel,exact:true}).click();
  expect(await page.evaluate(id=>sessionStorage.getItem(`velora:archive-restore-draft:navigation-user:${id}`),id)).toBeNull();
  expect(await page.evaluate(otherId=>sessionStorage.getItem(`velora:archive-restore-draft:navigation-user:${otherId}`),otherId)).not.toBeNull();
  await page.getByRole("button",{name:labels[language].action,exact:true}).click();
  await expect(dialog.getByLabel(labels[language].reason,{exact:true})).toHaveValue("");
  await dialog.getByLabel(labels[language].reason,{exact:true}).fill("Retained until logout");
  await dialog.getByRole("link",{name:language==="fa"?"تکمیل مدیر پروژه":"Complete project manager",exact:true}).click();
  await expect(page.getByTestId("restore-manager-search")).toBeVisible();
  await page.locator("#button-appHeaderSignOut").click();await expect(page).toHaveURL(/\/login/);
  expect(await page.evaluate(()=>Object.keys(sessionStorage).filter(k=>k.startsWith("velora:archive-restore")).length)).toBe(0);
 });
}
