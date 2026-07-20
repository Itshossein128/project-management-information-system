/**
 * FLOW: Role-based redirect after login
 * MODULE: Access Control
 * ROLES: All 8 roles
 *
 * DECISION TREE:
 * 1. Log in as a user with a specific role.
 * 2. Assert they can view what they are supposed to view.
 *
 * BRANCHES TESTED:
 * - project_manager lands correctly
 * - planning_engineer lands correctly
 * - site_supervisor lands correctly
 * - field_supervisor lands correctly
 * - finance_manager lands correctly
 * - procurement_officer lands correctly
 * - document_controller lands correctly
 * - viewer lands correctly
 */

import { expect, test } from "@playwright/test";
import { loginAs } from "../helpers/auth";

const E2E_ROLES = {
  project_manager: { phone: "+10000000010", password: "devpass123" },
  planning_engineer: { phone: "+10000000011", password: "devpass123" },
  site_supervisor: { phone: "+10000000012", password: "devpass123" },
  field_supervisor: { phone: "+10000000013", password: "devpass123" },
  finance_manager: { phone: "+10000000014", password: "devpass123" },
  procurement_officer: { phone: "+10000000015", password: "devpass123" },
  document_controller: { phone: "+10000000016", password: "devpass123" },
  viewer: { phone: "+10000000017", password: "devpass123" },
};

test.describe("Auth — role-based redirects", () => {
  for (const [roleName, user] of Object.entries(E2E_ROLES)) {
    test(`${roleName} can access the system`, async ({ page }) => {
      // 1. Go to login page
      await page.goto("/login");
      await expect(page.locator("html")).toHaveAttribute("dir", "rtl");

      // 2. Login via UI
      await page.fill('input[type="tel"]', user.phone);
      await page.fill('input[type="password"]', user.password);
      await page.click('button[type="submit"]');

      // 3. Verify successful navigation (/home redirects to /projects)
      await page.waitForURL('**/projects*', { timeout: 15_000 });
      await expect(page).toHaveURL(/\/projects\/?$/);

      // Basic check: everyone should see the project list
      await expect(page.getByRole("heading", { name: /پروژه|Projects/i }).first()).toBeVisible({
        timeout: 15_000,
      });

      // Navigate to the specific project created in seed_e2e
      const projectCard = page.locator('text=E2E Roles Test').first();
      await expect(projectCard).toBeVisible({ timeout: 15_000 });
      await projectCard.click();

      // Ensure we hit the overview page inside the project
      await expect(page).toHaveURL(/\/projects\/[0-9a-f-]+\/overview/);
    });
  }
});
