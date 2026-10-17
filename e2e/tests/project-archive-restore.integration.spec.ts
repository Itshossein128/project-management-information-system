import { expect, test } from "@playwright/test";
import { realActors, realSession, createArchivedProject, assertResponse, grantOrdinaryProjectAuthority } from "../helpers/project-archive-restore";
import { visit } from "../helpers/navigation";
for (const language of ["fa","en"] as const) {
 for (const origin of ["active","suspended","completed"] as const) {
  test(`${language} real nonmember admin restores ${origin} exactly`,async({page,request})=>{
   const p=await createArchivedProject(request,origin);const actor=realActors().administrator;
   await realSession(page,actor,language);await visit(page,`/projects/${p.id}/overview`,language);
   await page.getByRole("button",{name:language==="fa"?"خروج از بایگانی":"Restore from archive",exact:true}).click();
   const dialog=page.getByRole("dialog");
   if(origin==="active") {
    await dialog.getByRole("button",{name:language==="fa"?"لغو":"Cancel",exact:true}).click();
    const unchanged=await assertResponse(await request.get(p.base,{headers:{Authorization:`Bearer ${actor.access}`}}));
    expect(unchanged.status).toBe("archived");
    await page.getByRole("button",{name:language==="fa"?"خروج از بایگانی":"Restore from archive",exact:true}).click();
   }
   await dialog.getByLabel(language==="fa"?"دلیل":"Reason",{exact:true}).fill("Mistaken archive browser proof");
   await dialog.getByRole("button",{name:language==="fa"?"تأیید بازگردانی":"Confirm restoration",exact:true}).click();
   await expect(dialog).not.toBeVisible();
   const detail=await assertResponse(await request.get(p.base,{headers:{Authorization:`Bearer ${actor.access}`}}));
   expect(detail.status).toBe(origin);
   if(origin==="active"&&language==="en") {
    const headers={Authorization:`Bearer ${actor.access}`};
    await assertResponse(await request.post(p.base+"complete/",{headers,data:{}}));
    await assertResponse(await request.post(p.base+"archive/",{headers,data:{}}));
    const again=await assertResponse(await request.get(p.base+"restore-preview/",{headers}));
    expect(again.to_status).toBe("completed");expect(again.archive_cycle_id).not.toBe(detail.archive_cycle_id);
    const restored=await assertResponse(await request.post(p.base+"restore/",{headers,data:{request_id:crypto.randomUUID(),confirmation_token:again.confirmation_token,reason:"Second known-origin archive"}}));
    expect(restored.current_project.status).toBe("completed");
   }
  });
 }
}

for(const language of ["fa","en"] as const) {
 test(`${language} real archived remediation remains approved and usable without membership`,async({page,request})=>{
  const p=await createArchivedProject(request,"active",true);const actors=realActors();const actor=actors.administrator;
  const headers={Authorization:`Bearer ${actor.access}`};
  const before=await assertResponse(await request.get(p.base,{headers}));
  await realSession(page,actor,language);await visit(page,`/projects/${p.id}/overview`,language);
  await page.getByRole("button",{name:language==="fa"?"خروج از بایگانی":"Restore from archive",exact:true}).click();
  await page.getByRole("dialog").getByLabel(language==="fa"?"دلیل":"Reason",{exact:true}).fill("Restore after approved remediation");
  await page.getByRole("link",{name:language==="fa"?"تکمیل مدیر پروژه":"Complete project manager",exact:true}).click();
  await page.getByTestId("restore-manager-search").fill("Restore creator");
  await page.getByTestId("restore-manager-select").selectOption(actors.creator.user.id);
  await page.getByTestId("restore-manager-save").click();
  await expect.poll(async()=>(await assertResponse(await request.get(p.base,{headers}))).project_manager).toBe(actors.creator.user.id);
  await page.getByTestId("cr-reason").fill("Complete missing approved information");
  await page.getByTestId("cr-field-amount").fill("1000");
  await page.getByTestId("cr-field-scope").fill("Completed approved scope");
  await page.getByTestId("cr-create-btn").click();
  await page.getByTestId("cr-submit-btn").click();
  await expect(page.getByTestId("cr-item-submitted")).toBeVisible();
  await expect(page.getByTestId("cr-approve-btn")).toHaveCount(0);
  const requests=await assertResponse(await request.get(p.base+"change-requests/",{headers}));
  const open=requests.find((r:{status:string})=>r.status==="submitted");expect(open).toBeTruthy();
  await assertResponse(await request.post(`${p.base}change-requests/${open.id}/approve/`,{headers:{Authorization:`Bearer ${actors.creator.access}`},data:{}}));
  await visit(page,`/projects/${p.id}/overview`,language);
  await page.getByRole("button",{name:language==="fa"?"خروج از بایگانی":"Restore from archive",exact:true}).click();
  const dialog=page.getByRole("dialog");await expect(dialog.getByLabel(language==="fa"?"دلیل":"Reason",{exact:true})).toHaveValue("Restore after approved remediation");
  expect((await assertResponse(await request.get(p.base,{headers}))).status).toBe("archived");
  await dialog.getByRole("button",{name:language==="fa"?"تأیید بازگردانی":"Confirm restoration",exact:true}).click();
  await expect(dialog).not.toBeVisible();
  const after=await assertResponse(await request.get(p.base,{headers}));expect(after.status).toBe("active");
  expect(after.budget_approved_at).toBe(before.budget_approved_at);expect(after.budget_approved_by).toBe(before.budget_approved_by);
 });
}

for(const language of ["fa","en"] as const) {
 test(`${language} actual committed response loss recovers the durable request after reload`,async({page,request})=>{
  const p=await createArchivedProject(request,"active");const actor=realActors().administrator;const headers={Authorization:`Bearer ${actor.access}`};
  let sent:Record<string,string>|null=null;let forwarded=false;
  await page.route(`${p.base}restore/`,async route=>{
   sent=route.request().postDataJSON();
   const response=await route.fetch();expect(response.status()).toBe(200);forwarded=true;
   await route.abort(); // Only response delivery is lost; the real transaction already committed.
  });
  await realSession(page,actor,language);await visit(page,`/projects/${p.id}/overview`,language);
  await page.getByRole("button",{name:language==="fa"?"خروج از بایگانی":"Restore from archive",exact:true}).click();
  await page.getByRole("dialog").getByLabel(language==="fa"?"دلیل":"Reason",{exact:true}).fill("Committed response lost once");
  await page.getByRole("dialog").getByRole("button",{name:language==="fa"?"تأیید بازگردانی":"Confirm restoration",exact:true}).click();
  await expect.poll(()=>forwarded).toBe(true);
  await expect(page.getByRole("alert").filter({hasText:language==="fa"?"نتیجهٔ درخواست مشخص نیست":"The result is unknown"})).toBeVisible();
  await page.reload();await page.locator(`#button-language-${language}`).click();await page.getByRole("button",{name:language==="fa"?"بررسی نتیجه":"Check result",exact:true}).click();
  await expect(page.getByTestId("restore-unresolved")).not.toBeVisible();
  const result=await assertResponse(await request.get(`${p.base}restore-attempts/${sent!.request_id}/`,{headers}));
  expect(result.outcome).toBe("completed");expect(result.receipt.reason).toBe("Committed response lost once");
  const replay=await assertResponse(await request.post(p.base+"restore/",{headers,data:sent}));
  expect(replay.outcome).toBe("replayed");expect(replay.receipt).toEqual(result.receipt);
  await assertResponse(await request.post(p.base+"complete/",{headers,data:{}}));
  await assertResponse(await request.post(p.base+"archive/",{headers,data:{}}));
  const current=await assertResponse(await request.get(p.base,{headers}));
  const historical=await assertResponse(await request.post(p.base+"restore/",{headers,data:sent}));
  expect(historical.outcome).toBe("replayed");expect(historical.receipt).toEqual(result.receipt);
  expect(historical.current_project.status).toBe("archived");expect(historical.current_project.archive_cycle_id).toBe(current.archive_cycle_id);
  const obsolete=await request.post(p.base+"restore/",{headers,data:{...sent,request_id:crypto.randomUUID()}});
  expect(obsolete.status()).toBe(409);expect((await obsolete.json()).error.code).toBe("archive_already_restored");
  expect(await assertResponse(await request.get(p.base,{headers}))).toEqual(current);
  expect((await assertResponse(await request.get(p.base+"restore-history/",{headers}))).count).toBe(1);
 });
}

for(const language of ["fa","en"] as const) {
 test(`${language} before-commit delivery failure safely retries exactly the same request`,async({page,request})=>{
  const p=await createArchivedProject(request,"completed");const actor=realActors().administrator;const headers={Authorization:`Bearer ${actor.access}`};
  const bodies:Record<string,string>[]=[];
  await page.route(`${p.base}restore/`,async route=>{
   bodies.push(route.request().postDataJSON());
   if(bodies.length===1)await route.abort();else await route.continue();
  });
  await realSession(page,actor,language);await visit(page,`/projects/${p.id}/overview`,language);
  await page.getByRole("button",{name:language==="fa"?"خروج از بایگانی":"Restore from archive",exact:true}).click();
  await page.getByRole("dialog").getByLabel(language==="fa"?"دلیل":"Reason",{exact:true}).fill("Retry without changing identity");
  await page.getByRole("dialog").getByRole("button",{name:language==="fa"?"تأیید بازگردانی":"Confirm restoration",exact:true}).click();
  await expect(page.getByRole("alert").filter({hasText:language==="fa"?"نتیجهٔ درخواست مشخص نیست":"The result is unknown"})).toBeVisible();
  expect((await assertResponse(await request.get(`${p.base}restore-attempts/${bodies[0].request_id}/`,{headers}))).outcome).toBe("not_recorded");
  await page.getByRole("dialog").getByRole("button",{name:language==="fa"?"تلاش مجدد همین درخواست":"Retry same request",exact:true}).click();
  await expect(page.getByRole("dialog")).not.toBeVisible();expect(bodies).toHaveLength(2);expect(bodies[1]).toEqual(bodies[0]);
  expect((await assertResponse(await request.get(p.base,{headers}))).status).toBe("completed");
 });
}

for(const language of ["fa","en"] as const) {
 for(const origin of ["active","suspended","completed"] as const) {
  test(`${language} real visible history and populated document/contract preservation ${origin}`,async({page,request},testInfo)=>{
   const p=await createArchivedProject(request,origin);const actor=realActors().administrator;const headers={Authorization:`Bearer ${actor.access}`};
   const document=await assertResponse(await request.post(p.base+"documents/",{headers,multipart:{title:"Original approved drawing",doc_code:"D-01",status:"approved",approver:actor.user.id}}));
   const contract=await assertResponse(await request.post(p.base+"contracts/",{headers,data:{contract_number:"C-01",original_amount:"7654.32",status:"draft"}}));
   const docUrl=`${p.base}documents/${document.id}/`;const contractUrl=`${p.base}contracts/${contract.id}/`;
   const beforeDoc=await assertResponse(await request.get(docUrl,{headers}));const beforeContract=await assertResponse(await request.get(contractUrl,{headers}));
   const preview=await assertResponse(await request.get(p.base+"restore-preview/",{headers}));
   const result=await assertResponse(await request.post(p.base+"restore/",{headers,data:{request_id:crypto.randomUUID(),confirmation_token:preview.confirmation_token,reason:"Preserve original business data"}}));
   expect(await assertResponse(await request.get(docUrl,{headers}))).toEqual(beforeDoc);
   expect(await assertResponse(await request.get(contractUrl,{headers}))).toEqual(beforeContract);
   const history=await assertResponse(await request.get(p.base+"restore-history/",{headers}));expect(history.count).toBe(1);expect(history.results[0]).toEqual(result.receipt);
   await realSession(page,actor,language);await visit(page,`/projects/${p.id}/overview`,language);
   const visible=page.getByTestId("restore-history");await expect(visible).toContainText(result.receipt.actor.display_name);await expect(visible).toContainText(result.receipt.reason);
   await expect(visible.locator("time")).toHaveAttribute("datetime",result.receipt.restored_at);
   await page.screenshot({path:testInfo.outputPath(`real-history-${language}-${origin}.png`),fullPage:true});
  });
 }
}

test("bounded uncontended preview restore and history latency sample",async({request},testInfo)=>{
 test.setTimeout(120_000); // Six full fixture workflows are outside the timed API operations.
 const actor=realActors().administrator;const headers={Authorization:`Bearer ${actor.access}`};
 const times:{preview:number[];restore:number[];history:number[]}={preview:[],restore:[],history:[]};
 for(const origin of ["active","suspended","completed","active","suspended","completed"]) {
  const p=await createArchivedProject(request,origin);
  let start=performance.now();const preview=await assertResponse(await request.get(p.base+"restore-preview/",{headers}));times.preview.push(performance.now()-start);
  start=performance.now();await assertResponse(await request.post(p.base+"restore/",{headers,data:{request_id:crypto.randomUUID(),confirmation_token:preview.confirmation_token,reason:"Bounded timing sample"}}));times.restore.push(performance.now()-start);
  start=performance.now();const history=await assertResponse(await request.get(p.base+"restore-history/?page_size=100",{headers}));times.history.push(performance.now()-start);
  expect(history.count).toBe(1);expect(history.results).toHaveLength(1);expect(history.next).toBeNull();
 }
 const p95=(values:number[])=>[...values].sort((a,b)=>a-b)[Math.ceil(values.length*0.95)-1];
 const metrics={samples:6,unit:"ms",previewP95:p95(times.preview),restoreP95:p95(times.restore),historyP95:p95(times.history),times};
 await testInfo.attach("latency-sample.json",{body:JSON.stringify(metrics,null,2),contentType:"application/json"});
 console.log("RESTORE_LATENCY",JSON.stringify(metrics));
});

for(const language of ["fa","en"] as const) {
 for(const kind of ["superuser","ordinary"] as const) {
  test(`${language} real ${kind} authority is independent from project management`,async({page,request})=>{
   const p=await createArchivedProject(request,"completed");const actors=realActors();const actor=actors[kind];
   expect(actor.user.roles).not.toContain("admin");
   if(kind==="ordinary")await grantOrdinaryProjectAuthority(request,p);
   const headers={Authorization:`Bearer ${actor.access}`};
   const before=await assertResponse(await request.get(p.base,{headers}));
   expect(before.can_restore_from_archive).toBe(kind==="superuser");
   await realSession(page,actor,language);await visit(page,`/projects/${p.id}/overview`,language);
   const action=page.getByRole("button",{name:language==="fa"?"خروج از بایگانی":"Restore from archive",exact:true});
   if(kind==="ordinary") {
    await expect(page.getByRole("heading",{name:before.project_name,exact:true})).toBeVisible();
    await expect(action).toHaveCount(0);
    for(const endpoint of ["restore-preview/","restore/","restore-attempts/"+crypto.randomUUID()+"/"]) {
     const result=endpoint==="restore/"?await request.post(p.base+endpoint,{headers,data:{reason:"Membership is not system authority"}}):await request.get(p.base+endpoint,{headers});
     expect(result.status()).toBe(403);
    }
    expect(await assertResponse(await request.get(p.base,{headers}))).toEqual(before);
    const history=await assertResponse(await request.get(p.base+"restore-history/",{headers}));expect(history.count).toBe(0);
   } else {
    await action.click();const dialog=page.getByRole("dialog");
    await dialog.getByLabel(language==="fa"?"دلیل":"Reason",{exact:true}).fill("Groupless superuser restore proof");
    await dialog.getByRole("button",{name:language==="fa"?"تأیید بازگردانی":"Confirm restoration",exact:true}).click();
    await expect(dialog).not.toBeVisible();
    expect((await assertResponse(await request.get(p.base,{headers}))).status).toBe("completed");
    expect((await assertResponse(await request.get(p.base+"restore-history/",{headers}))).count).toBe(1);
   }
  });
 }
}
