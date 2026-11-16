import { test, expect, type Browser, type Page } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
const root = path.resolve(__dirname, '../..');
const fixture = JSON.parse(fs.readFileSync(process.env.A7P6_BROWSER_FIXTURES!, 'utf8'));
const api = process.env.A7P6_API_ORIGIN ?? 'http://127.0.0.1:18000';
const web = process.env.A7P6_WEB_BASE ?? 'http://127.0.0.1:15173';
const t = JSON.parse(fs.readFileSync(path.join(root, 'apps/web/src/app/locales/en.json'), 'utf8'));
const auth = (role: string) => ({ Authorization: `Bearer ${fixture.personas[role].access}` });
async function rolePage(browser: Browser, role: string) {
  const context = await browser.newContext({ baseURL: web });
  const user = fixture.personas[role];
  await context.addCookies([{name:'auth_token',value:user.access,domain:'127.0.0.1',path:'/'}]);
  await context.addInitScript(({u}) => {
    localStorage.setItem('auth_access_token',u.access);localStorage.setItem('auth_refresh_token',u.refresh);
    localStorage.setItem('auth_user',JSON.stringify(u.user));localStorage.setItem('app-language','en');localStorage.setItem('i18nextLng','en');
  },{u:user});
  return { context, page: await context.newPage() };
}

test.describe('A7 employer delivery', () => {
  test.use({ actionTimeout: 20_000, navigationTimeout: 30_000 });
  test.skip(!fixture.personas, 'Five-persona delivery fixture required');
  for (const role of ['creator_planner','independent_approver','viewer','system_admin','org_reference_steward']) {
    test(`human login works for ${role}`, async ({page}) => {
      await page.goto('/login');
      await page.getByTestId('login-phone-input').fill(fixture.personas[role].username);
      await page.getByTestId('login-password-input').fill(fixture.personas[role].password);
      await page.getByTestId('login-submit-btn').click();
      await expect(page).not.toHaveURL(/\/login/,{timeout:30_000});
      expect(await page.evaluate(() => Boolean(localStorage.getItem('auth_access_token')))).toBe(true);
    });
  }
  test('reference project: UI creation, charter, approval, template, native MPP and lifecycle', async ({browser, request}) => {
    test.setTimeout(300_000);
    const suffix = Date.now().toString();
    const ref = async (url:string,data:unknown) => {
      const r = await request.post(`${api}/api/v1/${url}/`,{headers:auth('org_reference_steward'),data});
      expect(r.status(),url).toBe(201);return r.json();
    };
    const unit = await ref('measurement-units',{unit_name:`A7 metre ${suffix}`,unit_symbol:'m2'});
    const org = await ref('organization-units',{code:`DEL-${suffix}`,name:`Delivery unit ${suffix}`});
    const contractCode = `DEL-${suffix}`;
    await ref('contract-types',{code:contractCode,name_fa:'قرارداد آزمون تحویل',name_en:`Delivery contract ${suffix}`,is_active:true});
    const planner = await rolePage(browser,'creator_planner');
    const approver = await rolePage(browser,'independent_approver');
    const admin = await rolePage(browser,'system_admin');
    const page = planner.page;
    const post = async (url:string,data:unknown={},role='creator_planner') => {
      const r=await request.post(`${api}/api/v1/${url}`,{headers:auth(role),data});
      expect([200,201]).toContain(r.status());return r.json();
    };
    try {
      console.log('A7 JOURNEY: create project');
      await page.goto('/projects/new');
      await page.locator('#wizard-project-name').fill(`Delivery reference ${suffix}`);
      await page.locator('#wizard-project-code').fill(`DEL-${suffix}`);
      await page.locator('#wizard-employer').fill('Original delivery employer');
      await page.locator('#wizard-purpose').fill('Employer acceptance');
      await page.locator('#wizard-scope').fill('Approved construction scope');
      await page.locator('#wizard-deliverables').fill('Delivered WBS and schedule');
      await page.getByTestId('wizard-owning-unit').click();
      await page.getByRole('option',{name:`${org.code} — ${org.name}`,exact:true}).click();
      await page.getByTestId('wizard-measurement-unit').click();
      await page.getByRole('option',{name:`${unit.unit_name} (m2)`,exact:true}).click();
      await page.getByTestId('wizard-contract-type').click();
      await page.getByRole('option',{name:new RegExp(contractCode)}).click();
      await page.getByRole('button',{name:t.projectWizard.next,exact:true}).click();
      await page.locator('#input-start_date').fill('2026-01-10');
      await page.locator('#input-start_date').press('Tab');
      await page.locator('#wizard-amount').fill('50000000');
      await page.getByRole('button',{name:t.projectWizard.next,exact:true}).click();
      const created=page.waitForResponse(r => r.request().method()==='POST' && r.url().endsWith('/api/v1/projects/'));
      await page.getByRole('button',{name:t.projectWizard.createProject,exact:true}).click();
      const createResponse=await created;expect(createResponse.status()).toBe(201);
      const project=await createResponse.json();const id=project.project_id ?? project.id;
      expect(project.measurement_unit).toBe(unit.id);
      await expect(page).toHaveURL(new RegExp(`${id}/overview`));
      for (const role of ['independent_approver','system_admin']) {
        await post(`projects/${id}/members/`,{user_id:fixture.personas[role].user.id,role_ids:[fixture.role_ids.project_manager]});
      }
      await page.goto(`/projects/${id}/settings`);
      await expect(page.getByTestId('settings-measurement-unit')).toHaveValue(unit.id);
      // Clear and reselect through the actual settings form to verify null handling.
      await page.getByTestId('settings-measurement-unit').selectOption('');
      await page.getByRole('button',{name:t.projectSettings.save,exact:true}).click();
      await expect.poll(async()=> (await (await request.get(`${api}/api/v1/projects/${id}/`,{headers:auth('creator_planner')})).json()).measurement_unit).toBeNull();
      await page.getByTestId('settings-measurement-unit').selectOption(unit.id);
      await page.getByRole('button',{name:t.projectSettings.save,exact:true}).click();
      await page.goto(`/projects/${id}/overview`);
      const charter=page.getByTestId('kickoff-charter-panel');
      for (const key of ['justification','success_criteria','constraints','assumptions','key_stakeholders_summary','pm_authority']) {
        await charter.locator(`#charter-${key}`).fill(`Delivery charter ${key}`);
      }
      const charterSaved = page.waitForResponse(r => r.request().method() === 'PUT' && r.url().endsWith('/kickoff-charter/'));
      await charter.getByRole('button',{name:t.common.save,exact:true}).click();
      expect((await charterSaved).status()).toBe(200);
      await page.getByTestId('project-submit-btn').click();
      await expect(page.getByTestId('project-sod-hint')).toBeVisible();
      const self=await request.post(`${api}/api/v1/projects/${id}/approve/`,{headers:auth('creator_planner')});
      expect(self.status()).toBe(400);
      await approver.page.goto(`/projects/${id}/overview`);
      await approver.page.getByTestId('project-approve-btn').click();
      await expect(approver.page.getByTestId('project-approve-btn')).toHaveCount(0);
      await page.goto(`/projects/${id}/settings`);
      await page.getByTestId('cr-reason').fill('Approved employer correction');
      await page.getByTestId('cr-field-employer').fill('Approved delivery employer');
      await page.getByTestId('cr-create-btn').click();
      await page.getByTestId('cr-submit-btn').click();
      await approver.page.goto(`/projects/${id}/settings`);
      await approver.page.getByTestId('cr-approve-btn').click();
      await expect.poll(async()=> (await (await request.get(`${api}/api/v1/projects/${id}/`,{headers:auth('creator_planner')})).json()).employer).toBe('Approved delivery employer');
      console.log('A7 JOURNEY: build WBS');
      await page.goto(`/projects/${id}/wbs`);
      await page.locator('#input-rootWbsName').fill('Reference root');
      await page.getByRole('button',{name:t.wbs.addRoot,exact:true}).click();
      for (const [parent,name] of [['1','Reference branch'],['1.1','Reference work package']]) {
        const row=page.getByTestId(`wbs-row-${parent}`);
        await row.getByRole('button',{name:t.wbs.addChild,exact:true}).click();
        const node=page.getByTestId(`wbs-node-${parent}`);
        await node.getByPlaceholder(t.wbs.name,{exact:true}).fill(name);
        await node.getByRole('button',{name:t.wbs.save,exact:true}).click();
      }
      await expect(page.getByTestId('wbs-row-1.1.1')).toBeVisible();
      const flat = await (await request.get(`${api}/api/v1/projects/${id}/wbs/flat/`,{headers:auth('creator_planner')})).json();
      const leaf = flat.find((n:any) => n.wbs_code === '1.1.1');
      const branch = flat.find((n:any) => n.wbs_code === '1.1');
      const rootNode = flat.find((n:any) => n.wbs_code === '1');
      const meta = await request.patch(`${api}/api/v1/projects/${id}/wbs/${leaf.wbs_id}/`,{headers:auth('creator_planner'),data:{responsible:fixture.personas.creator_planner.user.id,acceptance_criteria:'Employer verifies completion'}});
      expect(meta.status()).toBe(200);
      const moved = await post(`projects/${id}/wbs/${leaf.wbs_id}/move/`,{new_parent_id:rootNode.wbs_id,position:'last-child'});
      expect(moved.wbs_code).toBe('1.2');expect(moved.depth).toBe(2);
      await post(`projects/${id}/wbs/${leaf.wbs_id}/move/`,{new_parent_id:branch.wbs_id,position:'last-child'});
      await page.reload();
      await expect(page.getByTestId('wbs-responsible-view-1.1.1')).toContainText(fixture.personas.creator_planner.user.full_name);
      await expect(page.getByTestId('wbs-acceptance-view-1.1.1')).toContainText('Employer verifies completion');

      await page.getByRole('button',{name:t.wbs.saveAsTemplate,exact:true}).click();
      const templateDialog=page.getByRole('dialog');
      await templateDialog.locator('#template-name').fill(`Delivery template ${suffix}`);
      const saved=page.waitForResponse(r=>r.request().method()==='POST' && r.url().endsWith('/save-as-template/'));
      await templateDialog.getByRole('button',{name:t.common.save,exact:true}).click();
      const template=await (await saved).json();expect(template.wbs_node_count).toBe(3);
      console.log('A7 JOURNEY: template saved');
      const target=await post('projects/',{project_code:`COPY-${suffix}`,project_name:'Independent template copy',employer:'Delivery',start_date:'2026-01-01'});
      const targetId=target.project_id??target.id;
      await post(`project-templates/${template.template_id}/apply/${targetId}/`,{},'org_reference_steward');
      const copied=await request.get(`${api}/api/v1/projects/${targetId}/wbs/`,{headers:auth('creator_planner')});expect((await copied.json()).length).toBe(1);
      console.log('A7 JOURNEY: template copied');
      const renamed = await request.patch(`${api}/api/v1/projects/${id}/wbs/${leaf.wbs_id}/`,{headers:auth('creator_planner'),data:{wbs_name:'Source changed independently'}});
      expect(renamed.status()).toBe(200);
      const independent = await (await request.get(`${api}/api/v1/projects/${targetId}/wbs/`,{headers:auth('creator_planner')})).json();
      expect(independent[0].children[0].children[0].wbs_name).toBe('Reference work package');

      // Use the native file-picker event, rather than setting the input without clicking it.
      await page.getByTestId('msp-import-btn').click();
      const importDialog=page.getByRole('dialog');
      const chooser=page.waitForEvent('filechooser');
      await importDialog.getByText(t.scheduleImport.chooseFile,{exact:true}).click();
      await (await chooser).setFiles(path.join(root,'real-data/plan.mpp'));
      console.log('A7 JOURNEY: file chosen');
      await importDialog.getByRole('button',{name:t.scheduleImport.preview,exact:true}).click();
      await importDialog.getByLabel(t.scheduleImport.replace,{exact:true}).check();
      console.log('A7 JOURNEY: MPP preview ready');
      const start=page.waitForResponse(r=>r.request().method()==='POST' && r.url().endsWith('/import/msp/'));
      await importDialog.getByRole('button',{name:t.scheduleImport.confirm,exact:true}).click();
      const started=await start;expect(started.status()).toBe(202);const taskId=(await started.json()).task_id;
      let result:any;
      await expect.poll(async()=> {
        const status=await (await request.get(`${api}/api/v1/projects/${id}/import/msp/status/${taskId}/`,{headers:auth('creator_planner')})).json();result=status.result;return status.status;
      },{timeout:90_000}).toBe('done');
      expect(result.wbs_nodes_created).toBe(6);expect(result.activities_created).toBe(72);expect(result.relations_created).toBe(72);
      await expect(importDialog.getByRole('button',{name:t.scheduleImport.chooseAnother,exact:true})).toBeVisible();
      await importDialog.getByRole('button',{name:t.scheduleImport.chooseAnother,exact:true}).click();
      const repeatChooser=page.waitForEvent('filechooser');
      await importDialog.getByText(t.scheduleImport.chooseFile,{exact:true}).click();
      await (await repeatChooser).setFiles(path.join(root,'real-data/plan.mpp'));
      await importDialog.getByRole('button',{name:t.scheduleImport.preview,exact:true}).click();
      await importDialog.getByLabel(t.scheduleImport.replace,{exact:true}).check();
      await expect(importDialog.getByRole('button',{name:t.scheduleImport.confirm,exact:true})).toBeDisabled();
      await importDialog.getByLabel(t.scheduleImport.append,{exact:true}).check();
      const repeatedStart=page.waitForResponse(r=>r.request().method()==='POST' && r.url().endsWith('/import/msp/'));
      await importDialog.getByRole('button',{name:t.scheduleImport.confirm,exact:true}).click();
      const repeatedId=(await (await repeatedStart).json()).task_id;
      let repeatedResult:any;
      await expect.poll(async()=> {
        const status=await (await request.get(`${api}/api/v1/projects/${id}/import/msp/status/${repeatedId}/`,{headers:auth('creator_planner')})).json();repeatedResult=status.result;return status.status;
      },{timeout:90_000}).toBe('done');
      expect(repeatedResult.nothing_changed).toBe(true);
      await expect(importDialog.getByRole('button',{name:t.scheduleImport.chooseAnother,exact:true})).toBeVisible();
      await page.keyboard.press('Escape');
      await page.goto(`/projects/${id}/schedule/gantt`);
      await expect(page.getByTestId('baseline-lock-panel')).toBeVisible();
      await page.goto(`/projects/${id}/schedule/status`);
      await expect(page.getByRole('heading').first()).toBeVisible();
      const counts=async()=> {
        const activities=await (await request.get(`${api}/api/v1/projects/${id}/activities/`,{headers:auth('creator_planner')})).json();
        const baselines=await (await request.get(`${api}/api/v1/projects/${id}/baselines/`,{headers:auth('creator_planner')})).json();
        return [activities.count??activities.length,baselines.length];
      };
      expect(await counts()).toEqual([72,1]);
      await admin.page.goto(`/projects/${id}/overview`);
      const bar=admin.page.getByTestId('project-lifecycle-bar');
      for (const [action,operation] of [[t.project.suspend,'resume'],[t.project.complete,'undo_completion']]) {
        await bar.getByRole('button',{name:action,exact:true}).click();
        const section=admin.page.getByTestId(`project-status-undo-${operation}`);await section.getByRole('button').click();
        const dialog=admin.page.getByRole('dialog');await dialog.locator('textarea').fill('Acceptance lifecycle verification');
        await dialog.getByRole('button',{name:t.projectStatusUndo.confirm,exact:true}).click();
        await expect(section).toHaveCount(0);
      }
      await bar.getByRole('button',{name:t.project.archive,exact:true}).click();
      await admin.page.getByTestId('project-archive-restore').getByRole('button').click();
      const restore=admin.page.getByRole('dialog');await restore.locator('textarea').fill('Acceptance archive recovery');
      await restore.getByRole('button',{name:t.projectRestore.confirm,exact:true}).click();
      await expect(admin.page.getByTestId('project-archive-restore')).toHaveCount(0);
      expect(await counts()).toEqual([72,1]);
      const retained=await (await request.get(`${api}/api/v1/projects/${id}/kickoff-charter/`,{headers:auth('creator_planner')})).json();
      expect(retained.justification).toBe('Delivery charter justification');
    } finally {await planner.context.close();await approver.context.close();await admin.context.close();}
  });
});
