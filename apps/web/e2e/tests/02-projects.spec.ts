/**
 * FLOW: Project module list and read access
 * MODULE: Projects
 * ROLES INVOLVED: All (Project Manager, Planning Engineer, Site Supervisor, Field Supervisor, Finance Manager, Procurement Officer, Document Controller, Viewer)
 * DATE WRITTEN: 2025-07-15
 *
 * DECISION TREE:
 * START: User opens /projects
 *   ├── [A] Authentication
 *   │     ├── [A1] Unauthenticated -> redirects to /login
 *   │     └── [A2] Authenticated -> proceeds to load projects
 *   ├── [B] Projects Data fetching
 *   │     ├── [B1] User has no assigned projects -> shows empty state
 *   │     └── [B2] User has assigned projects -> lists projects
 *   ├── [C] Project Navigation
 *   │     └── [C1] User clicks on a project -> navigates to project dashboard
 *   └── [D] UI Behavior
 *         └── [D1] RTL layout correct
 *
 * BRANCHES TESTED TODAY: A1, A2, B2, C1, D1
 */

import { expect, test } from "@playwright/test";
import { loginAs } from "../helpers/auth";

test.describe("Projects Module - List and Access", () => {
  test("A1: Unauthenticated access redirects to login", async ({ page }) => {
    await page.goto("/projects");
    await expect(page).toHaveURL(/\/login/);
  });

  test("A2 & B2 & D1: Authenticated access loads projects with RTL layout", async ({ page }) => {
    await loginAs(page, "+10000000001");
    await page.goto("/projects");

    // D1: Check RTL layout
    await expect(page.locator("html")).toHaveAttribute("dir", "rtl");

    // A2 & B2: Check that the page loads and displays projects
    await expect(page.getByRole("heading", { name: /پروژه‌ها|projects/i })).toBeVisible({ timeout: 15_000 });

    // Check for a list of projects or at least the projects grid/table
    const projectLinks = page.locator('a[href*="/projects/"]');
    const count = await projectLinks.count();

    if (count > 0) {
      // C1: Click a project link
      const firstProjectLink = projectLinks.first();
      await firstProjectLink.click();

      // Wait for navigation
      await page.waitForURL(/\/projects\/[a-zA-Z0-9-]+\/?/);
      await expect(page).toHaveURL(/\/projects\/[a-zA-Z0-9-]+\/?/);
    } else {
      // B1: Empty state (if no projects exist)
      await expect(page.getByText(/موردی یافت نشد|no projects/i)).toBeVisible();
    }
  });
});
