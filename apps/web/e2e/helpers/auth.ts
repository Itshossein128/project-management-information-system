import { Page, expect } from '@playwright/test';

export async function loginAs(page: Page, phone: string, pass: string) {
  await page.goto('/login');
  await page.fill('input[type="tel"]', phone);
  await page.fill('input[type="password"]', pass);
  await page.click('button[type="submit"]');
  // Wait for login to complete and navigate
  await page.waitForURL('/home', { timeout: 10000 });
}

export async function loginViaUI(page: Page, phone: string, pass: string) {
  await loginAs(page, phone, pass);
}
