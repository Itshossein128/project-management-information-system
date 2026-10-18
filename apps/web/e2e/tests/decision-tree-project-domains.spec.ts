/**
 * E2E TEST: Decision Tree User Flow — Project Domains Navigation Suite
 * 
 * Simulates user navigation across all 5 core project domains:
 * - Planning: WBS, Activities, Gantt, Schedule Status, Progress, Activity Log, Decision Support
 * - Field: Daily Reports, New Report, Sync Conflicts, Sub-reports, Concrete Ops, Weather, Barriers, Risk Register, Quality & HSE, Alerts
 * - Commercial: Contracts, New Contract, Subcontractors, Documents, Decisions & Workflow, Cash Flow, Costs, Material Balance, Procurement (List, New, Officer, Inventory, Reports, Blocks, Transfers), Economic Analysis
 * - Resources: Equipment Utilization, Equipment Log, Labor Productivity, Personnel Summary, Manpower, Labor Camp, Overtime, Leave, Allocations
 * - Reporting: Role Dashboard, Standard Reports
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createProjectViaApi } from "../helpers/project";
import { markToursSeen } from "../helpers/tour";

test.describe("Decision Tree — Comprehensive Project Domain Navigation Flows", () => {
  test.setTimeout(180_000);

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
  });

  test("Simulate user flow across Planning Domain pages and components", async ({ page }) => {
    const projectBasePath = await createProjectViaApi(page);

    // 1. WBS
    await page.goto(`${projectBasePath}/wbs`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/wbs`));
    await expect(page.locator("main, [data-testid='wbs-tree']").first()).toBeVisible({ timeout: 15_000 });

    // 2. Activities
    await page.goto(`${projectBasePath}/activities`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/activities`));
    await expect(page.locator("main, table, [data-testid='activities-list']").first()).toBeVisible({ timeout: 15_000 });

    // 3. Schedule Gantt
    await page.goto(`${projectBasePath}/schedule/gantt`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/schedule/gantt`));
    await expect(page.locator("main, [data-testid='gantt-chart'], .gantt").first()).toBeVisible({ timeout: 15_000 });

    // 4. Schedule Status
    await page.goto(`${projectBasePath}/schedule/status`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/schedule/status`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 5. Progress
    await page.goto(`${projectBasePath}/progress`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/progress`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 6. Activity Log
    await page.goto(`${projectBasePath}/activity-log`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/activity-log`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 7. Decision Support
    await page.goto(`${projectBasePath}/decision-support`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/decision-support`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });
  });

  test("Simulate user flow across Field Domain pages and components", async ({ page }) => {
    const projectBasePath = await createProjectViaApi(page);

    // 1. Daily Reports List
    await page.goto(`${projectBasePath}/daily-reports`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/daily-reports`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 2. Blank create route redirects to list (auto-summary)
    await page.goto(`${projectBasePath}/daily-reports/new`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/daily-reports/?$`));
    await expect(page.getByTestId("daily-reports-list")).toBeVisible({ timeout: 15_000 });

    // 3. Sync Conflicts
    await page.goto(`${projectBasePath}/sync-conflicts`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/sync-conflicts`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 4. Discipline Sub-reports
    await page.goto(`${projectBasePath}/sub-reports`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/sub-reports`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 5. Concrete Operations
    await page.goto(`${projectBasePath}/concrete-operations`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/concrete-operations`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 6. Weather
    await page.goto(`${projectBasePath}/weather`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/weather`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 7. Barriers
    await page.goto(`${projectBasePath}/barriers`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/barriers`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 8. Risk Register
    await page.goto(`${projectBasePath}/risk-register`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/risk-register`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 9. Quality & HSE
    await page.goto(`${projectBasePath}/quality-hse`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/quality-hse`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 10. Alerts
    await page.goto(`${projectBasePath}/alerts`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/alerts`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });
  });

  test("Simulate user flow across Commercial Domain pages and components", async ({ page }) => {
    const projectBasePath = await createProjectViaApi(page);

    // 1. Contracts List
    await page.goto(`${projectBasePath}/contracts`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/contracts`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 2. New Contract Form
    await page.goto(`${projectBasePath}/contracts/new`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/contracts/new`));
    await expect(page.locator("form, main").first()).toBeVisible({ timeout: 15_000 });

    // 3. Subcontractors
    await page.goto(`${projectBasePath}/subcontractors`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/subcontractors`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 4. Documents & Correspondence
    await page.goto(`${projectBasePath}/documents`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/documents`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 5. Decisions & Workflow
    await page.goto(`${projectBasePath}/decisions-workflow`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/decisions-workflow`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 6. Cash Flow
    await page.goto(`${projectBasePath}/cash-flow`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/cash-flow`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 7. Costs Control
    await page.goto(`${projectBasePath}/costs`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/costs`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 8. Material Balance
    await page.goto(`${projectBasePath}/material-balance`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/material-balance`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 9. Procurement Requisitions List
    await page.goto(`${projectBasePath}/procurement`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/procurement`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 10. Procurement New Requisition
    await page.goto(`${projectBasePath}/procurement/new`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/procurement/new`));
    await expect(page.locator("main, form").first()).toBeVisible({ timeout: 15_000 });

    // 11. Procurement Officer Dashboard
    await page.goto(`${projectBasePath}/procurement/officer`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/procurement/officer`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 12. Block Inventory
    await page.goto(`${projectBasePath}/procurement/inventory`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/procurement/inventory`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 13. Procurement Reports
    await page.goto(`${projectBasePath}/procurement/reports`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/procurement/reports`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 14. Procurement Blocks
    await page.goto(`${projectBasePath}/procurement/blocks`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/procurement/blocks`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 15. Stock Transfers
    await page.goto(`${projectBasePath}/procurement/transfers`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/procurement/transfers`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 16. Economic Analysis
    await page.goto(`${projectBasePath}/economic`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/economic`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });
  });

  test("Simulate user flow across Resources & Reporting Domain pages and components", async ({ page }) => {
    const projectBasePath = await createProjectViaApi(page);

    // 1. Equipment Utilization
    await page.goto(`${projectBasePath}/equipment-utilization`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/equipment-utilization`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 2. Equipment Log
    await page.goto(`${projectBasePath}/equipment-log`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/equipment-log`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 3. Labor Productivity
    await page.goto(`${projectBasePath}/labor-productivity`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/labor-productivity`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 4. Personnel Summary
    await page.goto(`${projectBasePath}/personnel-summary`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/personnel-summary`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 5. Manpower
    await page.goto(`${projectBasePath}/manpower`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/manpower`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 6. Labor Camp
    await page.goto(`${projectBasePath}/labor-camp`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/labor-camp`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 7. Overtime Requests
    await page.goto(`${projectBasePath}/overtime-requests`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/overtime-requests`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 8. Leave Requests
    await page.goto(`${projectBasePath}/leave-requests`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/leave-requests`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 9. Resource Allocations
    await page.goto(`${projectBasePath}/resource-allocations`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/resource-allocations`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 10. Role Dashboard
    await page.goto(`${projectBasePath}/dashboard`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/dashboard`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });

    // 11. Standard Reports
    await page.goto(`${projectBasePath}/standard-reports`);
    await expect(page).toHaveURL(new RegExp(`${projectBasePath}/standard-reports`));
    await expect(page.locator("main").first()).toBeVisible({ timeout: 15_000 });
  });
});
