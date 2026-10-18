/**
 * E2E TEST: Decision Tree User Flow — Authentication & Portfolio Suite
 * 
 * Based on decision-tree:
 * - docs/decision-tree/login
 * - docs/decision-tree/login/toggle-theme
 * - docs/decision-tree/login/change-language
 * - docs/decision-tree/login/toggle-password-visibility
 * - docs/decision-tree/login/submit-invalid-credentials
 * - docs/decision-tree/login/navigate-register
 * - docs/decision-tree/login/navigate-forgot-password
 * - docs/decision-tree/login/submit-valid-credentials
 * - docs/decision-tree/login/submit-valid-credentials/open-executive-dashboard
 * - docs/decision-tree/login/submit-valid-credentials/open-portfolio-liquidity
 * - docs/decision-tree/login/submit-valid-credentials/[navigate-hr-hub]
 * - docs/decision-tree/login/submit-valid-credentials/[navigate-org-refs]
 * - docs/decision-tree/login/submit-valid-credentials/[navigate-templates]
 * - docs/decision-tree/login/submit-valid-credentials/[navigate-roles]
 * - docs/decision-tree/login/submit-valid-credentials/logout
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";

test.describe("Decision Tree — Authentication & Portfolio Navigation Flows", () => {
  test.setTimeout(90_000);

  test("Login screen: toggle theme, switch language, toggle password visibility", async ({ page }) => {
    await page.goto("/login");
    await expect(page.locator("#login-phone")).toBeVisible({ timeout: 15_000 });

    // 1. Theme toggle
    const html = page.locator("html");
    const initialDark = await html.evaluate((el) => el.classList.contains("dark"));
    const themeBtn = page.locator("#button-themeToggle");
    await expect(themeBtn).toBeVisible();
    await themeBtn.click();
    if (initialDark) {
      await expect(html).not.toHaveClass(/dark/);
    } else {
      await expect(html).toHaveClass(/dark/);
    }

    // 2. Language switcher (English vs Persian)
    const enBtn = page.locator("#button-language-en");
    const faBtn = page.locator("#button-language-fa");
    await expect(enBtn).toBeVisible();
    await expect(faBtn).toBeVisible();

    await enBtn.click();
    await expect(html).toHaveAttribute("dir", "ltr");
    await expect(html).toHaveAttribute("lang", "en");

    await faBtn.click();
    await expect(html).toHaveAttribute("dir", "rtl");
    await expect(html).toHaveAttribute("lang", "fa");

    // 3. Password visibility toggle
    const pwdInput = page.locator("#login-password");
    await expect(pwdInput).toHaveAttribute("type", "password");
    const toggleEye = page.locator('button[type="button"]:has(svg)').filter({
      hasNot: page.locator("#button-themeToggle"),
    }).last();
    if (await toggleEye.isVisible()) {
      await toggleEye.click();
      await expect(pwdInput).toHaveAttribute("type", "text");
      await toggleEye.click();
      await expect(pwdInput).toHaveAttribute("type", "password");
    }
  });

  test("Login screen: submit invalid credentials displays error feedback", async ({ page }) => {
    await page.goto("/login");
    await page.locator("#login-phone").fill("+19999999999");
    await page.locator("#login-password").fill("wrongpassword");
    await page.locator('button[type="submit"]').click();

    // Verify user stays on login and error notification/alert appears
    await expect(page).toHaveURL(/\/login/);
    await expect(page.locator(".text-destructive, [role='alert'], .text-red-500").first()).toBeVisible({
      timeout: 10_000,
    });
  });

  test("Login screen: navigate to Register and return back to Login", async ({ page }) => {
    await page.goto("/login");
    const registerBtn = page.getByRole("button", { name: /ثبت‌?نام|register/i });
    await expect(registerBtn).toBeVisible();
    await registerBtn.click();

    await expect(page).toHaveURL(/\/register/);
    await expect(page.locator("input#register-phone, input[name='phone_number'], input[type='tel']").first()).toBeVisible({
      timeout: 10_000,
    });

    const backToLogin = page.locator("a[href='/login']");
    await backToLogin.click();
    await expect(page).toHaveURL(/\/login/);
  });

  test("Login screen: navigate to Forgot Password and return back to Login", async ({ page }) => {
    await page.goto("/login");
    const forgotBtn = page.getByRole("button", { name: /فراموش|forgot/i });
    await expect(forgotBtn).toBeVisible();
    await forgotBtn.click();

    await expect(page).toHaveURL(/\/forgot-password/);
    await expect(page.locator("input[type='tel'], input[name='phone_number']").first()).toBeVisible({
      timeout: 10_000,
    });

    const backToLogin = page.getByRole("button", { name: /ورود|بازگشت|login/i }).or(page.getByRole("link", { name: /ورود|بازگشت|login/i })).first();
    await backToLogin.click();
    await expect(page).toHaveURL(/\/login/);
  });

  test("Authenticated App Shell: navigate across all portfolio & admin destinations and logout", async ({
    page,
  }) => {
    await loginAs(page, E2E_USERS.admin);
    await page.goto("/projects");
    await expect(page.locator("#nav-mainSidebar")).toBeVisible({ timeout: 15_000 });

    // 1. Navigate to Executive Portfolio Dashboard
    const dashboardLink = page.locator("#button-sidebarNav-workspace-portfolio-dashboard");
    await expect(dashboardLink).toBeVisible();
    await dashboardLink.click();
    await expect(page).toHaveURL(/\/portfolio\/dashboard/);
    await expect(page.getByRole("heading", { name: /داشبورد مدیریتی|Executive Dashboard|پرتفولیو/i }).first()).toBeVisible({
      timeout: 15_000,
    });

    // If figures exist, test figure drill-down drawer
    const figureCard = page.locator("[data-testid='dashboard-figure-card']").first();
    if (await figureCard.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await figureCard.click();
      const drawer = page.locator("[role='dialog']");
      await expect(drawer).toBeVisible();
      const closeBtn = drawer.getByRole("button", { name: /بستن|close/i });
      if (await closeBtn.isVisible()) {
        await closeBtn.click();
        await expect(drawer).not.toBeVisible();
      }
    }

    // 2. Navigate to Portfolio Liquidity Workbench
    const liquidityLink = page.locator("#button-sidebarNav-workspace-portfolio-liquidity");
    await expect(liquidityLink).toBeVisible();
    await liquidityLink.click();
    await expect(page).toHaveURL(/\/portfolio\/liquidity/);
    await expect(page.getByRole("heading", { name: /نقدینگی|Liquidity/i }).first()).toBeVisible({
      timeout: 15_000,
    });

    // 3. Navigate to HR Hub & HR Users
    const hrLink = page.locator("#button-sidebarNav-workspace-hr");
    await expect(hrLink).toBeVisible();
    await hrLink.click();
    await expect(page).toHaveURL(/\/hr/);
    await expect(page.getByRole("heading", { name: /منابع انسانی|HR/i }).first()).toBeVisible({
      timeout: 15_000,
    });

    // In HR Hub, navigate to users
    const usersCardLink = page.locator("a[href='/hr/users'], a[href*='/users']").first();
    if (await usersCardLink.isVisible()) {
      await usersCardLink.click();
      await expect(page).toHaveURL(/\/hr\/users/);
      await expect(page.getByRole("heading", { name: /کاربران|Users/i }).first()).toBeVisible({
        timeout: 15_000,
      });
    }

    // 4. Navigate to Data Administration (Legacy Setup)
    const setupLink = page.locator("#button-sidebarNav-administration-projects-setup");
    if (await setupLink.isVisible()) {
      await setupLink.click();
      await expect(page).toHaveURL(/\/projects\/setup/);
    }

    // 5. Navigate to Organization References
    const orgRefsLink = page.locator("#button-sidebarNav-administration-settings-org-refs");
    await expect(orgRefsLink).toBeVisible();
    await orgRefsLink.click();
    await expect(page).toHaveURL(/\/settings\/org-refs/);
    await expect(page.locator("[data-testid='org-refs-page']").first()).toBeVisible({
      timeout: 15_000,
    });

    // 6. Navigate to Templates
    const templatesLink = page.locator("#button-sidebarNav-administration-settings-templates");
    await expect(templatesLink).toBeVisible();
    await templatesLink.click();
    await expect(page).toHaveURL(/\/settings\/templates/);
    await expect(page.getByRole("heading", { name: /الگوها|قالب‌ها|Templates/i }).first()).toBeVisible({
      timeout: 15_000,
    });

    // 7. Navigate to Roles
    const rolesLink = page.locator("#button-sidebarNav-administration-settings-roles");
    await expect(rolesLink).toBeVisible();
    await rolesLink.click();
    await expect(page).toHaveURL(/\/settings\/roles/);
    await expect(page.getByRole("heading", { name: /نقش‌ها|Roles/i }).first()).toBeVisible({
      timeout: 15_000,
    });

    // 8. Return to Projects List
    const projectsLink = page.locator("#button-sidebarNav-workspace-projects");
    await expect(projectsLink).toBeVisible();
    await projectsLink.click();
    await expect(page).toHaveURL(/\/projects\/?$/);

    // 9. Notifications Bell dropdown toggle
    const bellBtn = page.locator("#button-notificationsToggle, button:has(svg.lucide-bell)");
    if (await bellBtn.isVisible()) {
      await bellBtn.click();
      const notifPanel = page.locator("#container-notificationsPanel, [role='dialog'], [data-state='open']");
      await expect(notifPanel).toBeVisible({ timeout: 5_000 });
      // Close dropdown
      await page.keyboard.press("Escape");
    }

    // 10. Logout decision
    const signOutBtn = page.locator("#button-appHeaderSignOut");
    await expect(signOutBtn).toBeVisible();
    await signOutBtn.click();
    await expect(page).toHaveURL(/\/login/);

    // Verify session was cleared
    const storedToken = await page.evaluate(() => localStorage.getItem("auth_access_token"));
    expect(storedToken).toBeNull();
  });
});
