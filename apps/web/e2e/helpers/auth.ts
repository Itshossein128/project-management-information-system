import { Page } from '@playwright/test';

export const E2E_USERS = {
  admin: { phone: '+10000000001', password: 'devpass123' },
  project_manager: { phone: '+10000000002', password: 'devpass123' },
};

export async function loginViaUI(page: Page, user: any) {
  await page.goto('/login');
  await page.locator('#login-phone').fill(user.phone);
  await page.locator('#login-password').fill(user.password || 'devpass123');
  await page.locator('button[type="submit"]').click();
}

export async function loginAs(page: Page, user: any) {
  const phone = typeof user === 'string' ? user : user.phone;
  await page.goto('/login');
  // Support both old ID-based selectors and new data-testids
  const phoneInput = page.locator('[data-testid="login-phone-input"], #login-phone').first();
  const passwordInput = page.locator('[data-testid="login-password-input"], #login-password').first();
  const submitBtn = page.locator('[data-testid="login-submit-btn"], button[type="submit"]').first();

  await phoneInput.fill(phone);
  await passwordInput.fill('devpass123');
  await submitBtn.click();
  // Wait for redirect to home or projects
  await page.waitForURL(/.*\/(home|projects)/, { timeout: 15000 }).catch(() => {});
}
