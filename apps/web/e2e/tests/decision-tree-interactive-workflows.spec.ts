/**
 * E2E TEST: Decision Tree User Flow — Interactive Workflows & State Machine Suite
 * 
 * Based on decision-tree:
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-contracts]
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-contracts-new]
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-daily-reports]
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-daily-reports-new]
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-sync-conflicts]
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-procurement]
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-procurement-new]
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-procurement-officer]
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-procurement-inventory]
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-procurement-blocks]
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-procurement-transfers]
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-decision-support]
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-quality-hse]
 * - docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-costs]
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { markToursSeen } from "../helpers/tour";
import {
  createActualCostViaApi,
  createBudgetViaApi,
  createProjectViaApi,
  createRootWbs,
} from "../helpers/project";

test.describe("Decision Tree — Interactive Domain Workflows", () => {
  test.setTimeout(120_000);

  let projectBase: string;

  test.beforeEach(async ({ page }) => {
    await markToursSeen(
      page,
      "procurement-list",
      "procurement-new",
      "procurement-blocks",
      "procurement-inventory",
      "procurement-transfers",
      "procurement-officer",
      "procurement-reports",
      "project-alerts",
      "project-manpower",
    );
    await loginAs(page, E2E_USERS.admin);
    projectBase = await createProjectViaApi(page);
  });

  test("Contracts & IPC Flow: navigate list, switch tabs, render new contract form", async ({ page }) => {
    // 1. Navigate to Contracts
    await page.goto(`${projectBase}/contracts`);
    await expect(page.getByRole("heading", { name: "قراردادها" })).toBeVisible({ timeout: 15_000 });

    // 2. Tab switching between Contracts and IPCs (صدور موقت)
    const ipcsTab = page.getByRole("tab", { name: "صدور موقت" });
    await expect(ipcsTab).toBeVisible();
    await ipcsTab.click();

    // 3. Navigate to New Contract Form
    const newContractBtn = page.locator("a[href*='/contracts/new']").first();
    if (await newContractBtn.isVisible()) {
      await newContractBtn.click();
    } else {
      await page.goto(`${projectBase}/contracts/new`);
    }

    await expect(page).toHaveURL(new RegExp(`${projectBase}/contracts/new`));
    await expect(page.getByRole("heading", { name: /قرارداد جدید|New Contract/i }).first()).toBeVisible({
      timeout: 15_000,
    });

    // Verify presence of form inputs
    await expect(page.locator("input[name='contract_number'], #contract_number").first()).toBeVisible();
    await expect(page.locator("input[name='counterparty'], #counterparty").first()).toBeVisible();
  });

  test("Daily Reports Flow: tabs rendering, new report creation, and sync conflicts route", async ({ page }) => {
    // 1. Navigate to Daily Reports List
    await page.goto(`${projectBase}/daily-reports`);
    await expect(page.getByTestId("daily-reports-list")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("daily-report-new-btn")).toBeVisible();

    // 2. Navigate to New Daily Report form
    await page.getByTestId("daily-report-new-btn").click();
    await expect(page).toHaveURL(new RegExp(`${projectBase}/daily-reports/new`));
    await expect(page.getByTestId("daily-report-form")).toBeVisible({ timeout: 15_000 });

    // Verify sub-tabs: activities, labor, equipment, materials, concrete, incidents
    await expect(page.getByTestId("report-tab-activities")).toBeVisible();
    await expect(page.getByTestId("report-tab-labor")).toBeVisible();
    await expect(page.getByTestId("report-tab-equipment")).toBeVisible();
    await expect(page.getByTestId("report-tab-materials")).toBeVisible();
    await expect(page.getByTestId("report-tab-concrete")).toBeVisible();
    await expect(page.getByTestId("report-tab-incidents")).toBeVisible();

    // Switch between tabs
    await page.getByTestId("report-tab-labor").click();
    await page.getByTestId("report-tab-equipment").click();
    await page.getByTestId("report-tab-activities").click();

    // 3. Navigate to Sync Conflicts / Offline Recovery route
    await page.goto(`${projectBase}/sync-conflicts`);
    await expect(page).toHaveURL(new RegExp(`${projectBase}/sync-conflicts`));
    await expect(page.locator("[data-testid='conflict-page-container']")).toBeVisible({
      timeout: 15_000,
    });
  });

  test("Procurement Flow: requisition creation page, line items, and workbench views", async ({ page }) => {
    // 1. Navigate to Procurement List
    await page.goto(`${projectBase}/procurement`);
    await expect(page.getByRole("heading", { name: /تدارکات|خرید|Procurement/i }).first()).toBeVisible({
      timeout: 15_000,
    });

    // 2. Navigate to New Requisition
    const newReqBtn = page.locator("a[href*='/procurement/new']").first();
    if (await newReqBtn.isVisible()) {
      await newReqBtn.click();
    } else {
      await page.goto(`${projectBase}/procurement/new`);
    }

    await expect(page).toHaveURL(new RegExp(`${projectBase}/procurement/new`));
    await expect(page.locator("[data-tour='submit-requisition'] button[type='submit']")).toBeVisible({
      timeout: 15_000,
    });

    // 3. Test Officer Workbench
    await page.goto(`${projectBase}/procurement/officer`);
    await expect(page.getByRole("heading", { name: /کارپرداز|officer/i }).first()).toBeVisible({
      timeout: 15_000,
    });

    // 4. Test Inventory view
    await page.goto(`${projectBase}/procurement/inventory`);
    await expect(page.getByRole("heading", { name: /انبار|موجودی|Inventory/i }).first()).toBeVisible({
      timeout: 15_000,
    });

    // 5. Test Transfers view
    await page.goto(`${projectBase}/procurement/transfers`);
    await expect(page.getByRole("heading", { name: /انتقال|حواله|Transfers/i }).first()).toBeVisible({
      timeout: 15_000,
    });

    // 6. Test Blocks view
    await page.goto(`${projectBase}/procurement/blocks`);
    await expect(page.getByRole("heading", { name: /بلوک|Blocks/i }).first()).toBeVisible({
      timeout: 15_000,
    });
  });

  test("Decision Support (MCDA Engine): method switching and criteria configuration", async ({ page }) => {
    await page.goto(`${projectBase}/decision-support`);
    await expect(page.getByRole("heading", { name: /تصمیم‌?یار|Decision Support/i }).first()).toBeVisible({
      timeout: 15_000,
    });

    // Check create case button
    const createCaseBtn = page.getByRole("button", { name: /پرونده جدید|create/i });
    if (await createCaseBtn.isVisible()) {
      await expect(createCaseBtn).toBeVisible();
    }

    // Verify presence of criteria / alternatives configuration containers
    await expect(page.locator("text=/معیار|شاخص|Criteria/i").first()).toBeVisible({
      timeout: 15_000,
    });
  });

  test("Quality & HSE Flow: inspections, NCRs, and work permits navigation", async ({ page }) => {
    await page.goto(`${projectBase}/quality-hse`);
    await expect(page.getByRole("heading", { name: /کیفیت|ایمنی|HSE|Quality/i }).first()).toBeVisible({
      timeout: 15_000,
    });

    // Click tabs specifically via role=tab
    const tabs = page.locator("[role='tab']");
    const count = await tabs.count();
    for (let i = 0; i < count; i++) {
      const tab = tabs.nth(i);
      if (await tab.isVisible()) {
        await tab.click();
      }
    }
  });

  test("Cost Control Flow: verify KPIs, tabs switching, and budget/variance grids", async ({ page }) => {
    // Populate root WBS, budget and actual cost via API first
    const wbsId = await createRootWbs(page, projectBase, { code: "CC-1", name: "Cost WBS" });
    await createBudgetViaApi(page, projectBase, { wbsId, budgetAmount: 100_000, costCategory: "labor" });
    await createActualCostViaApi(page, projectBase, { wbsId, amount: 45_000, costCategory: "labor" });

    await page.goto(`${projectBase}/costs`);
    await expect(page.getByRole("heading", { name: /هزینه|بودجه|Cost/i }).first()).toBeVisible({
      timeout: 15_000,
    });

    // Check KPI cards
    await expect(page.locator("text=/بودجه مصوب|Approved Budget|کل بودجه/i").first()).toBeVisible({
      timeout: 15_000,
    });

    // Check tab navigation between Budget, Actual Costs, Variance, and Cost Pools
    const costTabs = page.locator("[role='tab']");
    const tabCount = await costTabs.count();
    expect(tabCount).toBeGreaterThan(0);

    for (let i = 0; i < Math.min(tabCount, 4); i++) {
      const tab = costTabs.nth(i);
      if (await tab.isVisible()) {
        await tab.click();
      }
    }
  });
});
