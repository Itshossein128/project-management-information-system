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
}

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

test('lifecycle complete -> undo_completion and archive -> restore in browser (POS-10)', async ({
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

  // 1. Complete -> Undo completion
  const completeBtn = lifecycleBar.getByRole('button', {
    name: tFa.project?.complete ?? 'خاتمه',
    exact: true,
  });
  await expect(completeBtn).toBeVisible();
  await completeBtn.click();

  const undoSection = page.getByTestId('project-status-undo-undo_completion');
  await expect(undoSection).toBeVisible({ timeout: 20_000 });
  await page.screenshot({
    path: path.join(screenshotsDir, 'lifecycle-completed-undo-fa-1280.png'),
    fullPage: true,
  });

  await undoSection.getByRole('button').first().click();
  const undoDialog = page.getByRole('dialog');
  await expect(undoDialog).toBeVisible();
  const undoTextarea = undoDialog.locator(
    `#status-undo-reason-undo_completion-${fixture.project_main}`,
  );
  await expect(undoTextarea).toBeVisible({ timeout: 15_000 });
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
  await page.screenshot({
    path: path.join(screenshotsDir, 'lifecycle-archived-restore-fa-1280.png'),
    fullPage: true,
  });

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
});

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
            `http://127.0.0.1:18000/api/v1/projects/${item.project}/import/msp/status/${taskId}/`,
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
  await page.screenshot({
    path: path.join(screenshotsDir, 'viewer-readonly-fa-1280.png'),
    fullPage: true,
  });
});
