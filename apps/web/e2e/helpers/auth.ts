import type { Page } from "@playwright/test";
import { expect } from "@playwright/test";

const API_BASE = "http://127.0.0.1:8000/api";

export const E2E_USERS = {
  admin: { phone: "+10000000001", password: "devpass123" },
  visitor: { phone: "+10000000003", password: "devpass123" },
} as const;

const cachedTokens = new Map<
  string,
  {
    access: string;
    refresh: string;
    user: { id: number; mobile: string; full_name: string };
  }
>();

export async function loginAs(
  page: Page,
  user: (typeof E2E_USERS)[keyof typeof E2E_USERS] = E2E_USERS.admin,
) {
  let data = cachedTokens.get(user.phone);
  if (!data) {
    let res;
    for (let attempt = 0; attempt < 5; attempt++) {
      try {
        res = await page.request.post(`${API_BASE}/auth/login/`, {
          data: { phone_number: user.phone, password: user.password },
        });
        if (res.ok()) break;
      } catch (e) {
        if (attempt === 4) throw e;
        await new Promise((r) => setTimeout(r, 1000));
      }
    }
    if (!res || !res.ok()) {
      throw new Error(`loginAs failed: ${res?.status()} ${await res?.text()}`);
    }
    data = (await res.json()) as {
      access: string;
      refresh: string;
      user: { id: number; mobile: string; full_name: string };
    };
    cachedTokens.set(user.phone, data);
  }
  await page.goto("/login");
  await page.evaluate(
    ({ access, refresh, user }) => {
      localStorage.setItem("auth_access_token", access);
      localStorage.setItem("auth_refresh_token", refresh);
      localStorage.setItem("auth_user", JSON.stringify(user));
      document.cookie = `auth_token=${encodeURIComponent(access)}; path=/; max-age=${7 * 24 * 60 * 60}; SameSite=Lax`;
    },
    { access: data.access, refresh: data.refresh, user: data.user },
  );
}

export async function loginViaUI(
  page: Page,
  user: (typeof E2E_USERS)[keyof typeof E2E_USERS] = E2E_USERS.admin,
) {
  await page.goto("/login", { waitUntil: "networkidle" });
  await expect(page.locator('button[type="submit"]')).toBeEnabled();
  await page.locator("#login-phone").fill(user.phone);
  await page.locator("#login-password").fill(user.password);
  await Promise.all([
    page.waitForURL(/\/projects\/?$/, { timeout: 15_000 }),
    page.locator('button[type="submit"]').click(),
  ]);
}
