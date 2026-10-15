import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
import { session, visit } from "../helpers/navigation";

// Read the authoritative catalog so newly added API permissions cannot silently
// ship without translations. The API itself stays mocked; no real grants change.
const constants = readFileSync("apps/api/core/permissions/constants.py", "utf8");
const catalog = [...constants.split("ALL_PERMISSION_CODENAMES")[0].matchAll(/'([^']+)': '([^']+)'/g)]
  .map(([, codename, label]) => ({ codename, label }));
const systemCodes = [...constants.split("DEFAULT_ROLE_PERMISSIONS")[1]
  .split("DEFAULT_ROLE_DESCRIPTIONS")[0].matchAll(/^    '([^']+)':/gm)].map(([, code]) => code);
const locales = Object.fromEntries(["en", "fa"].map(language => [language,
  JSON.parse(readFileSync(`apps/web/src/app/locales/${language}.json`, "utf8")),
]));

test.beforeEach(async ({ page }, info) => {
  test.skip(info.project.name === "pwa-offline", "Requires dev server");
  await session(page);
  await page.route("**/api/v1/permissions/", route => route.fulfill({ json: catalog }));
  await page.route("**/api/v1/roles/", route => route.fulfill({ json: [
    ...systemCodes.map(code => ({ id: code, role_name: code,
      description: "API fallback description", is_system: true, permissions: ["view_project"] })),
    { id: "custom", role_name: "نقش سفارشی تیم", description: "توضیحات تیم",
      is_system: false, permissions: ["view_project"] },
  ] }));
});

test("member permission summaries and overrides use the same bilingual labels", async ({ page }) => {
  const projectId = "11111111-1111-4111-8111-111111111111";
  const base = `/api/v1/projects/${projectId}`;
  await page.route(`**${base}/`, route => route.fulfill({ json: {
    id: projectId, project_id: projectId, project_name: "Localization project", status: "draft",
  } }));
  await page.route(`**${base}/members/`, route => route.fulfill({ json: [{
    user_id: "member", full_name: "Test member", email: "", mobile: "", roles: ["viewer"],
    status: "active", joined_at: "2026-10-15", last_login: null,
  }] }));
  await page.route(`**${base}/members/*/permissions/`, route => route.fulfill({ json: {
    effective: { view_project: true, manage_members: true },
    permissions: [
      { codename: "view_project", label: "View project", granted: true },
      { codename: "future_permission", label: "Future catalog label", granted: true },
    ],
  } }));
  await visit(page, `/projects/${projectId}/settings/members`, "fa");
  await page.getByRole("button", { name: locales.fa.projectMembers.edit, exact: true }).click();
  for (const language of ["fa", "en"]) {
    const locale = locales[language];
    // The drawer blocks the header while open; close and reopen to switch locale.
    if (language === "en") {
      await page.keyboard.press("Escape");
      await page.locator("#button-language-en").click();
      await page.getByRole("button", { name: locale.projectMembers.edit, exact: true }).click();
    }
    const drawer = page.getByRole("dialog");
    await expect(drawer.getByText(`${locale.permissionLabels.view_project} · Future catalog label`, { exact: true })).toBeVisible();
    const advanced = drawer.getByRole("button", { name: new RegExp(locale.projectMembers.advancedPermissions) });
    // Drawer state may survive closing it during the language change.
    if (!(await drawer.getByRole("cell", { name: "Future catalog label", exact: true }).isVisible())) await advanced.click();
    await expect(drawer.getByRole("cell", { name: locale.permissionLabels.view_project, exact: true })).toBeVisible();
    await expect(drawer.getByRole("cell", { name: "Future catalog label", exact: true })).toBeVisible();
  }
});

test("all permission labels and system roles follow the selected language", async ({ page }) => {
  await visit(page, "/settings/roles", "fa");
  await page.getByRole("button", { name: /تصویب‌کننده ارشد/ }).click();
  for (const language of ["fa", "en", "fa"]) {
    await page.locator(`#button-language-${language}`).click();
    const locale = locales[language];
    await expect(page.getByRole("heading", { name: locale.roleLabels.executive_approver, exact: true })).toBeVisible();
    for (const code of systemCodes) {
      expect(locale.roleLabels[code], `${language} role ${code}`).toBeTruthy();
      expect(locale.roleDescriptions[code], `${language} description ${code}`).toBeTruthy();
      await expect(page.getByRole("button", { name: `${locale.roleLabels[code]} ${locale.roleDescriptions[code]}`, exact: true })).toBeVisible();
    }
    await expect(page.getByRole("checkbox")).toHaveCount(catalog.length);
    for (const { codename } of catalog) {
      const label = locale.permissionLabels?.[codename];
      expect(label, `${language} permission ${codename}`).toBeTruthy();
      const checkbox = page.getByRole("checkbox", { name: label, exact: true });
      await expect(checkbox).toBeDisabled();
      if (language === "fa") expect(label).toMatch(/[\u0600-\u06ff]/);
    }
    await expect(page.getByRole("checkbox", { name: locale.permissionLabels.view_project, exact: true })).toBeChecked();
    await expect(page.getByRole("button", { name: /نقش سفارشی تیم توضیحات تیم/ })).toBeVisible();
  }
});

test("language changes preserve draft grants and save the original permission codes", async ({ page }) => {
  await visit(page, "/settings/roles", "fa");
  await page.getByRole("button", { name: /نقش سفارشی تیم توضیحات تیم/ }).click();
  await page.getByRole("checkbox", { name: "ویرایش پروژه", exact: true }).check();
  await page.locator("#button-language-en").click();
  await expect(page.getByRole("heading", { name: "نقش سفارشی تیم", exact: true })).toBeVisible();
  await expect(page.getByRole("checkbox", { name: "Edit project", exact: true })).toBeChecked();
  await page.route("**/api/v1/roles/custom/permissions/", async route => {
    expect(route.request().method()).toBe("PUT");
    expect(route.request().postDataJSON()).toEqual({ permissions: ["view_project", "edit_project"] });
    await route.fulfill({ json: {} });
  });
  const saved = page.waitForResponse("**/api/v1/roles/custom/permissions/");
  await page.getByRole("button", { name: "Save permissions", exact: true }).click();
  await saved;
});
