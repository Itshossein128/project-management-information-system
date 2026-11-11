import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";

// Real isolated API and browser. Do not intercept or mock responses.
const f = JSON.parse(readFileSync(process.env.A6_P1_E2E_FIXTURES!, "utf8"));
const api = process.env.A6_P1_E2E_API!.replace(/\/$/, "");
const members = `${api}/v1/projects/${f.project_a}/members/`;
const history = `${api}/v1/projects/${f.project_a}/access-changes/`;

const copy = {
  fa: {
    phone: "شماره تلفن",
    password: "رمز عبور",
    signIn: "ورود",
    add: "افزودن عضو",
    search: "جستجو",
    save: "ذخیره",
    edit: "ویرایش",
    advanced: "دسترسی‌های پیشرفته",
    deny: "رد",
    grant: "اعطا",
    inherit: "ارث",
    close: "بستن",
    history: "تاریخچه دسترسی",
    status: "وضعیت",
    missing: "کاربر یافت نشد",
    viewer: "مشاهده‌کننده",
    manager: "مدیر پروژه",
  },
  en: {
    phone: "Phone number",
    password: "Password",
    signIn: "Sign in",
    add: "Add member",
    search: "Search",
    save: "Save",
    edit: "Edit",
    advanced: "Advanced permissions",
    deny: "Deny",
    grant: "Grant",
    inherit: "Inherit",
    close: "Close",
    history: "Access history",
    status: "Status",
    missing: "User not found",
    viewer: "Viewer",
    manager: "Project manager",
  },
} as const;

async function browserLogin(page: Page, lang: "fa" | "en") {
  const text = copy[lang];
  await page.addInitScript((language) => {
    localStorage.setItem("app-language", language);
    localStorage.setItem("i18nextLng", language);
  }, lang);
  await page.goto("/login");
  await page.waitForLoadState("networkidle");
  await page.getByRole("textbox", { name: text.phone }).fill(f.users.manager.mobile);
  await page.getByLabel(text.password, { exact: true }).fill(f.password);
  await page.getByRole("button", { name: text.signIn, exact: true }).click();
  await expect(page).not.toHaveURL(/\/login/);
}

for (const lang of ["fa", "en"] as const) {
  const person = lang === "fa" ? f.users.new : f.users.writer;

  test(`${lang}: create, assign, exception, revoke, and history through the screen`, async ({ page, request }) => {
    const runtimeErrors: string[] = [];
    page.on("pageerror", error => runtimeErrors.push(error.message));
    const text = copy[lang];
    await browserLogin(page, lang);
    await page.goto(`/projects/${f.project_a}/settings/members`);
    await page.getByRole("button", { name: text.add, exact: true }).click();
    const dialog = page.getByRole("dialog");
    const searchBox = dialog.getByRole("textbox").first();
    await searchBox.fill("zzzz-missing");
    await dialog.getByRole("button", { name: text.search, exact: true }).click();
    await expect(dialog.getByText(text.missing)).toBeVisible();

    await searchBox.fill(person.username);
    await dialog.getByRole("button", { name: text.search, exact: true }).click();
    await dialog.getByRole("button", { name: new RegExp(person.name) }).click();
    await dialog.getByRole("checkbox", { name: new RegExp(text.viewer) }).check();
    await dialog.getByRole("checkbox", { name: new RegExp(text.manager) }).check();
    await dialog.getByRole("button", { name: text.save, exact: true }).click();
    await expect(dialog).toBeHidden();

    const row = page.locator("tr", { hasText: person.name });
    await row.getByRole("button", { name: text.edit, exact: true }).click();
    await dialog.getByRole("button", { name: text.advanced }).click();
    const deny = dialog.getByRole("radio", { name: new RegExp(`view_wage.*${text.deny}`) });
    const inherit = dialog.getByRole("radio", { name: new RegExp(`view_wage.*${text.inherit}`) });
    await deny.click();
    await expect(deny).toBeChecked();
    await dialog.getByRole("button", { name: text.close, exact: true }).click();

    await row.getByRole("button", { name: text.edit, exact: true }).click();
    await dialog.getByRole("button", { name: text.advanced }).click();
    await expect(deny).toBeChecked();
    await deny.focus();
    await page.keyboard.press(lang === "fa" ? "ArrowRight" : "ArrowLeft");
    await expect(dialog.getByRole("radio", { name: new RegExp(`view_wage.*${text.grant}`) })).toBeChecked();
    await inherit.click();
    await expect(inherit).toBeChecked();
    await dialog.getByRole("button", { name: text.close, exact: true }).click();

    await row.getByLabel(text.status).selectOption("inactive");
    await expect(row.getByLabel(text.status)).toHaveValue("inactive");

    const directMembers = await request.get(members, {
      headers: { Authorization: `Bearer ${f.tokens.manager}`, "Accept-Language": lang },
    });
    expect(directMembers.status()).toBe(200);
    const memberRows = await directMembers.json();
    const listed = (Array.isArray(memberRows) ? memberRows : memberRows.results).find(
      (item: { user_id: string }) => item.user_id === person.id,
    );
    expect(listed.status).toBe("inactive");
    expect(listed.roles.length).toBeGreaterThan(1);

    const directHistory = await request.get(`${history}?subject=${person.id}`, {
      headers: { Authorization: `Bearer ${f.tokens.manager}`, "Accept-Language": lang },
    });
    expect(directHistory.status()).toBe(200);
    const historyBody = await directHistory.json();
    const historyRows = historyBody.results ?? historyBody;
    expect(historyRows.some((item: { before: object; after: object }) => item.before && item.after)).toBe(true);

    await page.goto(`/projects/${f.project_a}/settings/access-history`);
    await expect(page.getByRole("heading", { name: text.history })).toBeVisible();
    await expect(page.getByRole("listitem").filter({ hasText: person.name }).first()).toBeVisible();
    expect(runtimeErrors).toEqual([]);
  });
}
