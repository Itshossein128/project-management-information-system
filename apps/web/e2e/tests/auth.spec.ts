/**
 * FLOW: Authentication
 * MODULE: Access Control
 * ROLES: N/A (Unauthenticated user)
 *
 * DECISION TREE:
 * 1. Navigate to login page
 * 2. Enter credentials
 *   ├─ Valid credentials -> Navigate to home
 *   └─ Invalid credentials -> Show error message
 *
 * BRANCHES TESTED:
 * - Invalid credentials -> Show error message
 * - Empty credentials -> HTML validation error (or submit blocked)
 * - Valid credentials -> Navigates to home
 * BRANCHES DEFERRED:
 * - Forgot password
 * - Token refresh
 */

import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {

  test('user sees error with invalid credentials', async ({ page }) => {
    // 1. Navigate to login
    await page.goto('/login');

    // RTL check
    await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');

    // 2. Fill credentials
    await page.fill('input[type="tel"]', '09123456789');
    await page.fill('input[type="password"]', 'wrong-password-123');

    // 3. Submit
    await page.click('button[type="submit"]');

    // 4. Verify error shown in alert role
    const errorAlert = page.locator('[data-testid="login-error"]');
    await expect(errorAlert).toBeVisible();
  });

  test('submit button is functional with empty credentials', async ({ page }) => {
     await page.goto('/login');
     await page.click('button[type="submit"]');

     // Browser validation prevents submission if required attributes are present
     // We just check that we are still on the login page
     await expect(page).toHaveURL(/.*\/login.*/);
  });

  test('user logs in successfully with valid credentials', async ({ page }) => {
    await page.goto('/login');

    // These credentials must match a user in the database.
    await page.fill('input[type="tel"]', '+10000000001');
    await page.fill('input[type="password"]', 'devpass123');

    await page.click('button[type="submit"]');

    // 4. Verify successful navigation
    await page.waitForURL('**/home*', { timeout: 10000 });
    await expect(page).toHaveURL(/.*\/home.*/);
  });
});
