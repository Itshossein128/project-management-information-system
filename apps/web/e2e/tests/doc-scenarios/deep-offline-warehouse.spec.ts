/**
 * Specs 037, 042, and 043. Helpers match apps/web/e2e/helpers.
 * Assertions follow the spec text. Product code is not changed when a test fails.
 */
import { expect, test, type Page } from "@playwright/test";
import { E2E_USERS, loginAs } from "../../helpers/auth";
import { createProjectViaApi } from "../../helpers/project";

async function openDepartment(page: Page, department: "warehouse" | "buildings" | "electrical") {
  await loginAs(page, E2E_USERS.admin);
  const projectBase = await createProjectViaApi(page);
  await page.goto(`${projectBase}/${department}`);
  await expect(page).toHaveURL(new RegExp(`/${department}/?`));
  return projectBase;
}

test.describe("037 offline sync on the current unit page", () => {
  test.setTimeout(90_000);

  test("an offline edit stays on the unit form and shows pending sync", async ({ page, context }) => {
    await loginAs(page, E2E_USERS.admin);
    const projectBase = await createProjectViaApi(page);
    await page.goto(`${projectBase}/electrical?date=2026-10-27`);
    await expect(page.locator("#button-createUnitReportDraft")).toBeVisible();
    await context.setOffline(true);
    await page.locator("#button-createUnitReportDraft").click();
    const notes = page.getByTestId("unit-report-general-notes");
    await notes.fill("Edited while offline");
    await page.getByTestId("unit-report-save-btn").click();
    await expect(notes).toHaveValue("Edited while offline");
    await expect(page.getByText("در انتظار همگام‌سازی").first()).toBeVisible();
  });
});

test.describe("043 warehouse department reports", () => {
  test.setTimeout(90_000);

  test("create form shows the documented warehouse fields", async ({ page }) => {
    await openDepartment(page, "warehouse");
    await page.locator("#button-openDepartmentActivityCreateModal").click();
    for (const label of ["تاریخ", "نوع مصالح", "ورودی", "واحد", "خروجی", "محل مصرف", "تامین‌کننده", "توضیحات"]) {
      await expect(page.getByText(label, { exact: true }).first()).toBeVisible();
    }
  });

  test("zero inbound and outbound shows the positive-quantity message", async ({ page }) => {
    await openDepartment(page, "warehouse");
    await page.locator("#button-openDepartmentActivityCreateModal").click();
    await page.locator("#input-departmentActivityMaterialType").fill("سیمان");
    await page.locator("#input-departmentActivityQuantityIn").fill("0");
    await page.locator("#input-departmentActivityQuantityOut").fill("0");
    await page.locator("#input-departmentActivityConsumptionLocation").fill("سقف");
    await page.locator("#input-departmentActivitySupplier").fill("کارخانه");
    await page.locator("#input-departmentActivityUnit").click();
    await page.getByRole("option").first().click();
    await page.locator("#button-submitDepartmentActivityRecordCreate").click();
    await expect(page.getByText("حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد")).toBeVisible();
  });

  test("warehouse export buttons use the Shiraz labels", async ({ page }) => {
    await openDepartment(page, "warehouse");
    await expect(page.getByRole("button", { name: "دانلود گزارش روزانه انبار (شیراز)" })).toBeVisible();
    await expect(page.getByRole("button", { name: "دانلود گزارش هفتگی و بالانس تجمعی مصالح (۸ شیت)" })).toBeVisible();
  });
});

test.describe("042 department activity reports", () => {
  test.setTimeout(90_000);

  test("buildings page exposes the documented weekly report action", async ({ page }) => {
    await openDepartment(page, "buildings");
    await expect(page.getByRole("button", { name: "دانلود گزارش هفتگی" })).toBeVisible();
    await expect(page.getByRole("button", { name: /خروجی اکسل|گزارش روزانه/ })).toBeVisible();
  });
});
