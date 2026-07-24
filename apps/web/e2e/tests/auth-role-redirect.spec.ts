/**
 * FLOW: Role-based redirect after login
 * MODULE: Access Control
 * ROLES: All 8 roles
 *
 * BRANCHES TESTED:
 * - project_manager, planning_engineer, site_supervisor, field_supervisor
 * - finance_manager, procurement_officer, document_controller, viewer
 */

import { expect, test } from "@playwright/test";

const E2E_ROLES = {
  project_manager: { phone: "+10000000010", password: "devpass123" },
  planning_engineer: { phone: "+10000000011", password: "devpass123" },
  site_supervisor: { phone: "+10000000012", password: "devpass123" },
  field_supervisor: { phone: "+10000000013", password: "devpass123" },
  finance_manager: { phone: "+10000000014", password: "devpass123" },
  procurement_officer: { phone: "+10000000015", password: "devpass123" },
  document_controller: { phone: "+10000000016", password: "devpass123" },
  viewer: { phone: "+10000000017", password: "devpass123" },
} as const;

test.describe("Auth — role-based redirects", () => {
  for (const [roleName, user] of Object.entries(E2E_ROLES)) {
    test(`${roleName} can access the system`, async ({ page }) => {
      await page.goto("/login");
      await expect(page.locator("html")).toHaveAttribute("dir", "rtl");

      await page.locator("#login-phone").fill(user.phone);
      await page.locator("#login-password").fill(user.password);
      await Promise.all([
        page.waitForURL(/\/projects\/?$/, { timeout: 15_000 }),
        page.locator('button[type="submit"]').click(),
      ]);

      await expect(page.getByRole("heading", { name: /پروژه|Projects/i }).first()).toBeVisible({
        timeout: 15_000,
      });

      const projectCard = page.getByText("E2E Roles Test").first();
      await expect(projectCard).toBeVisible({ timeout: 15_000 });
      await projectCard.click();

      await expect(page).toHaveURL(/\/projects\/[0-9a-f-]+\/overview/);
    });
  }
});
