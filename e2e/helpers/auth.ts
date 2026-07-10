import { Page } from '@playwright/test';

export async function loginAs(page: Page, phoneNumber: string) {
  await page.goto('/login');
  await page.locator('[data-testid="login-phone-input"]').fill(phoneNumber);
  await page.locator('[data-testid="login-password-input"]').fill('devpass123');

  await page.locator('[data-testid="login-submit-btn"]').click();
  await page.waitForURL(/.*\/home/, { timeout: 15000 });
}
