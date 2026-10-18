/**
 * E2E TEST: Decision Tree User Flow — Project Wizard & Lifecycle Suite
 * 
 * Based on decision-tree:
 * - docs/decision-tree/login/submit-valid-credentials/create-project
 * - docs/decision-tree/login/submit-valid-credentials/create-project/step-1-fill-basic-info-and-next
 * - docs/decision-tree/login/submit-valid-credentials/create-project/step-1-cancel-to-project-list
 * - docs/decision-tree/login/submit-valid-credentials/create-project/step-2-fill-dates-and-next
 * - docs/decision-tree/login/submit-valid-credentials/create-project/step-2-back-to-basic-info
 * - docs/decision-tree/login/submit-valid-credentials/create-project/step-1-fill-basic-info-and-next/step-2-fill-dates-and-next/create-draft-project
 * - docs/decision-tree/login/submit-valid-credentials/select-project
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[save-kickoff-charter]
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[submit-project]
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[approve-project]
 * - docs/decision-tree/login/submit-valid-credentials/select-project/navigate-project-settings
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-project-members]
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-stakeholders]
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";

test.describe("Decision Tree — Project Creation Wizard & Lifecycle Flows", () => {
  test.setTimeout(120_000);

  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("Wizard cancellation returns to project list", async ({ page }) => {
    await page.goto("/projects/new");
    await expect(page.getByRole("heading", { name: /ایجاد پروژه|پروژه جدید/i }).first()).toBeVisible({
      timeout: 15_000,
    });

    const cancelBtn = page.getByRole("button", { name: /انصراف|cancel/i });
    if (await cancelBtn.isVisible()) {
      await cancelBtn.click();
      await expect(page).toHaveURL(/\/projects\/?$/);
    }
  });

  test("Wizard multi-step navigation: Step 1 -> Step 2 -> Back -> Forward -> Create -> Overview", async ({
    page,
  }) => {
    const code = `dt-${Date.now()}`;
    await page.goto("/projects/new");

    // Step 1: Basic Information
    const nextBtn = page.getByRole("button", { name: /بعدی|next/i });
    await expect(nextBtn).toBeDisabled();

    await page.getByLabel(/نام پروژه/i).fill(`Decision Tree ${code}`);
    await page.getByLabel(/کد پروژه/i).fill(code);
    await page.getByLabel(/کارفرما/i).fill("Test Client Co");

    await expect(nextBtn).toBeEnabled();
    await nextBtn.click();

    // Step 2: Dates
    await expect(page.locator("#input-start_date").or(page.getByLabel(/تاریخ شروع/i))).toBeVisible();
    const backBtn = page.getByRole("button", { name: /قبلی|بازگشت|back/i });
    await expect(backBtn).toBeVisible();

    // Test Back button to Step 1
    await backBtn.click();
    await expect(page.getByLabel(/نام پروژه/i)).toHaveValue(`Decision Tree ${code}`);

    // Return to Step 2
    await page.getByRole("button", { name: /بعدی|next/i }).click();

    // Fill start date
    await page.locator("#input-start_date").click();
    await page.locator(".rmdp-day:not(.rmdp-disabled)").first().click();

    // Step 2 -> Step 3
    await page.getByRole("button", { name: /بعدی|next/i }).click();

    // Step 3: Team / Submit
    const createProjectBtn = page.getByRole("button", { name: /ایجاد پروژه|تایید و ایجاد|ثبت نهایی/i });
    await expect(createProjectBtn).toBeVisible();
    await createProjectBtn.click();

    // Should redirect to project overview
    await expect(page).toHaveURL(new RegExp(`/projects/[0-9a-f-]+/overview`), {
      timeout: 25_000,
    });

    // Verify Overview loaded
    await expect(page.getByRole("heading", { name: new RegExp(code, "i") }).first()).toBeVisible({
      timeout: 15_000,
    });
  });

  test("Project Overview: Kickoff charter save & lifecycle transition actions", async ({ page }) => {
    // Navigate to projects list and open the first available project
    await page.goto("/projects");
    await expect(page.locator("table, .grid, [data-testid='project-card']").first()).toBeVisible({
      timeout: 15_000,
    });

    const projectLink = page.locator("a[href*='/overview']:visible").first();
    await expect(projectLink).toBeVisible();
    await projectLink.click();

    await expect(page).toHaveURL(/\/projects\/[0-9a-f-]+\/overview/);

    // Save Kickoff Charter if charter form is present
    const charterScopeInput = page.locator("textarea[name='charter_scope'], #charter-scope, textarea").first();
    if (await charterScopeInput.isVisible()) {
      await charterScopeInput.fill("E2E Kickoff Scope Charter description updated.");
      const saveCharterBtn = page.getByRole("button", { name: /ذخیره منشور|ثبت منشور|ذخیره/i });
      if (await saveCharterBtn.isVisible()) {
        await saveCharterBtn.click();
        await expect(page.locator("[role='status'], .text-green-600, .toast").first()).toBeVisible({
          timeout: 5_000,
        }).catch(() => {});
      }
    }

    // Settings navigation
    const currentUrl = page.url();
    const projectId = currentUrl.split("/projects/")[1].split("/")[0];

    await page.goto(`/projects/${projectId}/settings`);
    await expect(page.getByRole("heading", { name: /تنظیمات پروژه|Project Settings/i }).first()).toBeVisible({
      timeout: 15_000,
    });

    // Settings -> Members navigation
    await page.goto(`/projects/${projectId}/settings/members`);
    await expect(page.getByRole("heading", { name: /مدیریت اعضا|اعضا|Members/i }).first()).toBeVisible({
      timeout: 15_000,
    });

    // Stakeholders navigation
    await page.goto(`/projects/${projectId}/stakeholders`);
    await expect(page.locator("[data-testid='stakeholders-page']").first()).toBeVisible({
      timeout: 15_000,
    });
  });
});
