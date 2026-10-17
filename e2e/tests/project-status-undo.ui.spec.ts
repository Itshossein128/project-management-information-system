import { expect, test, type Page } from "@playwright/test";
import { session, visit } from "../helpers/navigation";
const id="11111111-1111-4111-8111-111111111111";
const base=`/api/v1/projects/${id}`;
const path=`/projects/${id}/overview`;
const labels={en:{resume:"Resume",undo_completion:"Undo completion",reason:"Reason",confirm:"Confirm status correction",cancel:"Cancel"},fa:{resume:"ازسرگیری",undo_completion:"بازگردانی خاتمه",reason:"دلیل",confirm:"تأیید اصلاح وضعیت",cancel:"لغو"}};
type Operation="resume"|"undo_completion";
const variants=[['resume','active'],['undo_completion','active'],['undo_completion','suspended']] as const;
async function setup(page:Page,language:"fa"|"en",operation:Operation,target:string) {
 await session(page,[],language);
 let status=operation==='resume'?'suspended':'completed';let writes=0;
 const project=()=>({project_id:id,project_name:"Status test project",project_code:"UNDO",status,currency:"IRR",can_resume_with_confirmation:status==='suspended'&&operation==='resume',can_undo_completion:status==='completed',can_view_status_undo_history:false});
 await page.route(`**${base}/`,r=>r.fulfill({json:project()}));
 await page.route(`**${base}/members/*/permissions/`,r=>r.fulfill({json:{effective:{edit_project:true,view_project:true}}}));
 await page.route(`**${base}/${operation==='resume'?'resume-preview':'undo-completion-preview'}/`,r=>r.fulfill({json:{project_id:id,project_name:"Status test project",operation,source_event_id:id,from_status:status,to_status:target,lifecycle_version:1,confirmation_token:"signed",can_confirm:true,missing:[],remediation:[]}}));
 await page.route(`**${base}/${operation==='resume'?'resume':'undo-completion'}/`,r=>{
  writes++;const body=r.request().postDataJSON();status=target;
  return r.fulfill({json:{outcome:"applied",receipt:{id,project_id:id,project_name:"Status test project",operation,source_event_id:id,request_id:body?.request_id,reason:body?.reason,from_status:operation==='resume'?'suspended':'completed',to_status:target,performed_at:"2026-10-17T08:00:00Z",actor:{id:"navigation-user",display_name:"Administrator"},source_event:{id,kind:operation==='resume'?'suspend':'complete',from_status:target,to_status:operation==='resume'?'suspended':'completed',actor:{id:"original",display_name:"Original actor"},occurred_at:"2026-10-17T07:00:00Z",project_name:"Status test project"}},current_project:{...project(),lifecycle_version:2}}});
 });
 return {writes:()=>writes};
}
for(const language of ['fa','en'] as const) {
 test(`${language} keyboard tab order reaches explicit confirmation`,async({page})=>{
  const state=await setup(page,language,'resume','active');await visit(page,path,language);
  await page.getByRole('button',{name:labels[language].resume,exact:true}).click();const dialog=page.getByRole('dialog');
  await dialog.getByLabel(labels[language].reason,{exact:true}).fill('Explicit keyboard correction');
  await page.keyboard.press('Tab');await expect(dialog.getByRole('button',{name:labels[language].cancel,exact:true})).toBeFocused();
  await page.keyboard.press('Tab');await expect(dialog.getByRole('button',{name:labels[language].confirm,exact:true})).toBeFocused();
  expect(state.writes()).toBe(0);await page.keyboard.press('Enter');await expect(dialog).not.toBeVisible();expect(state.writes()).toBe(1);
 });
 test(`${language} history failure retries into a localized empty state`,async({page})=>{
  await setup(page,language,'resume','active');
  await page.route(`**${base}/`,r=>r.fulfill({json:{project_id:id,project_name:'Status test project',status:'active',can_view_status_undo_history:true}}));
  let failed=true;let reads=0;
  await page.route(`**${base}/status-undo-history/**`,r=>{reads++;return failed?r.fulfill({status:503,json:{error:{code:'unavailable',message:'Unavailable'}}}):r.fulfill({json:{count:0,results:[],next:null,previous:null}});});
  await visit(page,path,language);const history=page.getByTestId('status-undo-history');const retry=history.getByRole('button');await expect(retry).toBeVisible();
  failed=false;await retry.click();await expect(history).toContainText(language==='fa'?'هنوز اصلاح وضعیتی ثبت نشده است.':'No status correction has been recorded.');
  expect(reads).toBe(2);await expect(history).not.toContainText('projectStatusUndo.');
 });
}
for(const language of ['fa','en'] as const) for(const [operation,target] of variants) {
 test(`${language} ${operation} to ${target} confirms and cancels without immediate write`,async({page})=>{
  const state=await setup(page,language,operation,target);await visit(page,path,language);
  await page.getByRole('button',{name:labels[language][operation],exact:true}).click();
  // Detect the old immediate resume mutation behavior, independently of selectors.
  await expect.poll(state.writes).toBe(0);
  const dialog=page.getByRole('dialog');await expect(dialog).toBeVisible();await expect(dialog).toContainText('Status test project');
  await expect(dialog.getByTestId('status-undo-target')).toContainText(language==='fa'?(target==='active'?'فعال':'تعلیق‌شده'):(target==='active'?'Active':'Suspended'));
  const confirm=dialog.getByRole('button',{name:labels[language].confirm,exact:true});await expect(confirm).toBeDisabled();
  await dialog.getByLabel(labels[language].reason,{exact:true}).fill('   ');await expect(confirm).toBeDisabled();
  await page.keyboard.press('Escape');await expect(dialog).not.toBeVisible();expect(state.writes()).toBe(0);
 });
 test(`${language} ${operation} to ${target} sends one explicit reasoned correction`,async({page})=>{
  const state=await setup(page,language,operation,target);await visit(page,path,language);
  await page.getByRole('button',{name:labels[language][operation],exact:true}).click();const dialog=page.getByRole('dialog');
  await dialog.getByLabel(labels[language].reason,{exact:true}).fill('Mistaken status choice');
  await dialog.getByRole('button',{name:labels[language].confirm,exact:true}).click();
  await expect(dialog).not.toBeVisible();expect(state.writes()).toBe(1);
 });
}

for(const language of ['fa','en'] as const) for(const anchor of ['restore-manager','project-change-requests']) {
 test(`${language} US2 repair ${anchor} retains unsent reason with fresh preview`,async({page})=>{
  await setup(page,language,'undo_completion','active');let reads=0;
  await page.route(`**${base}/`,r=>r.fulfill({json:{project_id:id,project_name:'Status test project',project_code:'UNDO',status:'completed',completed_from_status:'active',can_undo_completion:true,status_undo_remediation:{operation:'undo_completion',source_event_id:id,can_edit_manager:true,can_create_change_request:true},project_manager:null,scope_description:'',contract_amount:null}}));
  await page.route(`**${base}/change-requests/`,r=>r.fulfill({json:[]}));
  await page.route(`**${base}/undo-completion-preview/`,r=>{reads++;return r.fulfill({json:{project_id:id,project_name:'Status test project',operation:'undo_completion',source_event_id:id,from_status:'completed',to_status:'active',lifecycle_version:reads,confirmation_token:`signed-${reads}`,can_confirm:false,missing:['project_manager','scope_description','budget_approved'],remediation:['project_manager','scope_description','budget_approved'].map(field=>({field,action:field==='project_manager'?'project_settings':'project_change_request',can_perform:true}))}});});
  await visit(page,path,language);await page.getByRole('button',{name:labels[language].undo_completion,exact:true}).click();const dialog=page.getByRole('dialog');
  await dialog.getByLabel(labels[language].reason,{exact:true}).fill('Keep the exact unsent correction reason');
  await expect(dialog.getByRole('listitem')).toHaveCount(3);
  await dialog.locator(`a[href$="#${anchor}"]`).first().click();
  if(anchor==='restore-manager')await expect(page.getByTestId('restore-manager-search')).toBeVisible();
  else {await expect(page.getByTestId('cr-reason')).toBeVisible();await expect(page.getByTestId('cr-field-employer')).toBeHidden();}
  await visit(page,path,language);await page.getByRole('button',{name:labels[language].undo_completion,exact:true}).click();
  await expect(page.getByRole('dialog').getByLabel(labels[language].reason,{exact:true})).toHaveValue('Keep the exact unsent correction reason');expect(reads).toBeGreaterThan(1);
 });
}

test('US2 stale completed repair retains permitted cancel after status becomes active',async({page})=>{
 await setup(page,'en','undo_completion','active');
 await page.route(`**${base}/`,r=>r.fulfill({json:{project_id:id,project_name:'Status test project',status:'active',can_undo_completion:false}}));
 await page.route(`**${base}/change-requests/`,r=>r.fulfill({json:[{id,status:'draft',reason:'Old completion repair',proposed_changes:{scope_description:'Scope'},restore_completion_event_id:id,restore_remediation_actions:['cancel']}]}));
 await visit(page,`/projects/${id}/settings`,'en');await expect(page.getByTestId('cr-cancel-btn')).toBeVisible();await expect(page.getByTestId('cr-submit-btn')).toHaveCount(0);
});

for(const language of ['fa','en'] as const) for(const operation of ['resume','undo_completion'] as const) {
 test(`${language} US3 ${operation} unknown result survives reload and freezes exact retry`,async({page})=>{
  await setup(page,language,operation,'active');const bodies:Record<string,string>[]=[];
  await page.route(`**${base}/${operation==='resume'?'resume':'undo-completion'}/`,r=>{bodies.push(r.request().postDataJSON());return r.abort();});
  await page.route(`**${base}/status-undo-attempts/${operation}/*/`,r=>r.fulfill({json:{outcome:'not_recorded',receipt:null,current_project:{status:operation==='resume'?'suspended':'completed'}}}));
  await visit(page,path,language);await page.getByRole('button',{name:labels[language][operation],exact:true}).click();await page.getByRole('dialog').getByLabel(labels[language].reason,{exact:true}).fill('Frozen reason across reload');await page.getByRole('dialog').getByRole('button',{name:labels[language].confirm,exact:true}).click();
  await expect(page.getByRole('alert').filter({hasText:language==='fa'?'نتیجهٔ درخواست مشخص نیست':'The result is unknown'})).toBeVisible();
  await page.reload();await page.locator(`#button-language-${language}`).click();
  await page.getByRole('button',{name:language==='fa'?'بررسی نتیجه':'Check result',exact:true}).click();
  await expect(page.getByTestId(`status-undo-unresolved-${operation}`)).toBeVisible();
  await page.getByRole('button',{name:language==='fa'?'ارسال دوبارهٔ همین درخواست':'Retry same request',exact:true}).click();
  await expect.poll(()=>bodies.length).toBe(2);expect(bodies[1]).toEqual(bodies[0]);
 });
}
for(const language of ['fa','en'] as const) for(const code of [403,404,409,503,0]) test(`${language} US3 preview error ${code} is read-only and cached data never enables confirmation`,async({page})=>{
 await setup(page,language,'resume','active');let reads=0;let writes=0;
 await page.route(`**${base}/resume/`,r=>{writes++;return r.abort();});
 await page.route(`**${base}/resume-preview/`,r=>{reads++;return code===0?r.abort():r.fulfill({status:code,json:{error:{code:'unavailable',message:'Unavailable',details:{}}}});});
 await visit(page,path,language);await page.getByRole('button',{name:labels[language].resume,exact:true}).click();const dialog=page.getByRole('dialog');await expect(dialog.getByRole('button',{name:labels[language].confirm,exact:true})).toBeDisabled();
 await dialog.getByRole('button',{name:language==='fa'?'تلاش دوباره برای پیش‌نمایش':'Retry preview',exact:true}).click();await expect.poll(()=>reads).toBe(2);expect(writes).toBe(0);
 expect(await page.evaluate(()=>Object.keys(sessionStorage).filter(k=>k.startsWith('velora:status-undo-pending:')).length)).toBe(0);
});

for(const language of ['fa','en'] as const) test(`${language} US3 auth refresh preserves the entire confirmed request body`,async({page})=>{
 await setup(page,language,'resume','active');const bodies:Record<string,string>[]=[];
 await page.route('**/api/auth/token/refresh/',r=>r.fulfill({json:{access:'renewed',refresh:'navigation-test'}}));
 await page.route(`**${base}/resume/`,async r=>{bodies.push(r.request().postDataJSON());if(bodies.length===1)return r.fulfill({status:401,json:{detail:'Expired'}});return r.abort();});
 await visit(page,path,language);await page.getByRole('button',{name:labels[language].resume,exact:true}).click();await page.getByRole('dialog').getByLabel(labels[language].reason,{exact:true}).fill('Auth refresh frozen body');await page.getByRole('dialog').getByRole('button',{name:labels[language].confirm,exact:true}).click();
 await expect.poll(()=>bodies.length).toBe(2);expect(bodies[1]).toEqual(bodies[0]);
});
for(const language of ['fa','en'] as const) test(`${language} US3 sent dismissal retains pending work and signout clears private state before a late response`,async({page})=>{
 await setup(page,language,'resume','active');let deliver:(()=>Promise<void>)|undefined;
 await page.route(`**${base}/resume/`,r=>new Promise<void>(done=>{deliver=async()=>{try{await r.abort();}finally{done();}};}));
 await visit(page,path,language);await page.getByRole('button',{name:labels[language].resume,exact:true}).click();await page.getByRole('dialog').getByLabel(labels[language].reason,{exact:true}).fill('Private pending reason');await page.getByRole('dialog').getByRole('button',{name:labels[language].confirm,exact:true}).click();
 await expect.poll(()=>page.evaluate(()=>Object.keys(sessionStorage).filter(k=>k.startsWith('velora:status-undo-pending:')).length)).toBe(1);
 await page.keyboard.press('Escape');await expect(page.getByTestId('status-undo-unresolved-resume')).toBeVisible();
 await page.locator('#button-appHeaderSignOut').click();await expect(page).toHaveURL(/\/login/);
 await expect.poll(()=>page.evaluate(()=>Object.keys(sessionStorage).filter(k=>k.startsWith('velora:status-undo-')).length)).toBe(0);await deliver!();await expect(page.getByText('Private pending reason',{exact:true})).toHaveCount(0);
});
for(const language of ['fa','en'] as const) test(`${language} US3 lost authority clears the private attempt and stops retries`,async({page})=>{
 await setup(page,language,'resume','active');await page.route(`**${base}/resume/`,r=>r.abort());await page.route(`**${base}/status-undo-attempts/resume/*/`,r=>r.fulfill({status:403,json:{error:{code:'permission_denied',message:'Denied',details:{}}}}));
 await visit(page,path,language);await page.getByRole('button',{name:labels[language].resume,exact:true}).click();await page.getByRole('dialog').getByLabel(labels[language].reason,{exact:true}).fill('Authority may be revoked');await page.getByRole('dialog').getByRole('button',{name:labels[language].confirm,exact:true}).click();await page.keyboard.press('Escape');
 await page.getByRole('button',{name:language==='fa'?'بررسی نتیجه':'Check result',exact:true}).click();await expect(page.getByTestId('status-undo-unresolved-resume')).not.toBeVisible();
 expect(await page.evaluate(()=>Object.keys(sessionStorage).filter(k=>k.startsWith('velora:status-undo-pending:')).length)).toBe(0);
});

for(const language of ['fa','en'] as const) for(const code of [403,404,409,503,0]) test(`${language} US3 cached preview failure ${code} keeps confirmation disabled`,async({page})=>{
 await setup(page,language,'resume','active');await visit(page,path,language);await page.getByRole('button',{name:labels[language].resume,exact:true}).click();await expect(page.getByRole('dialog').getByLabel(labels[language].reason,{exact:true})).toBeVisible();await page.getByRole('dialog').getByRole('button',{name:labels[language].cancel,exact:true}).click();
 let reads=0;await page.route(`**${base}/resume-preview/`,r=>{reads++;return code===0?r.abort():r.fulfill({status:code,json:{error:{code:'unavailable',message:'Unavailable',details:{}}}});});
 await page.getByRole('button',{name:labels[language].resume,exact:true}).click();const dialog=page.getByRole('dialog');await expect(dialog.getByRole('button',{name:language==='fa'?'تلاش دوباره برای پیش‌نمایش':'Retry preview',exact:true})).toBeVisible();await expect(dialog.getByRole('button',{name:labels[language].confirm,exact:true})).toBeDisabled();
 await dialog.getByRole('button',{name:language==='fa'?'تلاش دوباره برای پیش‌نمایش':'Retry preview',exact:true}).click();await expect.poll(()=>reads).toBe(2);
 expect(await page.evaluate(()=>Object.keys(sessionStorage).filter(k=>k.startsWith('velora:status-undo-pending:')).length)).toBe(0);
});

for(const language of ['fa','en'] as const) test(`${language} US3 late project A response cannot change cached project B pending work`,async({page,isMobile})=>{
 await setup(page,language,'resume','active');const b='22222222-2222-4222-8222-222222222222';let deliver:(()=>Promise<void>)|undefined;let bodyA:Record<string,string>|null=null;let bodyB:Record<string,string>|null=null;
 await page.route(`**${base}/resume/`,r=>new Promise<void>(done=>{bodyA=r.request().postDataJSON();deliver=async()=>{try{await r.fulfill({json:{outcome:'applied',receipt:{id,project_id:id,project_name:'A private name',operation:'resume',source_event_id:id,request_id:bodyA!.request_id,reason:'A private reason',to_status:'active'},current_project:{status:'active'}}});}finally{done();}};}));
 await page.route('**/api/v1/projects/',r=>r.fulfill({json:{count:1,results:[{project_id:b,project_code:'B',project_name:'Project B',status:'suspended',contract_amount:null}]}}));
 await page.route(`**/api/v1/projects/${b}/`,r=>r.fulfill({json:{project_id:b,project_code:'B',project_name:'Project B',status:'suspended',can_resume_with_confirmation:true}}));
 await page.route(`**/api/v1/projects/${b}/resume-preview/`,r=>r.fulfill({json:{project_id:b,project_name:'Project B',operation:'resume',source_event_id:b,from_status:'suspended',to_status:'active',confirmation_token:'B-token',can_confirm:true,missing:[],remediation:[]}}));
 await page.route(`**/api/v1/projects/${b}/resume/`,r=>{bodyB=r.request().postDataJSON();return r.abort();});
 await visit(page,path,language);await page.getByRole('button',{name:labels[language].resume,exact:true}).click();await page.getByRole('dialog').getByLabel(labels[language].reason,{exact:true}).fill('A private reason');await page.getByRole('dialog').getByRole('button',{name:labels[language].confirm,exact:true}).click();await expect.poll(()=>Boolean(bodyA)).toBe(true);await page.keyboard.press('Escape');
 await page.locator('a[href="/projects"]').first().click();await page.getByRole(isMobile?'button':'row').filter({hasText:'Project B'}).click();await page.getByRole('button',{name:labels[language].resume,exact:true}).click();await page.getByRole('dialog').getByLabel(labels[language].reason,{exact:true}).fill('B own reason');await page.getByRole('dialog').getByRole('button',{name:labels[language].confirm,exact:true}).click();await expect.poll(()=>Boolean(bodyB)).toBe(true);
 await deliver!();await expect(page.getByRole('dialog').getByText('B own reason',{exact:true})).toBeVisible();await expect(page.getByText('A private name',{exact:true})).toHaveCount(0);
 const saved=await page.evaluate(()=>Object.keys(sessionStorage).filter(k=>k.startsWith('velora:status-undo-pending:')).map(k=>JSON.parse(sessionStorage.getItem(k)!)));
 expect(saved.find(v=>v.project_id===b)?.request_id).toBe(bodyB!.request_id);expect(saved.find(v=>v.project_id===id)?.request_id).toBe(bodyA!.request_id);
});

function historyReceipt() {return {id,project_id:id,project_name:'Name at correction',operation:'resume',source_event_id:id,request_id:id,actor:{id:'undo-actor',display_name:'Undo actor'},performed_at:'2026-10-17T08:00:00Z',reason:'Mistaken decision',from_status:'suspended',to_status:'active',source_event:{id,kind:'suspend',from_status:'active',to_status:'suspended',occurred_at:'2026-10-17T07:00:00Z',actor:{id:'original',display_name:'Original actor'},project_name:'Original project name'}};}
for(const language of ['fa','en'] as const) test(`${language} US4 history-only capability shows original and undo facts with bounded pages`,async({page})=>{
 await session(page,[],language);await page.route(`**${base}/`,r=>r.fulfill({json:{project_id:id,project_code:'UNDO',project_name:'Renamed current project',status:'active',can_view_status_undo_history:true}}));await page.route(`**${base}/members/*/permissions/`,r=>r.fulfill({status:404,json:{}}));
 await page.route(`**${base}/status-undo-history/**`,r=>{const second=new URL(r.request().url()).searchParams.get('page')==='2';return r.fulfill({json:{count:101,next:second?null:'page-two',previous:second?'page-one':null,results:[historyReceipt()]}});});
 await visit(page,path,language);const history=page.getByTestId('status-undo-history');await expect(history).toContainText('Original actor');await expect(history).toContainText('Undo actor');await expect(history).toContainText('Original project name');await expect(history).toContainText('Mistaken decision');await expect(history.locator('time[datetime]')).toHaveCount(2);
 await history.getByTestId('status-undo-history-next').click();await expect(history.getByTestId('status-undo-history-next')).toBeDisabled();await expect(history.getByTestId('status-undo-history-previous')).toBeEnabled();
});
for(const mode of ['applied','replayed','lookup','cancel','not_recorded'] as const) test(`US4 warm actual portfolio caches refresh only on evidenced ${mode}`,async({page,isMobile})=>{
 await page.clock.setFixedTime(new Date('2026-10-17T10:00:00Z'));await setup(page,'en','resume','active');let summary=0;let dashboard=0;let current='suspended';let payload:Record<string,string>|null=null;
 const row=()=>({project_id:id,project_code:'UNDO',project_name:'Status test project',status:current,contract_amount:null});
 await page.route(`**${base}/`,r=>r.fulfill({json:{...row(),can_resume_with_confirmation:current==='suspended',can_view_status_undo_history:true}}));
 await page.route('**/api/v1/projects/',r=>r.fulfill({json:{count:1,results:[row()]}}));
 await page.route('**/api/v1/portfolio/summary/',r=>{summary++;return r.fulfill({json:{totals:{project_count:1},totals_by_currency:{}}});});
 await page.route('**/api/v1/portfolio/dashboard/',r=>{dashboard++;return r.fulfill({json:{projects:[]}});});
 const result=()=>({outcome:mode==='replayed'?'replayed':'applied',receipt:{...historyReceipt(),request_id:payload?.request_id},current_project:{project_id:id,project_name:'Status test project',status:current}});
 await page.route(`**${base}/status-undo-history/**`,r=>r.fulfill({json:{count:current==='active'?1:0,next:null,previous:null,results:current==='active'?[{...historyReceipt(),reason:payload?.reason}]:[]}}));
 await page.route(`**${base}/resume/`,r=>{payload=r.request().postDataJSON();if(mode==='lookup'||mode==='not_recorded'){if(mode==='lookup')current='active';return r.abort();}current='active';return r.fulfill({json:result()});});
 await page.route(`**${base}/status-undo-attempts/resume/*/`,r=>r.fulfill({json:{...result(),outcome:mode==='lookup'?'completed':'not_recorded',receipt:mode==='lookup'?result().receipt:null}}));
 await visit(page,'/projects','en');await expect.poll(()=>summary).toBe(1);await page.getByTestId('portfolio-dashboard-link').click();await expect.poll(()=>dashboard).toBe(1);await page.locator('a[href="/projects"]').first().click();await page.getByRole(isMobile?'button':'row').filter({hasText:'Status test project'}).click();
 await page.getByRole('button',{name:'Resume',exact:true}).click();const dialog=page.getByRole('dialog');
 if(mode==='cancel')await dialog.getByRole('button',{name:'Cancel',exact:true}).click();
 else {await dialog.getByLabel('Reason',{exact:true}).fill('Explicit cache correction');await dialog.getByRole('button',{name:'Confirm status correction',exact:true}).click();if(mode==='lookup'||mode==='not_recorded'){await expect(dialog.getByRole('alert')).toContainText('The result is unknown');await page.keyboard.press('Escape');await page.getByRole('button',{name:'Check result',exact:true}).click();}else await expect(dialog).not.toBeVisible();}
 if(mode==='applied'||mode==='replayed'||mode==='lookup')await expect(page.getByTestId('status-undo-history')).toContainText('Explicit cache correction');
 await page.locator('a[href="/projects"]').first().click();const expected=mode==='cancel'||mode==='not_recorded'?1:2;await expect.poll(()=>summary).toBe(expected);await expect(page.getByRole(isMobile?'button':'row').filter({hasText:'Status test project'})).toContainText(expected===2?'Active':'Suspended');await page.getByTestId('portfolio-dashboard-link').click();await expect.poll(()=>dashboard).toBe(expected);
});

for(const language of ['fa','en'] as const) for(const late of [false,true]) {
 test(`${language} convergence account history cache is private after SPA login${late?' with late A response':''}`,async({page,isMobile})=>{
  await page.clock.setFixedTime(new Date('2026-10-17T10:00:00Z'));
  await setup(page,language,'resume','active');let accountB=false;let detailB=0;let historyB=0;
  let releaseB!:()=>void;const bResponse=new Promise<void>(resolve=>{releaseB=resolve;});
  let deliver:(()=>Promise<void>)|undefined;
  const userB={id:'account-b',full_name:'Account B',roles:[]};
  const row={project_id:id,project_name:'Status test project',project_code:'UNDO',status:'active'};
  await page.route('**/api/auth/login/',r=>{accountB=true;return r.fulfill({json:{access:'account-b-access',refresh:'account-b-refresh',user:userB}});});
  await page.route('**/api/auth/profile/',r=>r.fulfill({json:accountB?userB:{id:'navigation-user',full_name:'Navigation tester',roles:[]}}));
  await page.route('**/api/v1/projects/',r=>r.fulfill({json:{count:1,results:[row]}}));
  await page.route(`**${base}/`,async r=>{
   if(accountB){detailB++;await bResponse;return r.fulfill({status:403,json:{error:{code:'permission_denied',message:'B cannot read this project'}}});}
   return r.fulfill({json:{...row,can_view_status_undo_history:true}});
  });
  await page.route(`**${base}/members/*/permissions/`,r=>r.fulfill({json:{effective:{view_project:!accountB}}}));
  const privateReceipt={...historyReceipt(),reason:'Private history reason A',actor:{id:'actor-a',display_name:'Private historical actor A'}};
  await page.route(`**${base}/status-undo-history/**`,async r=>{
   if(accountB){historyB++;await bResponse;return r.fulfill({status:403,json:{error:{code:'permission_denied',message:'B cannot read history'}}});}
   if(late&&new URL(r.request().url()).searchParams.get('page')==='2')return new Promise<void>(done=>{
    deliver=async()=>{try{await r.fulfill({json:{count:51,next:null,previous:'page-one',results:[privateReceipt]}});}catch{/* An account change may cancel the originating fetch. */}finally{done();}};
   });
   return r.fulfill({json:{count:51,next:'page-two',previous:null,results:[privateReceipt]}});
  });
  await visit(page,path,language);await expect(page.getByTestId('status-undo-history')).toContainText(privateReceipt.reason);
  await page.evaluate(()=>{(window as unknown as {convergenceDocument:string}).convergenceDocument='same-spa-document';});
  if(late){await page.getByTestId('status-undo-history-next').click();await expect.poll(()=>Boolean(deliver)).toBe(true);}
  try {
   await page.locator('#button-appHeaderSignOut').click();await expect(page).toHaveURL(/\/login/);
   await page.getByTestId('login-phone-input').fill('+10000000002');await page.getByTestId('login-password-input').fill('mock-only-password');await page.getByTestId('login-submit-btn').click();
   await expect.poll(()=>page.evaluate(()=>JSON.parse(localStorage.getItem('auth_user')??'null')?.id)).toBe(userB.id);
   if(isMobile){await page.locator('#button-openMobileNav').click();await page.getByRole('dialog').locator('#button-sidebarNav-workspace-projects').click();}
   else await page.locator('a[href="/projects"]').first().click();
   await page.getByRole(isMobile?'button':'row').filter({hasText:row.project_name}).click();
   await expect(page).toHaveURL(new RegExp(`${id}/overview`));
   await page.evaluate(()=>new Promise<void>(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve()))));
   if(deliver){await deliver();deliver=undefined;}
   await expect(page.getByText(privateReceipt.reason,{exact:false})).toHaveCount(0);
   await expect(page.getByText(privateReceipt.actor.display_name,{exact:false})).toHaveCount(0);
   releaseB();await expect(page.getByText(privateReceipt.reason,{exact:false})).toHaveCount(0);
   await expect.poll(()=>detailB).toBeGreaterThan(0);
   expect(await page.evaluate(()=>(window as unknown as {convergenceDocument:string}).convergenceDocument)).toBe('same-spa-document');
   // A new 403 response cannot make any prior account history visible.
   expect(historyB).toBeLessThanOrEqual(1);
  } finally {releaseB();if(deliver)await deliver();}
 });
}

for(const language of ['fa','en'] as const) for(const operation of ['resume','undo_completion'] as const) for(const fault of ['rollback','another','readiness'] as const) {
 test(`${language} convergence ${operation} sent ${fault} preserves truthful recovery and warm caches`,async({page,isMobile})=>{
  await page.clock.setFixedTime(new Date('2026-10-17T10:00:00Z'));await setup(page,language,operation,'active');
  let current=operation==='resume'?'suspended':'completed';let allowFresh=false;let historyReads=0;let summaries=0;let dashboards=0;
  const bodies:Record<string,string>[]=[];
  const row=()=>({project_id:id,project_name:'Status test project',project_code:'UNDO',status:current});
  await page.route(`**${base}/`,r=>r.fulfill({json:{...row(),can_resume_with_confirmation:current==='suspended',can_undo_completion:current==='completed',can_view_status_undo_history:true}}));
  await page.route('**/api/v1/projects/',r=>r.fulfill({json:{count:1,results:[row()]}}));
  await page.route('**/api/v1/portfolio/summary/',r=>{summaries++;return r.fulfill({json:{totals:{project_count:1},totals_by_currency:{}}});});
  await page.route('**/api/v1/portfolio/dashboard/',r=>{dashboards++;return r.fulfill({json:{projects:[]}});});
  const receipt=()=>({...historyReceipt(),operation,reason:bodies.at(-1)?.reason,request_id:bodies.at(-1)?.request_id,from_status:operation==='resume'?'suspended':'completed',source_event:{...historyReceipt().source_event,kind:operation==='resume'?'suspend':'complete',to_status:operation==='resume'?'suspended':'completed'}});
  await page.route(`**${base}/status-undo-history/**`,r=>{historyReads++;return r.fulfill({json:{count:current==='active'?1:0,results:current==='active'?[receipt()]:[],next:null,previous:null}});});
  await page.route(`**${base}/${operation==='resume'?'resume-preview':'undo-completion-preview'}/`,r=>{
   const blocked=bodies.length>0&&!allowFresh&&fault!=='rollback';
   if(blocked&&fault==='another')return r.fulfill({status:409,json:{error:{code:'status_undo_context_changed',message:'Review the new occurrence'}}});
   return r.fulfill({json:{...row(),operation,source_event_id:allowFresh?'new-source':id,from_status:current,to_status:'active',confirmation_token:allowFresh?'fresh-confirmation':'original-confirmation',can_confirm:!blocked,missing:blocked?['project_manager']:[],remediation:blocked?[{field:'project_manager',action:'project_settings',can_perform:true}]:[]}});
  });
  await page.route(`**${base}/${operation==='resume'?'resume':'undo-completion'}/`,r=>{
   bodies.push(r.request().postDataJSON());
   if(bodies.length===1)return r.fulfill({status:fault==='rollback'?503:fault==='another'?409:400,json:{error:{code:fault==='rollback'?'status_undo_not_applied':fault==='another'?'status_undo_already_applied':'activation_gates_failed',message:'Rejected safely',details:{}}}});
   current='active';return r.fulfill({json:{outcome:'applied',receipt:receipt(),current_project:row()}});
  });
  await visit(page,'/projects',language);await expect.poll(()=>summaries).toBe(1);await page.getByTestId('portfolio-dashboard-link').click();await expect.poll(()=>dashboards).toBe(1);await page.locator('a[href="/projects"]').first().click();await page.getByRole(isMobile?'button':'row').filter({hasText:'Status test project'}).click();await expect.poll(()=>historyReads).toBe(1);
  await page.getByRole('button',{name:labels[language][operation],exact:true}).click();const dialog=page.getByRole('dialog');await dialog.getByLabel(labels[language].reason,{exact:true}).fill('Original rejected decision');await dialog.getByRole('button',{name:labels[language].confirm,exact:true}).click();
  const message=fault==='rollback'?(language==='fa'?'اصلاح وضعیت اعمال نشد':'The status correction was not applied'):fault==='another'?(language==='fa'?'این رخداد وضعیت قبلاً اصلاح شده':'This status event was already corrected'):(language==='fa'?'پیش از بازگردانی':'Complete all missing activation');
  await expect(dialog.getByRole('alert').filter({hasText:message})).toBeVisible();expect(bodies).toHaveLength(1);expect(summaries).toBe(1);expect(dashboards).toBe(1);expect(historyReads).toBe(1);expect(current).not.toBe('active');
  await expect(page.getByRole('alert').filter({hasText:language==='fa'?/از تعلیق به فعال بازگشت|خاتمهٔ پروژهٔ/:/resumed from suspended|Completion was undone/})).toHaveCount(0);
  const pending=()=>page.evaluate(()=>Object.keys(sessionStorage).filter(k=>k.startsWith('velora:status-undo-pending:')).map(k=>JSON.parse(sessionStorage.getItem(k)!)));
  if(fault==='rollback') {
   const saved=await pending();expect(saved).toHaveLength(1);for(const key of ['request_id','confirmation_token','reason'])expect(saved[0][key]).toBe(bodies[0][key]);
   await dialog.getByRole('button',{name:language==='fa'?'ارسال دوبارهٔ همین درخواست':'Retry same request',exact:true}).click();
  } else {
   expect(await pending()).toHaveLength(0);await expect(dialog.getByRole('button',{name:labels[language].confirm,exact:true})).toBeDisabled();
   await dialog.getByRole('button',{name:labels[language].cancel,exact:true}).click();allowFresh=true;
   await page.getByRole('button',{name:labels[language][operation],exact:true}).click();await dialog.getByLabel(labels[language].reason,{exact:true}).fill('Fresh explicitly confirmed decision');
   await expect(dialog.getByRole('button',{name:labels[language].confirm,exact:true})).toBeEnabled();expect(bodies).toHaveLength(1);
   await dialog.getByRole('button',{name:labels[language].confirm,exact:true}).click();
  }
  await expect(dialog).not.toBeVisible();expect(bodies).toHaveLength(2);
  if(fault==='rollback')expect(bodies[1]).toEqual(bodies[0]);else {expect(bodies[1].request_id).not.toBe(bodies[0].request_id);expect(bodies[1].confirmation_token).toBe('fresh-confirmation');}
  await expect.poll(()=>historyReads).toBe(2);expect(await pending()).toHaveLength(0);
  await page.locator('a[href="/projects"]').first().click();await expect.poll(()=>summaries).toBe(2);await page.getByTestId('portfolio-dashboard-link').click();await expect.poll(()=>dashboards).toBe(2);
 });
}

for(const language of ['fa','en'] as const) test(`${language} convergence late resume result keeps independent completion attempt`,async({page})=>{
 await setup(page,language,'resume','active');let current='suspended';let deliver:(()=>Promise<void>)|undefined;
 let resumeBody:Record<string,string>|null=null;let completionBody:Record<string,string>|null=null;
 await page.route(`**${base}/`,r=>r.fulfill({json:{project_id:id,project_name:'Status test project',status:current,can_resume_with_confirmation:current==='suspended',can_undo_completion:current==='completed'}}));
 await page.route(`**${base}/resume/`,r=>new Promise<void>(done=>{resumeBody=r.request().postDataJSON();current='active';deliver=async()=>{try{await r.fulfill({json:{outcome:'applied',receipt:{...historyReceipt(),request_id:resumeBody!.request_id},current_project:{project_id:id,status:'active'}}});}finally{done();}};}));
 await page.route(`**${base}/undo-completion-preview/`,r=>r.fulfill({json:{project_id:id,project_name:'Status test project',operation:'undo_completion',source_event_id:'new-completion',from_status:'completed',to_status:'active',confirmation_token:'completion-confirmation',can_confirm:true,missing:[],remediation:[]}}));
 await page.route(`**${base}/undo-completion/`,r=>{completionBody=r.request().postDataJSON();return r.abort();});
 await visit(page,path,language);await page.getByRole('button',{name:labels[language].resume,exact:true}).click();await page.getByRole('dialog').getByLabel(labels[language].reason,{exact:true}).fill('Original resume sent');await page.getByRole('dialog').getByRole('button',{name:labels[language].confirm,exact:true}).click();await expect.poll(()=>Boolean(resumeBody)).toBe(true);await page.keyboard.press('Escape');
 // A concurrent completion refreshes the real singleton cache without remounting either controller.
 current='completed';await page.evaluate(async projectId=>{const modulePath='/src/app/lib/react-query.ts';const {queryClient}=await import(modulePath);await queryClient.invalidateQueries({queryKey:['project',projectId]});},id);
 await page.getByRole('button',{name:labels[language].undo_completion,exact:true}).click();await page.getByRole('dialog').getByLabel(labels[language].reason,{exact:true}).fill('Independent completion decision');await page.getByRole('dialog').getByRole('button',{name:labels[language].confirm,exact:true}).click();await expect.poll(()=>Boolean(completionBody)).toBe(true);
 await deliver!();await expect(page.getByTestId('status-undo-unresolved-resume')).toHaveCount(0);await expect(page.getByTestId('status-undo-unresolved-undo_completion')).toBeVisible();await expect(page.getByRole('dialog').getByText('Independent completion decision',{exact:true})).toBeVisible();
 const saved=await page.evaluate(()=>Object.keys(sessionStorage).filter(k=>k.startsWith('velora:status-undo-pending:')).map(k=>JSON.parse(sessionStorage.getItem(k)!)));
 expect(saved).toHaveLength(1);expect(saved[0].operation).toBe('undo_completion');expect(saved[0].request_id).toBe(completionBody!.request_id);
});
