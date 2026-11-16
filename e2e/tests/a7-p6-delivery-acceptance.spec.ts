import { execFileSync } from 'node:child_process';
import { expect, test } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

interface AuthFixture {
  access: string;
  refresh: string;
  user: {
    id: string;
    phone_number: string;
    full_name: string;
  };
}

interface CaseFixture {
  width: number;
  lang: 'fa' | 'en';
  project: string;
}

interface P6BrowserFixtures {
  admin_auth: AuthFixture;
  viewer_auth: AuthFixture;
  project_main: string;
  project_b: string;
  cases: CaseFixture[];
  viewer_wbs?: string;
  viewer_baseline_name?: string;
  private_job?: string;
  private_activity?: string;
  private_baseline?: string;
  private_baseline_activity?: string;
  private_markers?: string[];
}

const apiOrigin = process.env.A7P6_API_ORIGIN ?? 'http://127.0.0.1:18000';
const fixture: P6BrowserFixtures = JSON.parse(
  fs.readFileSync(process.env.A7P6_BROWSER_FIXTURES!, 'utf8'),
);
const root = path.resolve(__dirname, '../..');
const screenshotsDir = path.join(
  root,
  'specs/056-a7-p6-delivery-acceptance/evidence/screenshots',
);
fs.mkdirSync(screenshotsDir, { recursive: true });

const validXmlBuffer = fs.readFileSync(
  path.join(root, 'specs/051-a7-p1-project-reference/evidence/fixtures/branch.xml'),
);
const invalidXmlBuffer = fs.readFileSync(
  path.join(root, 'specs/051-a7-p1-project-reference/evidence/fixtures/not-a-project.xml'),
);

test('lifecycle suspend, resume, complete, undo, archive and restore in browser (POS-10)', async ({
  page,
  context,
}) => {
  const tFa = JSON.parse(
    fs.readFileSync(path.join(root, 'apps/web/src/app/locales/fa.json'), 'utf8'),
  );
  await page.setViewportSize({ width: 1280, height: 800 });
  await context.addCookies([
    {
      name: 'auth_token',
      value: fixture.admin_auth.access,
      domain: '127.0.0.1',
      path: '/',
    },
  ]);
  await page.addInitScript(
    ({ auth }) => {
      localStorage.setItem('auth_access_token', auth.access);
      localStorage.setItem('auth_refresh_token', auth.refresh);
      localStorage.setItem('auth_user', JSON.stringify(auth.user));
      localStorage.setItem('app-language', 'fa');
      localStorage.setItem('i18nextLng', 'fa');
    },
    { auth: fixture.admin_auth },
  );

  await page.goto(`/projects/${fixture.project_main}/overview`);
  const lifecycleBar = page.getByTestId('project-lifecycle-bar');
  await expect(lifecycleBar).toBeVisible({ timeout: 30_000 });
  const readCharter = async () => {
    const response = await context.request.get(`${apiOrigin}/api/v1/projects/${fixture.project_main}/kickoff-charter/`, {
      headers: { Authorization: `Bearer ${fixture.admin_auth.access}` },
    });
    expect(response.ok()).toBeTruthy();
    return response.json();
  };
  const charterBefore = await readCharter();
  expect(charterBefore.justification).toBeTruthy();

  // Suspend and resume through the same confirmation flow used by a real user.
  await lifecycleBar.getByRole('button', { name: tFa.project.suspend, exact: true }).click();
  const resumeSection = page.getByTestId('project-status-undo-resume');
  await expect(resumeSection).toBeVisible({ timeout: 20_000 });
  await resumeSection.getByRole('button').first().click();
  const resumeDialog = page.getByRole('dialog');
  const resumeTextarea = resumeDialog.locator(`#status-undo-reason-resume-${fixture.project_main}`);
  await expect(resumeTextarea).toBeVisible({ timeout: 15_000 });
  await expect(resumeDialog.getByRole('button', { name: tFa.projectStatusUndo.confirm, exact: true })).toBeDisabled();
  await resumeTextarea.fill('رفع موانع و ازسرگیری پروژه در آزمون پذیرش');
  await resumeDialog.getByRole('button', { name: tFa.projectStatusUndo.confirm, exact: true }).click();
  await expect(resumeSection).toHaveCount(0, { timeout: 20_000 });

  // Complete -> Undo completion
  const completeBtn = lifecycleBar.getByRole('button', {
    name: tFa.project?.complete ?? 'خاتمه',
    exact: true,
  });
  await expect(completeBtn).toBeVisible();
  await completeBtn.focus();
  await page.keyboard.press('Shift+Tab');
  await page.keyboard.press('Tab');
  await completeBtn.click();

  const undoSection = page.getByTestId('project-status-undo-undo_completion');
  await expect(undoSection).toBeVisible({ timeout: 20_000 });

  await undoSection.getByRole('button').first().click();
  const undoDialog = page.getByRole('dialog');
  await expect(undoDialog).toBeVisible();
  const undoTextarea = undoDialog.locator(
    `#status-undo-reason-undo_completion-${fixture.project_main}`,
  );
  await expect(undoTextarea).toBeVisible({ timeout: 15_000 });
  await undoTextarea.focus();
  await page.keyboard.press('Shift+Tab');
  await page.keyboard.press('Tab');
  await expect(undoTextarea).toBeFocused();
  await undoTextarea.fill('تصحیح وضعیت خاتمه در آزمون پذیرش مرورگر فاز ۶');
  await undoDialog
    .getByRole('button', { name: tFa.projectStatusUndo.confirm, exact: true })
    .click();

  await expect(undoSection).toHaveCount(0, { timeout: 20_000 });
  await expect(completeBtn).toBeVisible({ timeout: 20_000 });

  // 2. Archive -> Restore from archive
  const archiveBtn = lifecycleBar.getByRole('button', {
    name: tFa.project?.archive ?? 'بایگانی',
    exact: true,
  });
  await expect(archiveBtn).toBeVisible();
  await archiveBtn.click();

  const restoreSection = page.getByTestId('project-archive-restore');
  await expect(restoreSection).toBeVisible({ timeout: 20_000 });

  await restoreSection.getByRole('button').first().click();
  const restoreDialog = page.getByRole('dialog');
  await expect(restoreDialog).toBeVisible();
  const restoreTextarea = restoreDialog.locator(
    `#restore-reason-${fixture.project_main}`,
  );
  await expect(restoreTextarea).toBeVisible({ timeout: 15_000 });
  await restoreTextarea.fill('بازگردانی پروژه از بایگانی در آزمون پذیرش مرورگر فاز ۶');
  await restoreDialog
    .getByRole('button', { name: tFa.projectRestore.confirm, exact: true })
    .click();

  await expect(restoreSection).toHaveCount(0, { timeout: 20_000 });
  await expect(completeBtn).toBeVisible({ timeout: 20_000 });
  expect(await readCharter()).toEqual(charterBefore);
});

for (const item of [
  { lang: 'fa' as const, width: 1280 },
  { lang: 'fa' as const, width: 390 },
  { lang: 'en' as const, width: 1280 },
  { lang: 'en' as const, width: 390 },
]) {
  test(`lifecycle and WBS screens (${item.lang} ${item.width}px)`, async ({ page, context }) => {
    const localeData = JSON.parse(
      fs.readFileSync(path.join(root, `apps/web/src/app/locales/${item.lang}.json`), 'utf8'),
    );
    await page.setViewportSize({ width: item.width, height: item.width === 390 ? 844 : 800 });
    await context.addCookies([
      { name: 'auth_token', value: fixture.admin_auth.access, domain: '127.0.0.1', path: '/' },
    ]);
    await page.addInitScript(
      ({ auth, lang }) => {
        localStorage.setItem('auth_access_token', auth.access);
        localStorage.setItem('auth_refresh_token', auth.refresh);
        localStorage.setItem('auth_user', JSON.stringify(auth.user));
        localStorage.setItem('app-language', lang);
        localStorage.setItem('i18nextLng', lang);
      },
      { auth: fixture.admin_auth, lang: item.lang },
    );
    await page.goto(`/projects/${fixture.project_main}/overview`);
    await page.locator(`#button-language-${item.lang}`).click();
    await expect.poll(async () => page.evaluate(() => document.documentElement.dir)).toBe(item.lang === 'fa' ? 'rtl' : 'ltr');
    const lifecycleBar = page.getByTestId('project-lifecycle-bar');
    await expect(lifecycleBar).toBeVisible({ timeout: 30_000 });
    const firstButton = lifecycleBar.getByRole('button').first();
    await firstButton.focus();
    await page.keyboard.press('Shift+Tab');
    await page.keyboard.press('Tab');
    await expect(firstButton).toBeFocused();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow).toBeLessThanOrEqual(2);
    await page.goto(`/projects/${fixture.project_main}/wbs`);
    await expect(page.getByRole('heading', { name: localeData.pages.wbs.title })).toBeVisible({ timeout: 30_000 });
    await page.screenshot({
      path: path.join(screenshotsDir, `lifecycle-wbs-${item.lang}-${item.width}.png`),
      fullPage: true,
    });
  });
}

for (const item of fixture.cases) {
  test(`schedule import wizard, invalid upload recovery, and responsive layout (${item.lang} ${item.width}px) (POS-05, POS-06, NEG-06, NEG-07, OPS-01..03)`, async ({
    page,
    context,
  }) => {
    const localeData = JSON.parse(
      fs.readFileSync(
        path.join(root, `apps/web/src/app/locales/${item.lang}.json`),
        'utf8',
      ),
    );
    const t = localeData.scheduleImport;
    const height = item.width === 390 ? 844 : 800;
    await page.setViewportSize({ width: item.width, height });
    await context.addCookies([
      {
        name: 'auth_token',
        value: fixture.admin_auth.access,
        domain: '127.0.0.1',
        path: '/',
      },
    ]);
    await page.addInitScript(
      ({ auth, lang }) => {
        localStorage.setItem('auth_access_token', auth.access);
        localStorage.setItem('auth_refresh_token', auth.refresh);
        localStorage.setItem('auth_user', JSON.stringify(auth.user));
        localStorage.setItem('app-language', lang);
        localStorage.setItem('i18nextLng', lang);
      },
      { auth: fixture.admin_auth, lang: item.lang },
    );

    await page.goto(`/projects/${item.project}/wbs`);
    await page.locator(`#button-language-${item.lang}`).click();

    await expect
      .poll(async () => page.evaluate(() => document.documentElement.dir))
      .toBe(item.lang === 'fa' ? 'rtl' : 'ltr');

    // Keyboard activation + Escape dismissal + reopen (OPS-03)
    const importBtn = page.getByTestId('msp-import-btn');
    await expect(importBtn).toBeVisible({ timeout: 30_000 });
    await importBtn.focus();
    await page.keyboard.press('Enter');

    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(dialog).toHaveCount(0);

    await importBtn.focus();
    await page.keyboard.press('Enter');
    await expect(dialog).toBeVisible();

    // Check no horizontal viewport overflow at current viewport width (OPS-01 / OPS-02)
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - window.innerWidth,
    );
    expect(overflow).toBeLessThanOrEqual(2);

    // 1. Reject unsupported extension client-side (NEG-06)
    await dialog.getByTestId('msp-import-file').setInputFiles({
      name: 'notes.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from('not a schedule file'),
    });
    await expect(dialog.getByTestId('msp-import-filename')).toHaveCount(0);

    // 2. Reject invalid XML payload on preview and recover cleanly (NEG-06, NEG-07)
    await dialog.getByTestId('msp-import-file').setInputFiles({
      name: 'not-a-project.xml',
      mimeType: 'application/xml',
      buffer: invalidXmlBuffer,
    });
    await expect(dialog.getByTestId('msp-import-filename')).toBeVisible();
    const failedPreview = page.waitForResponse(
      (r) =>
        r.request().method() === 'POST' && /\/import\/msp\/preview\/$/.test(r.url()),
    );
    await dialog.getByRole('button', { name: t.preview, exact: true }).click();
    expect((await failedPreview).status()).toBe(400);

    // 3. Recover in same session by selecting valid-msp.xml, previewing, and importing (POS-05, POS-06, NEG-07)
    await dialog.getByTestId('msp-import-file').setInputFiles({
      name: 'valid-msp.xml',
      mimeType: 'application/xml',
      buffer: validXmlBuffer,
    });
    const okPreview = page.waitForResponse(
      (r) =>
        r.request().method() === 'POST' && /\/import\/msp\/preview\/$/.test(r.url()),
    );
    await dialog.getByRole('button', { name: t.preview, exact: true }).focus();
    await page.keyboard.press('Enter');
    expect((await okPreview).status()).toBe(200);

    await dialog.getByLabel(t.append, { exact: true }).check();
    const accepted = page.waitForResponse(
      (r) => r.request().method() === 'POST' && /\/import\/msp\/$/.test(r.url()),
    );
    await dialog.getByRole('button', { name: t.confirm, exact: true }).focus();
    await page.keyboard.press('Enter');

    const importResp = await accepted;
    expect(importResp.status()).toBe(202);
    const { task_id: taskId } = (await importResp.json()) as { task_id: string };

    await expect
      .poll(
        async () => {
          const polled = await context.request.get(
            `${apiOrigin}/api/v1/projects/${item.project}/import/msp/status/${taskId}/`,
            {
              headers: { Authorization: `Bearer ${fixture.admin_auth.access}` },
            },
          );
          return (await polled.json()).status;
        },
        { timeout: 60_000 },
      )
      .toBe('done');

    await expect(
      dialog.getByRole('button', { name: t.chooseAnother, exact: true }),
    ).toBeVisible({ timeout: 30_000 });

    await page.screenshot({
      path: path.join(screenshotsDir, `import-${item.lang}-${item.width}.png`),
      fullPage: true,
    });
  });
}

async function authHeaders(access: string) {
  return { Authorization: `Bearer ${access}` };
}

for (const family of ['msp', 'p6'] as const) {
for (const dismiss of ['escape', 'cancel'] as const) {
test(`cancel after preview creates no import job (${family}, ${dismiss}) (NEG-07)`, async ({ page, context }) => {
  const localeData = JSON.parse(
    fs.readFileSync(path.join(root, 'apps/web/src/app/locales/fa.json'), 'utf8'),
  );
  const t = localeData.scheduleImport as { preview: string; cancel: string; confirm: string; back: string };
  await page.setViewportSize({ width: 1280, height: 800 });
  await context.addCookies([
    { name: 'auth_token', value: fixture.admin_auth.access, domain: '127.0.0.1', path: '/' },
  ]);
  await page.addInitScript(
    ({ auth }) => {
      localStorage.setItem('auth_access_token', auth.access);
      localStorage.setItem('auth_refresh_token', auth.refresh);
      localStorage.setItem('auth_user', JSON.stringify(auth.user));
      localStorage.setItem('app-language', 'fa');
      localStorage.setItem('i18nextLng', 'fa');
    },
    { auth: fixture.admin_auth },
  );

  const snapshotProject = () => JSON.parse(execFileSync('python3', [
    path.join(root, 'ops/a7-p5/snapshot-project.py'), fixture.project_main,
  ], { encoding: 'utf8' }));
  const before = snapshotProject();
  const importStarts: string[] = [];
  page.on('request', request => {
    if (request.method() === 'POST' && /\/import\/(msp|p6)\/$/.test(request.url())) importStarts.push(request.url());
  });
  const extension = family === 'msp' ? 'xml' : 'xer';
  const marker = `neg07-cancel-${Date.now()}.${extension}`;
  await page.goto(`/projects/${fixture.project_main}/wbs`);
  const importBtn = page.getByTestId('msp-import-btn');
  await expect(importBtn).toBeVisible({ timeout: 30_000 });
  await importBtn.click();
  const dialog = page.getByRole('dialog');
  await expect(dialog).toBeVisible();
  await dialog.getByTestId('msp-import-file').setInputFiles({
    name: marker,
    mimeType: family === 'msp' ? 'application/xml' : 'application/octet-stream',
    buffer: family === 'msp' ? validXmlBuffer : fs.readFileSync(path.join(root, 'specs/051-a7-p1-project-reference/evidence/fixtures/branch.xer')),
  });
  const previewResp = page.waitForResponse(
    (r) => r.request().method() === 'POST' && r.url().endsWith(`/import/${family}/preview/`),
  );
  await dialog.getByRole('button', { name: t.preview, exact: true }).click();
  expect((await previewResp).status()).toBe(200);

  // Both supported dismissal paths must leave the database untouched.
  if (dismiss === 'escape') {
    await page.keyboard.press('Escape');
  } else {
    await dialog.getByRole('button', { name: t.back, exact: true }).click();
    await dialog.getByRole('button', { name: t.cancel, exact: true }).click();
  }
  await expect(dialog).toHaveCount(0);

  // Re-open wizard: no in-flight attempt should have been saved from preview alone.
  await importBtn.click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(page.getByTestId('msp-import-file')).toBeAttached();
  await expect(page.getByTestId('msp-import-filename')).toHaveCount(0);
  await expect(page.getByTestId('msp-import-processing')).toHaveCount(0);

  // Read the database directly: a fresh start would miss a completed stray job.
  const after = snapshotProject();
  expect(after).toEqual(before);
  expect(importStarts).toEqual([]);
  await page.keyboard.press('Escape');

});

}
}

const recoveryControl = (action: string) => JSON.parse(execFileSync('python3', [
  path.join(root, 'ops/a7-p5/browser-recovery-fixture.py'), action, fixture.project_main,
], { encoding: 'utf8' }).trim().replace(/^(armed|released)$/, 'null'));

async function loginPlanner(page: import('@playwright/test').Page, context: import('@playwright/test').BrowserContext) {
  await context.addCookies([{ name: 'auth_token', value: fixture.admin_auth.access, domain: '127.0.0.1', path: '/' }]);
  await page.addInitScript(({ auth }) => {
    localStorage.setItem('auth_access_token', auth.access);
    localStorage.setItem('auth_refresh_token', auth.refresh);
    localStorage.setItem('auth_user', JSON.stringify(auth.user));
    localStorage.setItem('app-language', 'fa');
    localStorage.setItem('i18nextLng', 'fa');
  }, { auth: fixture.admin_auth });
}

for (const family of ['msp', 'p6'] as const) {
  test(`real worker import recovers same attempt after offline and reload (${family}) (NEG-08)`, async ({ page, context }) => {
    const locale = JSON.parse(fs.readFileSync(path.join(root, 'apps/web/src/app/locales/fa.json'), 'utf8')).scheduleImport;
    await loginPlanner(page, context);
    const before = recoveryControl('jobs');
    await page.goto(`/projects/${fixture.project_main}/wbs`);
    await page.getByTestId('msp-import-btn').click();
    const dialog = page.getByRole('dialog');
    const extension = family === 'msp' ? 'xml' : 'xer';
    const name = `neg08-real-${Date.now()}.${extension}`;
    await dialog.getByTestId('msp-import-file').setInputFiles({ name, mimeType: family === 'msp' ? 'application/xml' : 'application/octet-stream', buffer: fs.readFileSync(path.join(root, `specs/051-a7-p1-project-reference/evidence/fixtures/branch.${extension}`)) });
    await dialog.getByRole('button', { name: locale.preview, exact: true }).click();
    await expect(dialog.getByRole('button', { name: locale.confirm, exact: true })).toBeVisible();
    let starts = 0;
    page.on('request', r => { if (r.method() === 'POST' && r.url().endsWith(`/import/${family}/`)) starts++; });
    recoveryControl('hold');
    try {
      const started = page.waitForResponse(r => r.request().method() === 'POST' && r.url().endsWith(`/import/${family}/`));
      await dialog.getByRole('button', { name: locale.confirm, exact: true }).click();
      const response = await started;
      expect(response.status()).toBe(202);
      const taskId = (await response.json()).task_id;
      await expect.poll(() => recoveryControl('jobs').held).toBe(true);
      const jobs = recoveryControl('jobs');
      expect(jobs[family].length).toBe(before[family].length + 1);
      expect(jobs[family].find((j: {id: string}) => j.id === taskId).status).toBe('running');
      const storageKey = `schedule-import-attempt:${fixture.admin_auth.user.id}:${fixture.project_main}`;
      expect(JSON.parse((await page.evaluate(key => sessionStorage.getItem(key), storageKey))! ).task_id).toBe(taskId);
      await context.setOffline(true);
      await expect(dialog.getByTestId('msp-import-interrupted')).toBeVisible({ timeout: 15_000 });
      await context.setOffline(false);
      const resumed = page.waitForResponse(r => r.url().endsWith(`/import/${family}/status/${taskId}/`) && r.status() === 200);
      await dialog.getByTestId('msp-import-interrupted').getByRole('button').click();
      expect((await (await resumed).json()).status).toBe('running');
      await page.reload();
      const recoveredPoll = page.waitForResponse(r => r.url().endsWith(`/import/${family}/status/${taskId}/`) && r.status() === 200);
      await page.getByTestId('msp-import-btn').click();
      await expect(page.getByTestId('msp-import-filename')).toContainText(name);
      expect((await (await recoveredPoll).json()).status).toBe('running');
      const sameStatus = await context.request.get(`${apiOrigin}/api/v1/projects/${fixture.project_main}/import/${family}/status/${taskId}/`, { headers: await authHeaders(fixture.admin_auth.access) });
      expect((await sameStatus.json()).status).toBe('running');
      expect(recoveryControl('jobs')[family].map((j: {id: string}) => j.id).sort()).toEqual(jobs[family].map((j: {id: string}) => j.id).sort());
      expect(starts).toBe(1);
      recoveryControl('release');
      await expect.poll(async () => {
        const r = await context.request.get(`${apiOrigin}/api/v1/projects/${fixture.project_main}/import/${family}/status/${taskId}/`, { headers: await authHeaders(fixture.admin_auth.access) });
        return (await r.json()).status;
      }, { timeout: 60_000 }).toBe('done');
      await expect(page.getByRole('button', { name: locale.chooseAnother, exact: true })).toBeVisible({ timeout: 15_000 });
      expect(recoveryControl('jobs')[family].length).toBe(before[family].length + 1);
    } finally {
      await context.setOffline(false);
      recoveryControl('release');
    }
  });
}

test('planner cannot read foreign schedule or baseline through browser or forged IDs (NEG-11)', async ({ page, context }) => {
  expect(fixture.private_activity).toBeTruthy();
  expect(fixture.private_baseline).toBeTruthy();
  await loginPlanner(page, context);
  const headers = await authHeaders(fixture.admin_auth.access);
  // A permitted control proves these are authorization checks with a valid login.
  for (const suffix of ['wbs/', 'activities/', 'baselines/', 'gantt/', 'schedule-status/']) {
    const own = await context.request.get(`${apiOrigin}/api/v1/projects/${fixture.project_main}/${suffix}`, { headers });
    expect(own.status()).toBe(200);
    const foreign = await context.request.get(`${apiOrigin}/api/v1/projects/${fixture.project_b}/${suffix}`, { headers });
    expect([403, 404]).toContain(foreign.status());
    for (const marker of fixture.private_markers!) expect(await foreign.text()).not.toContain(marker);
  }
  for (const project of [fixture.project_main, fixture.project_b]) {
    const job = await context.request.get(`${apiOrigin}/api/v1/projects/${project}/import/msp/status/${fixture.private_job}/`, { headers });
    expect([403, 404]).toContain(job.status());
  }
  const forged = await context.request.get(`${apiOrigin}/api/v1/projects/${fixture.project_main}/activities/${fixture.private_activity}/`, { headers });
  expect(forged.status()).toBe(404);
  const borrowedBaseline = await context.request.get(`${apiOrigin}/api/v1/projects/${fixture.project_main}/gantt/?baseline_id=${fixture.private_baseline}`, { headers });
  expect(borrowedBaseline.status()).toBe(200);
  for (const marker of fixture.private_markers!) expect(await borrowedBaseline.text()).not.toContain(marker);
  const beforeB = JSON.parse(execFileSync('python3', [path.join(root, 'ops/a7-p5/snapshot-project.py'), fixture.project_b], { encoding: 'utf8' }));
  const patch = await context.request.patch(`${apiOrigin}/api/v1/projects/${fixture.project_main}/baselines/${fixture.private_baseline}/activities/${fixture.private_baseline_activity}/`, { headers, data: { planned_duration: 999 } });
  expect(patch.status()).toBe(404);
  expect(JSON.parse(execFileSync('python3', [path.join(root, 'ops/a7-p5/snapshot-project.py'), fixture.project_b], { encoding: 'utf8' }))).toEqual(beforeB);
  for (const route of ['gantt', 'status']) {
    const ownData = page.waitForResponse(r => r.url().endsWith(`/api/v1/projects/${fixture.project_main}/${route === 'gantt' ? 'gantt' : 'schedule-status'}/`) && r.status() === 200);
    await page.goto(`/projects/${fixture.project_main}/schedule/${route}`);
    await ownData;
    for (const marker of fixture.private_markers!) await expect(page.getByText(marker, { exact: false })).toHaveCount(0);
    const denied = page.waitForResponse(r => r.url().includes(`/api/v1/projects/${fixture.project_b}/`) && [403, 404].includes(r.status()));
    await page.goto(`/projects/${fixture.project_b}/schedule/${route}`);
    await denied;
    await expect(page.getByTestId('msp-import-btn')).toHaveCount(0);
    for (const marker of fixture.private_markers!) await expect(page.getByText(marker, { exact: false })).toHaveCount(0);
  }
});

test('project-switch and viewer account-switch isolation in browser (I10, NEG-11, NEG-12)', async ({
  page,
  context,
}) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await context.addCookies([
    {
      name: 'auth_token',
      value: fixture.admin_auth.access,
      domain: '127.0.0.1',
      path: '/',
    },
  ]);
  await page.addInitScript(
    ({ auth, mainProject }) => {
      localStorage.setItem('auth_access_token', auth.access);
      localStorage.setItem('auth_refresh_token', auth.refresh);
      localStorage.setItem('auth_user', JSON.stringify(auth.user));
      localStorage.setItem('app-language', 'fa');
      localStorage.setItem('i18nextLng', 'fa');
      sessionStorage.setItem(
        `schedule-import-attempt:${auth.user.id}:${mainProject}`,
        JSON.stringify({
          user_id: auth.user.id,
          project_id: mainProject,
          task_id: '00000000-0000-0000-0000-000000000001',
          file_name: 'project-main-only.xml',
          recognized_kind: 'xml',
          replace: false,
        }),
      );
    },
    { auth: fixture.admin_auth, mainProject: fixture.project_main },
  );

  // Navigate to Project B and verify Project Main's attempt does not bleed into Project B's dialog
  await page.goto(`/projects/${fixture.project_b}/wbs`);
  const importBtnB = page.getByTestId('msp-import-btn');
  await expect(importBtnB).toBeVisible({ timeout: 30_000 });
  await importBtnB.click();
  const dialogB = page.getByRole('dialog');
  await expect(dialogB).toBeVisible();
  await expect(dialogB.getByTestId('msp-import-file')).toBeAttached();
  await expect(dialogB.getByTestId('msp-import-filename')).toHaveCount(0);

  // NEG-11: cross-project isolation for schedule + baseline endpoints (admin owns both here;
  // use a second unauthenticated/forged probe via viewer who is only on project_main).
  const viewerHeaders = await authHeaders(fixture.viewer_auth.access);
  for (const pathSuffix of ['wbs/', 'activities/', 'gantt/', 'baselines/'] as const) {
    const denied = await context.request.get(
      `${apiOrigin}/api/v1/projects/${fixture.project_b}/${pathSuffix}`,
      { headers: viewerHeaders },
    );
    expect([403, 404]).toContain(denied.status());
  }

  // Switch to Viewer account and verify read-only WBS view (no msp-import-btn)
  await context.clearCookies();
  await context.addCookies([
    {
      name: 'auth_token',
      value: fixture.viewer_auth.access,
      domain: '127.0.0.1',
      path: '/',
    },
  ]);
  await page.evaluate(({ viewerAuth }) => {
    localStorage.setItem('auth_access_token', viewerAuth.access);
    localStorage.setItem('auth_refresh_token', viewerAuth.refresh);
    localStorage.setItem('auth_user', JSON.stringify(viewerAuth.user));
  }, { viewerAuth: fixture.viewer_auth });

  await page.goto(`/projects/${fixture.project_main}/wbs`);
  await expect(page.getByTestId('msp-import-btn')).toHaveCount(0);

  // NEG-12: viewer cannot mutate project or create baseline
  const projectPatch = await context.request.patch(
    `${apiOrigin}/api/v1/projects/${fixture.project_main}/`,
    {
      headers: {
        ...(await authHeaders(fixture.viewer_auth.access)),
        'Content-Type': 'application/json',
      },
      data: { employer: 'viewer-forbidden' },
    },
  );
  expect(projectPatch.status()).toBe(403);
  const baselineCreate = await context.request.post(
    `${apiOrigin}/api/v1/projects/${fixture.project_main}/baselines/`,
    {
      headers: {
        ...(await authHeaders(fixture.viewer_auth.access)),
        'Content-Type': 'application/json',
      },
      data: { version_name: 'viewer-forbidden-baseline', make_current: true },
    },
  );
  expect(baselineCreate.status()).toBe(403);

  await page.screenshot({
    path: path.join(screenshotsDir, 'viewer-readonly-fa-1280.png'),
    fullPage: true,
  });
});

for (const item of [{ lang: 'fa', width: 1280 }, { lang: 'en', width: 390 }]) {
  test(`viewer project and baseline are read-only in UI and direct browser requests (${item.lang} ${item.width}) (NEG-12)`, async ({ page, context }) => {
    expect(fixture.viewer_wbs).toBeTruthy();
    const locale = JSON.parse(fs.readFileSync(path.join(root, `apps/web/src/app/locales/${item.lang}.json`), 'utf8'));
    await page.setViewportSize({ width: item.width, height: item.width === 390 ? 844 : 800 });
    await context.addCookies([{ name: 'auth_token', value: fixture.viewer_auth.access, domain: '127.0.0.1', path: '/' }]);
    await page.addInitScript(({ auth, lang }) => {
      localStorage.setItem('auth_access_token', auth.access);
      localStorage.setItem('auth_refresh_token', auth.refresh);
      localStorage.setItem('auth_user', JSON.stringify(auth.user));
      localStorage.setItem('app-language', lang);
      localStorage.setItem('i18nextLng', lang);
    }, { auth: fixture.viewer_auth, lang: item.lang });
    const snapshot = () => JSON.parse(execFileSync('python3', [path.join(root, 'ops/a7-p5/snapshot-project.py'), fixture.project_main], { encoding: 'utf8' }));
    const before = snapshot();
    const headers = await authHeaders(fixture.viewer_auth.access);
    for (const path of ['', 'wbs/', 'activities/', 'baselines/', 'gantt/', 'schedule-status/', 'kickoff-charter/']) {
      const read = await context.request.get(`${apiOrigin}/api/v1/projects/${fixture.project_main}/${path}`, { headers });
      expect(read.status(), path).toBe(200);
    }
    await page.goto(`/projects/${fixture.project_main}/settings`);
    await expect(page.locator('#input-projectName')).toBeDisabled();
    await expect(page.getByTestId('settings-purpose')).toBeDisabled();
    await expect(page.getByRole('button', { name: locale.projectSettings.save, exact: true })).toHaveCount(0);
    await page.goto(`/projects/${fixture.project_main}/wbs`);
    await expect(page.getByTestId('msp-import-btn')).toHaveCount(0);
    await expect(page.getByTestId('wbs-row-1')).toBeVisible();
    const baselinesLoaded = page.waitForResponse(r => r.url().endsWith(`/api/v1/projects/${fixture.project_main}/baselines/`) && r.status() === 200);
    await page.goto(`/projects/${fixture.project_main}/schedule/gantt`);
    await baselinesLoaded;
    const baselinePanel = page.getByTestId('baseline-lock-panel');
    await expect(baselinePanel).toContainText(fixture.viewer_baseline_name!);
    await expect(baselinePanel.getByRole('button', { name: locale.schedule.createSnapshot, exact: true })).toHaveCount(0);
    await expect(baselinePanel.getByRole('button', { name: locale.schedule.approveLock, exact: true })).toHaveCount(0);
    // Use browser fetch, as a user bypassing disabled controls in developer tools could.
    const results = await page.evaluate(async ({ origin, pid, baseline, ba, wbs, activity, xml, xer }) => {
      const base = `${origin}/api/v1/projects/${pid}/`;
      const authorization = `Bearer ${localStorage.getItem('auth_access_token')}`;
      const writes: [string, string, Record<string, unknown>][] = [
        ['PATCH', '', { project_name: 'Forbidden rename' }],
        ['DELETE', '', {}],
        ['PUT', 'kickoff-charter/', { justification: 'Forbidden charter' }],
        ['POST', 'baselines/', { version_name: 'Forbidden baseline' }],
        ['POST', `baselines/${baseline}/approve-lock/`, {}],
        ['PATCH', `baselines/${baseline}/activities/${ba}/`, { planned_duration: 999 }],
        ['DELETE', `baselines/${baseline}/activities/${ba}/`, {}],
        ['POST', 'wbs/', { wbs_code: 'FORBIDDEN', wbs_name: 'Forbidden' }],
        ['PATCH', `wbs/${wbs}/`, { wbs_name: 'Forbidden rename' }],
        ['DELETE', `wbs/${wbs}/`, {}],
        ['PATCH', `activities/${activity}/`, { activity_name: 'Forbidden rename' }],
      ];
      const outcomes: { path: string; status: number }[] = [];
      for (const [method, path, data] of writes) {
        const r = await fetch(base + path, { method, headers: { Authorization: authorization, 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
        outcomes.push({ path: `${method} ${path}`, status: r.status });
      }
      for (const [family, name, content] of [['msp', 'branch.xml', xml], ['p6', 'branch.xer', xer]]) {
        for (const suffix of ['preview/', '']) {
          const data = new FormData();
          data.append('file', new File([content], name, { type: family === 'msp' ? 'application/xml' : 'application/octet-stream' }));
          const r = await fetch(base + `import/${family}/` + suffix, { method: 'POST', headers: { Authorization: authorization }, body: data });
          outcomes.push({ path: `import/${family}/${suffix}`, status: r.status });
        }
      }
      return outcomes;
    }, { origin: apiOrigin, pid: fixture.project_main, baseline: fixture.private_baseline!, ba: fixture.private_baseline_activity!, wbs: fixture.viewer_wbs!, activity: fixture.private_activity!, xml: validXmlBuffer.toString('utf8'), xer: fs.readFileSync(path.join(root, 'specs/051-a7-p1-project-reference/evidence/fixtures/branch.xer'), 'utf8') });
    for (const result of results) expect(result.status, result.path).toBe(403);
    expect(snapshot()).toEqual(before);
  });
}
