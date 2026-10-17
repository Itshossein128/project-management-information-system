import { expect, test } from "@playwright/test";
import { realActors,realSession,createStatusSourceProject,assertResponse,grantOrdinaryProjectAuthority,grantHistoryOnlyProjectAuthority } from "../helpers/project-status-undo";
import { visit } from "../helpers/navigation";
for(const language of ['fa','en'] as const) for(const operation of ['resume','undo_completion'] as const) {
 test(`${language} convergence real view-only member reads history without either mutation ${operation}`,async({page,request},info)=>{
  const p=await createStatusSourceProject(request,'active',false,operation);const administrator=realActors().administrator;
  const adminHeaders={Authorization:`Bearer ${administrator.access}`};
  const preview=await assertResponse(await request.get(p.base+(operation==='resume'?'resume-preview/':'undo-completion-preview/'),{headers:adminHeaders}));
  const body={request_id:crypto.randomUUID(),confirmation_token:preview.confirmation_token,reason:'Actual view-only history boundary'};
  const applied=await assertResponse(await request.post(p.base+(operation==='resume'?'resume/':'undo-completion/'),{headers:adminHeaders,data:body}));
  await assertResponse(await request.post(p.base+(operation==='resume'?'suspend/':'complete/'),{headers:adminHeaders,data:{}}));
  const viewer=await grantHistoryOnlyProjectAuthority(request,p);const headers={Authorization:`Bearer ${viewer.access}`};
  const before=await assertResponse(await request.get(p.base,{headers}));expect(before.status).toBe(operation==='resume'?'suspended':'completed');
  expect(before.can_view_status_undo_history).toBe(true);expect(before.can_resume_with_confirmation).toBe(false);expect(before.can_undo_completion).toBe(false);
  const history=await assertResponse(await request.get(p.base+'status-undo-history/',{headers}));expect(history.count).toBe(1);expect(history.results[0]).toEqual(applied.receipt);
  for(const action of ['resume','undo-completion']) {
   expect((await request.get(p.base+action+'-preview/',{headers})).status()).toBe(403);
   expect((await request.post(p.base+action+'/',{headers,data:body})).status()).toBe(403);
  }
  expect((await request.get(`${p.base}status-undo-attempts/${operation}/${body.request_id}/`,{headers})).status()).toBe(403);
  await realSession(page,viewer,language);await visit(page,`/projects/${p.id}/overview`,language);
  const visible=page.getByTestId('status-undo-history');await expect(visible).toContainText(body.reason);await expect(visible).toContainText(applied.receipt.actor.display_name);await expect(visible).toContainText(applied.receipt.source_event.actor.display_name);await expect(visible.locator('time[datetime]')).toHaveCount(2);
  await expect(page.getByRole('button',{name:language==='fa'?'ازسرگیری':'Resume',exact:true})).toHaveCount(0);
  await expect(page.getByRole('button',{name:language==='fa'?'بازگردانی خاتمه':'Undo completion',exact:true})).toHaveCount(0);
  expect(await assertResponse(await request.get(p.base,{headers}))).toEqual(before);
  expect(await assertResponse(await request.get(p.base+'status-undo-history/',{headers}))).toEqual(history);
  await page.screenshot({path:info.outputPath(`view-only-${language}-${operation}.png`),fullPage:true});
 });
}
for(const language of ['fa','en'] as const) for(const [operation,origin,target] of [['resume','active','active'],['undo_completion','active','active'],['undo_completion','suspended','suspended']] as const) {
 test(`${language} real ${operation} returns exactly ${target}`,async({page,request})=>{
  const p=await createStatusSourceProject(request,origin,false,operation);const actor=realActors().administrator;const headers={Authorization:`Bearer ${actor.access}`};
  const before=await assertResponse(await request.get(p.base,{headers}));
  await realSession(page,actor,language);await visit(page,`/projects/${p.id}/overview`,language);
  const action=operation==='resume'?(language==='fa'?'ازسرگیری':'Resume'):(language==='fa'?'بازگردانی خاتمه':'Undo completion');
  await page.getByRole('button',{name:action,exact:true}).click();const dialog=page.getByRole('dialog');
  if(operation==='resume') {
   await dialog.getByLabel(language==='fa'?'دلیل':'Reason',{exact:true}).fill('Cancel before sending');
   await dialog.getByRole('button',{name:language==='fa'?'لغو':'Cancel',exact:true}).click();await expect(dialog).not.toBeVisible();
   expect(await assertResponse(await request.get(p.base,{headers}))).toEqual(before);
   expect((await assertResponse(await request.get(p.base+'status-undo-history/',{headers}))).count).toBe(0);
   await page.getByRole('button',{name:action,exact:true}).click();
  }
  await dialog.getByLabel(language==='fa'?'دلیل':'Reason',{exact:true}).fill('Mistaken lifecycle choice real browser');
  await dialog.getByRole('button',{name:language==='fa'?'تأیید اصلاح وضعیت':'Confirm status correction',exact:true}).click();
  await expect(dialog).not.toBeVisible();
  const after=await assertResponse(await request.get(p.base,{headers}));expect(after.status).toBe(target);
  expect(after.budget_approved_at).toBe(before.budget_approved_at);expect(after.budget_approved_by).toBe(before.budget_approved_by);
  expect(operation==='resume'?after.suspension_event_id:after.completion_event_id).toBe(operation==='resume'?before.suspension_event_id:before.completion_event_id);
  if(target==='suspended') {
   await page.getByRole('button',{name:language==='fa'?'ازسرگیری':'Resume',exact:true}).click();
   await dialog.getByLabel(language==='fa'?'دلیل':'Reason',{exact:true}).fill('Separate approved resume decision');
   await dialog.getByRole('button',{name:language==='fa'?'تأیید اصلاح وضعیت':'Confirm status correction',exact:true}).click();await expect(dialog).not.toBeVisible();
   expect((await assertResponse(await request.get(p.base,{headers}))).status).toBe('active');
  }
 });
}

for(const language of ['fa','en'] as const) {
 test(`${language} real ordinary editor sees no completion correction and can resume suspended project`,async({page,request})=>{
  const completed=await createStatusSourceProject(request,'active');const suspended=await createStatusSourceProject(request,'active',false,'resume');const actors=realActors();
  await grantOrdinaryProjectAuthority(request,completed);await grantOrdinaryProjectAuthority(request,suspended);
  await realSession(page,actors.ordinary,language);await visit(page,`/projects/${completed.id}/overview`,language);
  await expect(page.getByRole('heading',{name:'Status undo browser project',exact:true}).first()).toBeVisible();
  await expect(page.getByRole('button',{name:language==='fa'?'بازگردانی خاتمه':'Undo completion',exact:true})).toHaveCount(0);
  await visit(page,`/projects/${suspended.id}/overview`,language);await page.getByRole('button',{name:language==='fa'?'ازسرگیری':'Resume',exact:true}).click();
  await page.getByRole('dialog').getByLabel(language==='fa'?'دلیل':'Reason',{exact:true}).fill('Authorized ordinary editor resume');
  await page.getByRole('dialog').getByRole('button',{name:language==='fa'?'تأیید اصلاح وضعیت':'Confirm status correction',exact:true}).click();await expect(page.getByRole('dialog')).not.toBeVisible();
  expect((await assertResponse(await request.get(suspended.base,{headers:{Authorization:`Bearer ${actors.administrator.access}`}}))).status).toBe('active');
 });
 test(`${language} US2 real approved missing-only completion repair retains reason`,async({page,request})=>{
  const p=await createStatusSourceProject(request,'active',true,'undo_completion');const actors=realActors();const actor=actors.administrator;const headers={Authorization:`Bearer ${actor.access}`};const before=await assertResponse(await request.get(p.base,{headers}));
  await realSession(page,actor,language);await visit(page,`/projects/${p.id}/overview`,language);
  await page.getByRole('button',{name:language==='fa'?'بازگردانی خاتمه':'Undo completion',exact:true}).click();
  await page.getByRole('dialog').getByLabel(language==='fa'?'دلیل':'Reason',{exact:true}).fill('Keep completion repair reason');
  await page.getByRole('dialog').locator('a[href$="#restore-manager"]').click();
  await page.getByTestId('restore-manager-search').fill('Restore creator');await page.getByTestId('restore-manager-select').selectOption(actors.creator.user.id);await page.getByTestId('restore-manager-save').click();
  await expect.poll(async()=>(await assertResponse(await request.get(p.base,{headers}))).project_manager).toBe(actors.creator.user.id);
  await page.getByTestId('cr-reason').fill('Complete missing activation information');await page.getByTestId('cr-field-amount').fill('0');await page.getByTestId('cr-field-scope').fill('Approved missing scope');await expect(page.getByTestId('cr-field-employer')).toBeHidden();
  await page.getByTestId('cr-create-btn').click();await page.getByTestId('cr-submit-btn').click();await expect(page.getByTestId('cr-item-submitted')).toBeVisible();await expect(page.getByTestId('cr-approve-btn')).toHaveCount(0);
  const rows=await assertResponse(await request.get(p.base+'change-requests/',{headers}));const cr=rows.find((r:{status:string})=>r.status==='submitted');expect(cr.restore_completion_event_id).toBe(before.completion_event_id);
  await assertResponse(await request.post(`${p.base}change-requests/${cr.id}/approve/`,{headers:{Authorization:`Bearer ${actors.creator.access}`},data:{}}));
  await visit(page,`/projects/${p.id}/overview`,language);await page.getByRole('button',{name:language==='fa'?'بازگردانی خاتمه':'Undo completion',exact:true}).click();const dialog=page.getByRole('dialog');await expect(dialog.getByLabel(language==='fa'?'دلیل':'Reason',{exact:true})).toHaveValue('Keep completion repair reason');
  expect((await assertResponse(await request.get(p.base,{headers}))).status).toBe('completed');
  await dialog.getByRole('button',{name:language==='fa'?'تأیید اصلاح وضعیت':'Confirm status correction',exact:true}).click();await expect(dialog).not.toBeVisible();
  const after=await assertResponse(await request.get(p.base,{headers}));expect(after.status).toBe('active');expect(after.budget_approved_at).toBe(before.budget_approved_at);expect(after.budget_approved_by).toBe(before.budget_approved_by);
 });
 test(`${language} US2 real editor denied completion undo and groupless admin allowed`,async({page,request})=>{
  const p=await createStatusSourceProject(request,'active');const actors=realActors();await grantOrdinaryProjectAuthority(request,p);
  const ordinary={Authorization:`Bearer ${actors.ordinary.access}`};expect((await request.get(p.base+'undo-completion-preview/',{headers:ordinary})).status()).toBe(403);
  expect((await request.post(p.base+'undo-completion/',{headers:ordinary,data:{}})).status()).toBe(403);
  await realSession(page,actors.superuser,language);await visit(page,`/projects/${p.id}/overview`,language);await page.getByRole('button',{name:language==='fa'?'بازگردانی خاتمه':'Undo completion',exact:true}).click();
  await page.getByRole('dialog').getByLabel(language==='fa'?'دلیل':'Reason',{exact:true}).fill('Groupless administrator correction');await page.getByRole('dialog').getByRole('button',{name:language==='fa'?'تأیید اصلاح وضعیت':'Confirm status correction',exact:true}).click();await expect(page.getByRole('dialog')).not.toBeVisible();
 });
}

for(const language of ['fa','en'] as const) for(const [operation,origin] of [['resume','active'],['undo_completion','active'],['undo_completion','suspended']] as const) for(const loss of ['before','after'] as const) {
 test(`${language} US3 real ${operation} ${origin} response loss ${loss} commit recovers one request`,async({page,request})=>{
  const p=await createStatusSourceProject(request,origin,false,operation);const actor=realActors().administrator;const headers={Authorization:`Bearer ${actor.access}`};let sent:Record<string,string>|null=null;let committed=false;
  const url=p.base+(operation==='resume'?'resume/':'undo-completion/');
  let acknowledgeLoss!:()=>void;const deliveryLost=new Promise<void>(resolve=>{acknowledgeLoss=resolve;});
  await page.route(url,async route=>{sent=route.request().postDataJSON();if(loss==='after'){const response=await route.fetch();expect(response.status()).toBe(200);committed=true;}await route.abort();acknowledgeLoss();});
  await realSession(page,actor,language);await visit(page,`/projects/${p.id}/overview`,language);await page.getByRole('button',{name:operation==='resume'?(language==='fa'?'ازسرگیری':'Resume'):(language==='fa'?'بازگردانی خاتمه':'Undo completion'),exact:true}).click();
  await page.getByRole('dialog').getByLabel(language==='fa'?'دلیل':'Reason',{exact:true}).fill('Original frozen lost delivery');await page.getByRole('dialog').getByRole('button',{name:language==='fa'?'تأیید اصلاح وضعیت':'Confirm status correction',exact:true}).click();
  // Start the UI assertion after the intended fault, not during the real commit.
  await deliveryLost;
  await expect(page.getByRole('alert').filter({hasText:language==='fa'?'نتیجهٔ درخواست مشخص نیست':'The result is unknown'})).toBeVisible();expect(committed).toBe(loss==='after');
  let laterSource:string|null=null;
  if(loss==='after'&&language==='en') {
   const next=operation==='resume'?'suspend':'complete';await assertResponse(await request.post(p.base+next+'/',{headers,data:{}}));
   const current=await assertResponse(await request.get(p.base,{headers}));laterSource=operation==='resume'?current.suspension_event_id:current.completion_event_id;
  }
  await page.unroute(url);await page.reload();await page.locator(`#button-language-${language}`).click();await page.getByRole('button',{name:language==='fa'?'بررسی نتیجه':'Check result',exact:true}).click();
  if(loss==='before')await page.getByRole('button',{name:language==='fa'?'ارسال دوبارهٔ همین درخواست':'Retry same request',exact:true}).click();
  await expect(page.getByTestId(`status-undo-unresolved-${operation}`)).not.toBeVisible();
  const result=await assertResponse(await request.get(`${p.base}status-undo-attempts/${operation}/${sent!.request_id}/`,{headers}));expect(result.outcome).toBe('completed');expect(result.receipt.reason).toBe('Original frozen lost delivery');
  const replay=await assertResponse(await request.post(url,{headers,data:sent}));expect(replay.outcome).toBe('replayed');expect(replay.receipt).toEqual(result.receipt);
  if(laterSource) {
   const current=await assertResponse(await request.get(p.base,{headers}));expect(operation==='resume'?current.suspension_event_id:current.completion_event_id).toBe(laterSource);
   expect((await request.post(url,{headers,data:{...sent,request_id:crypto.randomUUID()}})).status()).toBe(409);
   expect(await assertResponse(await request.get(p.base,{headers}))).toEqual(current);
  }
 });
}

for(const language of ['fa','en'] as const) for(const [operation,origin] of [['resume','active'],['undo_completion','active'],['undo_completion','suspended']] as const) {
 test(`${language} US4 real original undo history preserves populated documents and contracts ${operation} ${origin}`,async({page,request},info)=>{
  const p=await createStatusSourceProject(request,origin,false,operation);const actor=realActors().administrator;const headers={Authorization:`Bearer ${actor.access}`};
  const document=await assertResponse(await request.post(p.base+'documents/',{headers,multipart:{title:'Original approved drawing',doc_code:'D-01',status:'approved',approver:actor.user.id}}));const contract=await assertResponse(await request.post(p.base+'contracts/',{headers,data:{contract_number:'C-01',original_amount:'7654.32',status:'draft'}}));
  const docUrl=`${p.base}documents/${document.id}/`;const contractUrl=`${p.base}contracts/${contract.id}/`;const beforeDoc=await assertResponse(await request.get(docUrl,{headers}));const beforeContract=await assertResponse(await request.get(contractUrl,{headers}));
  const preview=await assertResponse(await request.get(p.base+(operation==='resume'?'resume-preview/':'undo-completion-preview/'),{headers}));const result=await assertResponse(await request.post(p.base+(operation==='resume'?'resume/':'undo-completion/'),{headers,data:{request_id:crypto.randomUUID(),confirmation_token:preview.confirmation_token,reason:'Actual preserved business records'}}));
  expect(await assertResponse(await request.get(docUrl,{headers}))).toEqual(beforeDoc);expect(await assertResponse(await request.get(contractUrl,{headers}))).toEqual(beforeContract);
  const history=await assertResponse(await request.get(p.base+'status-undo-history/',{headers}));expect(history.count).toBe(1);expect(history.results[0]).toEqual(result.receipt);
  await realSession(page,actor,language);await visit(page,`/projects/${p.id}/overview`,language);const visible=page.getByTestId('status-undo-history');await expect(visible).toContainText(result.receipt.actor.display_name);await expect(visible).toContainText(result.receipt.source_event.actor.display_name);await expect(visible).toContainText(result.receipt.reason);await expect(visible.locator('time[datetime]')).toHaveCount(2);await page.screenshot({path:info.outputPath(`history-${language}-${operation}-${origin}.png`),fullPage:true});
 });
}
