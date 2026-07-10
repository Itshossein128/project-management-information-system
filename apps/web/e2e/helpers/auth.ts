import type { Page } from '@playwright/test';

export async function loginViaUI(page: Page, phone: string, pass: string) {
  await page.goto('/login');
  await page.fill('input[type="tel"]', phone);
  await page.fill('input[type="password"]', pass);
  await page.click('button[type="submit"]');
  await page.waitForURL('/home', { timeout: 10000 });
}
