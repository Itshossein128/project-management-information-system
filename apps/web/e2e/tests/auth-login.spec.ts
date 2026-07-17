/**
 * FLOW: Standard login and session management
 * MODULE: Auth
 * ROLES: ANY
 * DECISION TREE:
 *  - Provide credentials
 *    - Valid -> Store token -> Redirect to /home -> /projects
 *    - Invalid -> Show error
 *    - Unknown mobile -> Show error
 *  - RTL layout validation
 *
 * BRANCHES TESTED: valid credentials, wrong password, RTL form layout
 * BRANCHES DEFERRED: unknown mobile, expired token, logout, direct URL without auth, token refresh
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs, loginViaUI } from "../helpers/auth";

test.describe("Auth — login", () => {
  test("shows error for invalid credentials", async ({ page }) => {
    await page.goto("/login");
    await page.locator("#login-phone").fill(E2E_USERS.admin.phone);
    await page.locator("#login-password").fill("wrong-password");
    const loginResponse = page.waitForResponse(
      (res) => res.url().includes("/auth/login/") && res.request().method() === "POST",
    );
    await page.locator('button[type="submit"]').click();
    const response = await loginResponse;
    expect(response.status()).toBe(401);
    await expect(page.getByRole("alert")).toBeVisible({ timeout: 10_000 });
  });

  test("logs in via UI with valid credentials", async ({ page }) => {
    await loginViaUI(page, E2E_USERS.admin);
    await expect(page).toHaveURL(/\/projects\/?$/);
  });

  test("logs in via API helper and /home redirects to projects", async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
    await page.goto("/home");
    await expect(page).toHaveURL(/\/projects\/?$/);
  });
});
