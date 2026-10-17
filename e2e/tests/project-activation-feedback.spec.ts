import { expect, test, type Page } from "@playwright/test";
import { session, visit } from "../helpers/navigation";

// Real UI/router/API client, intercepted API traffic: never mutates live projects.
const projectId = "11111111-1111-4111-8111-111111111111";
const base = `/api/v1/projects/${projectId}`;
const overview = `/projects/${projectId}/overview`;
const settingsPath = `/projects/${projectId}/settings`;
const initialProject = {
  project_id: projectId, project_name: "Activation test", project_code: "TEST",
  can_resume_with_confirmation: false, employer: "Test employer", status: "pending_approval", start_date: "2026-01-01",
  contract_amount: null as string | null, scope_description: "", project_manager: "test-manager",
};
const gates = ["project_manager", "scope_description", "budget_approved"] as const;
const copy = {
  fa: {
    approve: "تصویب و فعال‌سازی", resume: "ازسرگیری", suspend: "تعلیق",
    title: "اطلاعات لازم برای فعال‌سازی پروژه کامل نیست", pending: "در انتظار تصویب",
    requirements: ["مدیر پروژه را تعیین کنید.", "شرح محدوده را وارد کنید.", "مبلغ قرارداد را وارد کنید."],
    unknown: "سایر اطلاعات الزامی پروژه را تکمیل کنید.", link: "تکمیل اطلاعات پروژه",
    contact: "برای تکمیل اطلاعات، با کاربری که مجوز ویرایش پروژه دارد تماس بگیرید.",
    success: "وضعیت پروژه به‌روز شد", save: "ذخیره", saved: "تغییرات ذخیره شد",
  },
  en: {
    approve: "Approve & activate", resume: "Resume", suspend: "Suspend",
    title: "Required information for project activation is incomplete", pending: "Pending approval",
    requirements: ["Assign a project manager.", "Enter the scope description.", "Enter the contract amount."],
    unknown: "Complete the other required project information.", link: "Complete project information",
    contact: "Ask someone with permission to edit the project to complete the information.",
    success: "Project status updated", save: "Save", saved: "Changes saved",
  },
};
type Language = keyof typeof copy;
function activationError(missing: unknown = gates) {
  return { error: { code: "activation_gates_failed", message: "Activation requirements not met.", details: { missing } } };
}
async function mockProject(page: Page, overrides: Partial<typeof initialProject> = {}) {
  await page.route(`**${base}/`, route => route.fulfill({ json: { ...initialProject, ...overrides } }));
}
async function mockFailure(page: Page, missing: unknown = gates, action = "approve") {
  await page.route(`**${base}/${action}/`, route => route.fulfill({ status: 400, json: activationError(missing) }));
}
function feedback(page: Page, language: Language = "fa") {
  return page.getByRole("alert").filter({ hasText: copy[language].title });
}
async function approve(page: Page, language: Language = "fa") {
  await page.getByRole("button", { name: copy[language].approve, exact: true }).click();
}
async function expectNoFalseSuccess(page: Page, language: Language = "fa") {
  await expect(page.getByText(copy[language].success, { exact: true })).toHaveCount(0);
  await expect(page.getByText(copy[language].pending, { exact: true })).toBeVisible();
  await expect(page.getByTestId("project-approve-btn")).toBeEnabled();
}

test.beforeEach(async ({ page }, info) => {
  test.skip(info.project.name === "pwa-offline", "Live frontend with intercepted API traffic");
  await session(page, ["admin"], "fa");
  await mockProject(page);
  await page.route(`**${base}/members/*/permissions/`, route => route.fulfill({ json: {
    effective: { view_project: true, edit_project: true, approve_project: true },
  } }));
});

for (const language of ["fa", "en"] as const) {
  test.describe(`${language} approval messages`, () => {
    for (let mask = 1; mask < 8; mask++) {
      const indexes = [0, 1, 2].filter(index => mask & (1 << index));
      const missing = indexes.map(index => gates[index]);
      test(`reports exactly these missing requirements: ${missing.join(", ")}`, async ({ page }) => {
        await mockFailure(page, missing);
        await visit(page, overview, language);
        await approve(page, language);
        const alert = feedback(page, language);
        await expect(alert.getByRole("listitem")).toHaveText(indexes.map(index => copy[language].requirements[index]));
        await expect(alert).not.toContainText("activation_gates_failed");
        await expect(alert).not.toContainText("Activation requirements not met.");
        await expect(alert.getByRole("link", { name: copy[language].link })).toHaveAttribute("href", settingsPath);
        await expectNoFalseSuccess(page, language);
      });
    }
    test("guidance persists and links to editable settings", async ({ page }) => {
      await mockFailure(page);
      await visit(page, overview, language);
      await approve(page, language);
      const alert = feedback(page, language);
      await expect(alert).toContainText(language === "fa" ? "تکمیل و ذخیره" : "Complete and save");
      await page.clock.install();
      await page.clock.fastForward(12_000);
      await expect(alert).toBeVisible();
      await alert.getByRole("link", { name: copy[language].link }).click();
      await expect(page).toHaveURL(settingsPath);
      await expect(page.getByTestId("settings-scope")).toBeEditable();
      await expect(page.getByTestId("settings-contract-amount")).toBeEditable();
    });
    test("an approver without edit permission is told to contact an editor", async ({ page }) => {
      await page.route(`**${base}/members/*/permissions/`, route => route.fulfill({ json: {
        effective: { view_project: true, approve_project: true, edit_project: false },
      } }));
      await mockFailure(page);
      await visit(page, overview, language);
      await approve(page, language);
      await expect(feedback(page, language)).toContainText(copy[language].contact);
      await expect(feedback(page, language).getByRole("listitem")).toHaveText(copy[language].requirements);
      await expect(feedback(page, language).getByRole("link")).toHaveCount(0);
    });
    test("success shows one translated message and refreshes project status", async ({ page }) => {
      let approved = false;
      let submissions = 0;
      await page.route(`**${base}/`, route => route.fulfill({ json: {
        ...initialProject, status: approved ? "active" : "pending_approval",
      } }));
      await page.route(`**${base}/approve/`, route => {
        expect(route.request().method()).toBe("POST");
        approved = true;
        submissions++;
        return route.fulfill({ json: { ...initialProject, status: "active" } });
      });
      await visit(page, overview, language);
      await approve(page, language);
      await expect(page.getByRole("alert").filter({ hasText: copy[language].success })).toHaveCount(1);
      await expect(page.getByRole("button", { name: copy[language].suspend, exact: true })).toBeVisible();
      await expect(page.getByTestId("project-approve-btn")).toHaveCount(0);
      await expect(feedback(page, language)).toHaveCount(0);
      expect(submissions).toBe(1);
    });
  });
}

test("language switching translates the existing error without another request", async ({ page }) => {
  let submissions = 0;
  await page.route(`**${base}/approve/`, route => {
    submissions++;
    return route.fulfill({ status: 400, json: activationError() });
  });
  await visit(page, overview, "fa");
  await approve(page);
  await expect(feedback(page)).toBeVisible();
  for (const language of ["en", "fa"] as const) {
    await page.locator(`#button-language-${language}`).click();
    await expect(feedback(page, language).getByRole("listitem")).toHaveText(copy[language].requirements);
    await expect(feedback(page, language).getByRole("link", { name: copy[language].link })).toBeVisible();
  }
  expect(submissions).toBe(1);
});

for (const scenario of [
  { name: "absent details", details: undefined, expected: [] },
  { name: "null details", details: null, expected: [] },
  { name: "no missing property", details: {}, expected: [] },
  { name: "empty missing list", details: { missing: [] }, expected: [] },
  { name: "missing is not a list", details: { missing: "scope_description" }, expected: [] },
  { name: "null missing list", details: { missing: null }, expected: [] },
  { name: "invalid and duplicate entries", details: { missing: [null, 42, {}, "scope_description", "scope_description"] }, expected: [copy.fa.requirements[1]] },
  { name: "unknown requirements", details: { missing: ["future_requirement", "constructor", "__proto__"] }, expected: [copy.fa.unknown, copy.fa.unknown, copy.fa.unknown] },
]) {
  test(`malformed activation metadata: ${scenario.name}`, async ({ page }) => {
    await page.route(`**${base}/approve/`, route => route.fulfill({ status: 400, json: {
      error: { code: "activation_gates_failed", message: "Activation requirements not met.", details: scenario.details },
    } }));
    await visit(page, overview, "fa");
    await approve(page);
    await expect(feedback(page)).toBeVisible();
    await expect(feedback(page).getByRole("listitem")).toHaveText(scenario.expected);
    await expect(feedback(page).getByRole("link", { name: copy.fa.link })).toBeVisible();
    await expectNoFalseSuccess(page);
  });
}

test("retries replace outdated requirements and success removes the guidance", async ({ page }) => {
  let attempts = 0;
  let status = "pending_approval";
  await page.route(`**${base}/`, route => route.fulfill({ json: { ...initialProject, status } }));
  await page.route(`**${base}/approve/`, route => {
    attempts++;
    if (attempts < 3) return route.fulfill({ status: 400, json: activationError(attempts === 1 ? gates : ["budget_approved"]) });
    status = "active";
    return route.fulfill({ json: { ...initialProject, status } });
  });
  await visit(page, overview, "fa");
  await approve(page);
  await expect(feedback(page).getByRole("listitem")).toHaveText(copy.fa.requirements);
  await approve(page);
  await expect(feedback(page).getByRole("listitem")).toHaveText([copy.fa.requirements[2]]);
  await approve(page);
  await expect(feedback(page)).toHaveCount(0);
  await expect(page.getByRole("alert").filter({ hasText: copy.fa.success })).toHaveCount(1);
  await expect(page.getByRole("button", { name: copy.fa.suspend, exact: true })).toBeVisible();
  expect(attempts).toBe(3);
});

test("follow the guidance, save missing fields, return and approve", async ({ page }) => {
  let project = { ...initialProject };
  await page.route(`**${base}/`, async route => {
    if (route.request().method() === "PATCH") project = { ...project, ...route.request().postDataJSON() };
    await route.fulfill({ json: project });
  });
  await page.route(`**${base}/approve/`, route => {
    if (!project.scope_description || !project.contract_amount) return route.fulfill({ status: 400, json: activationError(["scope_description", "budget_approved"]) });
    project = { ...project, status: "active" };
    return route.fulfill({ json: project });
  });
  await visit(page, overview, "fa");
  await approve(page);
  await feedback(page).getByRole("link", { name: copy.fa.link }).click();
  await page.getByTestId("settings-scope").fill("محدودهٔ تأییدشدهٔ پروژه");
  await page.getByTestId("settings-contract-amount").fill("1000.50");
  await page.getByRole("button", { name: copy.fa.save, exact: true }).click();
  await expect(page.getByRole("alert").filter({ hasText: copy.fa.saved })).toBeVisible();
  expect(project.scope_description).toBe("محدودهٔ تأییدشدهٔ پروژه");
  expect(project.contract_amount).toBe("1000.50");
  await page.getByRole("link", { name: initialProject.project_name, exact: true }).click();
  await expect(page).toHaveURL(overview);
  await approve(page);
  await expect(page.getByRole("alert").filter({ hasText: copy.fa.success })).toBeVisible();
  await expect(feedback(page)).toHaveCount(0);
  await expect(page.getByTestId("project-approve-btn")).toHaveCount(0);
});

test("pending request disables conflicting actions and prevents duplicate submissions", async ({ page }) => {
  let submissions = 0;
  let release!: () => void;
  const pending = new Promise<void>(resolve => { release = resolve; });
  await page.route(`**${base}/approve/`, async route => {
    submissions++;
    await pending;
    await route.fulfill({ status: 400, json: activationError() });
  });
  await visit(page, overview, "fa");
  try {
    await approve(page);
    await expect(page.getByTestId("project-approve-btn")).toBeDisabled();
    await expect(page.getByTestId("project-reject-btn")).toBeDisabled();
    await page.keyboard.press("Enter");
    await page.keyboard.press("Space");
    expect(submissions).toBe(1);
    await expect(feedback(page)).toHaveCount(0);
    await expect(page.getByText(copy.fa.success, { exact: true })).toHaveCount(0);
  } finally {
    release();
  }
  await expect(feedback(page)).toBeVisible();
  await expect(page.getByTestId("project-approve-btn")).toBeEnabled();
  await expect(page.getByTestId("project-reject-btn")).toBeEnabled();
});

for (const scenario of [
  { status: 403, code: "permission_denied", message: "اجازهٔ تصویب پروژه را ندارید." },
  { status: 404, code: "not_found", message: "پروژه یافت نشد." },
  { status: 400, code: "invalid_status_transition", message: "وضعیت پروژه تغییر کرده است." },
  { status: 400, code: "project_archived", message: "پروژه بایگانی شده است." },
  { status: 409, code: "conflict", message: "اطلاعات پروژه تغییر کرده است؛ صفحه را تازه کنید." },
  { status: 429, code: "throttled", message: "کمی صبر کنید و دوباره تلاش کنید." },
  { status: 500, code: "error", message: "خطای سرور؛ دوباره تلاش کنید." },
]) {
  test(`HTTP ${scenario.status} ${scenario.code} retains its own message`, async ({ page }) => {
    await page.route(`**${base}/approve/`, route => route.fulfill({ status: scenario.status, json: {
      error: { code: scenario.code, message: scenario.message, details: {} },
    } }));
    await visit(page, overview, "fa");
    await approve(page);
    await expect(page.getByRole("alert").filter({ hasText: scenario.message })).toBeVisible();
    await expect(feedback(page)).toHaveCount(0);
    await expectNoFalseSuccess(page);
  });
}
for (const scenario of [
  { name: "legacy detail", json: { detail: "Legacy validation message" }, body: undefined, expected: "Legacy validation message" },
  { name: "flat error", json: { error: "Flat validation message" }, body: undefined, expected: "Flat validation message" },
  { name: "plain text", json: undefined, body: "Service temporarily unavailable", expected: "Service temporarily unavailable" },
  { name: "empty response", json: undefined, body: "", expected: "Service Unavailable" },
]) {
  test(`nonstandard error response: ${scenario.name}`, async ({ page }) => {
    await page.route(`**${base}/approve/`, route => route.fulfill({ status: 503,
      ...(scenario.json ? { json: scenario.json } : { body: scenario.body }),
    }));
    await visit(page, overview, "fa");
    await approve(page);
    await expect(page.getByRole("alert").filter({ hasText: scenario.expected })).toBeVisible();
    await expect(feedback(page)).toHaveCount(0);
    await expectNoFalseSuccess(page);
  });
}

test("network failure displays an error and permits a successful retry of the request", async ({ page }) => {
  let submissions = 0;
  await page.route(`**${base}/approve/`, route => {
    if (++submissions === 1) return route.abort("failed");
    return route.fulfill({ status: 400, json: activationError() });
  });
  await visit(page, overview, "fa");
  await approve(page);
  await expect(page.getByRole("alert").filter({ hasText: /Failed to fetch|NetworkError|Load failed/ })).toBeVisible();
  await expect(feedback(page)).toHaveCount(0);
  await expectNoFalseSuccess(page);
  await approve(page);
  await expect(feedback(page)).toBeVisible();
  expect(submissions).toBe(2);
});

test("expired token refreshes once and preserves the retried approval error", async ({ page }) => {
  let submissions = 0;
  let refreshes = 0;
  await page.route("**/api/auth/token/refresh/", route => {
    refreshes++;
    return route.fulfill({ json: { access: "refreshed-test-token" } });
  });
  await page.route(`**${base}/approve/`, route => {
    if (++submissions === 1) return route.fulfill({ status: 401, json: { detail: "Token expired" } });
    expect(route.request().headers().authorization).toBe("Bearer refreshed-test-token");
    return route.fulfill({ status: 400, json: activationError() });
  });
  await visit(page, overview, "fa");
  await approve(page);
  await expect(feedback(page).getByRole("listitem")).toHaveText(copy.fa.requirements);
  expect(refreshes).toBe(1);
  expect(submissions).toBe(2);
});

test("session expiry redirects to login when refresh fails", async ({ page }) => {
  let submissions = 0;
  await page.route("**/api/auth/token/refresh/", route => route.fulfill({ status: 401, json: { detail: "Session expired" } }));
  await page.route(`**${base}/approve/`, route => {
    submissions++;
    return route.fulfill({ status: 401, json: { detail: "Token expired" } });
  });
  await visit(page, overview, "fa");
  await approve(page);
  await expect(page).toHaveURL(/\/login\?redirectTo=/);
  await expect(page.getByTestId("login-submit-btn")).toBeVisible();
  await expect(page.getByText(copy.fa.success, { exact: true })).toHaveCount(0);
  expect(submissions).toBe(1);
});

test("resume shares the translated activation guidance", async ({ page }) => {
  await mockProject(page, { status: "suspended", can_resume_with_confirmation: true });
  await page.route(`**${base}/resume-preview/`, route => route.fulfill({json:{project_id:projectId,project_name:initialProject.project_name,operation:"resume",source_event_id:projectId,from_status:"suspended",to_status:"active",lifecycle_version:1,confirmation_token:"signed",can_confirm:false,missing:["scope_description","budget_approved"],remediation:[]}}));
  await visit(page, overview, "en");
  await page.getByRole("button", { name: copy.en.resume, exact: true }).click();
  const items = page.getByRole("dialog").getByRole("listitem");
  await expect(items).toHaveCount(2);
  for (let index=0;index<2;index++) await expect(items.nth(index)).toContainText(copy.en.requirements[index+1]);
  await expect(page.getByRole("dialog").getByRole("button",{name:"Confirm status correction",exact:true})).toBeDisabled();
});
