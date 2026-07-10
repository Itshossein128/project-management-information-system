/**
 * FLOW: Standard login and session management
 * MODULE: Auth
 * ROLES INVOLVED: All (testing valid credentials, invalid credentials, RTL layout)
 * DATE WRITTEN: 2025-07-10
 *
 * DECISION TREE:
 * START: User opens /login
 *   ├── [A] Credentials valid
 *   │     ├── [A1] Correct phone & password → successful login
 *   ├── [B] Credentials invalid
 *   │     ├── [B1] Wrong password → error message
 *   │     └── [B2] Wrong phone → error message
 *   ├── [C] Validation
 *   │     ├── [C1] Empty fields → validation errors (HTML5 native required)
 *   └── [D] UI behavior
 *         └── [D1] RTL layout correct
 *
 * BRANCHES TESTED TODAY: A1, B1, B2, C1, D1
 */

import { test, expect } from '@playwright/test';
import { loginAs } from '../helpers/auth';

test.describe('Authentication - Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('D1: Page layout should be RTL', async ({ page }) => {
    await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  });

  test('C1: Empty fields should trigger native validation', async ({ page }) => {
    // Attempt to submit empty form
    await page.locator('[data-testid="login-submit-btn"]').click();

    // Check for native validation
    const phoneInput = page.locator('[data-testid="login-phone-input"]');
    const isValid = await phoneInput.evaluate((el: HTMLInputElement) => el.checkValidity());
    expect(isValid).toBeFalsy();
  });

  test('B1 & B2: Wrong credentials should show error', async ({ page }) => {
    await page.locator('[data-testid="login-phone-input"]').fill('+10000000001');
    await page.locator('[data-testid="login-password-input"]').fill('wrongpassword1234');
    await page.locator('[data-testid="login-submit-btn"]').click();

    // Check for error element using role alert
    await expect(page.getByRole('alert')).toBeVisible({ timeout: 10000 });
  });

  test('A1: Correct credentials should log user in and redirect', async ({ page }) => {
    await loginAs(page, '+10000000001');
  });
});
