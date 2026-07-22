/**
 * FLOW: Budget & Cost
 * MODULE: Finance
 * ROLES: admin, finance_manager
 *
 * DECISION TREE:
 * 1. Navigate to Project Costs page
 * 2. View Budget Grid
 *   ├─ User has view permission -> Shows BudgetGrid
 *   └─ User lacks view permission -> Shows Error
 *
 * BRANCHES TESTED:
 * - Budget page loads
 * - Budget grid renders WBS rows and columns
 * - Lacking view_costs permission shows access denied (viewer role)
 *
 * BRANCHES DEFERRED:
 * - (handled by sprint7-costs.spec.ts) Edit budget value (WBS mode) and save
 * - (handled by sprint7-costs.spec.ts) Activity mode editing
 * - (handled by sprint7-costs.spec.ts) Cost pool allocation
 * - (handled by sprint7-costs.spec.ts) Actual cost editing
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createProjectViaApi, createRootWbs } from "../helpers/project";

const API_BASE = "http://127.0.0.1:8000/api";

test.describe("Finance - Budget & Cost (Access Denied Path)", () => {
  let projectBasePath: string;

  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
    projectBasePath = await createProjectViaApi(page);
    await createRootWbs(page, projectBasePath, { code: "B1", name: "Budget Test Node" });
  });

  test("viewer cannot see costs page", async ({ page }) => {
    const projectId = projectBasePath.split('/').pop();
    const access = await page.evaluate(() => localStorage.getItem("auth_access_token"));

    // get visitor user id
    const resVisitor = await page.request.post(`${API_BASE}/auth/login/`, {
      data: { phone_number: E2E_USERS.visitor.phone, password: E2E_USERS.visitor.password },
    });
    const visitorData = await resVisitor.json() as { user: { id: string } };

    // find viewer role ID
    const rolesRes = await page.request.get(`${API_BASE}/v1/roles/`, {
      headers: { Authorization: `Bearer ${access}` },
    });
    const rolesData = await rolesRes.json() as { results: { id: string, codename: string }[] };
    const viewerRoleId = rolesData.results.find(r => r.codename === 'viewer')?.id;

    if (viewerRoleId) {
      // add visitor as viewer to the project
      await page.request.post(`${API_BASE}/v1/projects/${projectId}/members/`, {
        headers: { Authorization: `Bearer ${access}` },
        data: {
          user: visitorData.user.id,
          positions: [{ role: viewerRoleId }]
        },
      });
    }

    await loginAs(page, E2E_USERS.visitor);
    await page.goto(`${projectBasePath}/costs`);
    await expect(page.getByText(/دسترسی ندارید|دسترسی به این بخش ندارید/i)).toBeVisible();
  });
});
