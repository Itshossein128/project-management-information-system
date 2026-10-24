import { expect, type Page } from "@playwright/test";

// Exercise the real shell and router with deterministic API responses. These
// tests verify navigation behavior, not backend authorization or project data.
export async function session(page: Page, roles = ["admin"], language = "en") {
  const user = { id: "navigation-user", full_name: "Navigation tester", roles };
  await page.context().addCookies([
    { name: "auth_token", value: "navigation-test", url: "http://localhost:5173" },
  ]);
  await page.addInitScript(({ user, language }) => {
    localStorage.setItem("auth_access_token", "navigation-test");
    localStorage.setItem("auth_refresh_token", "navigation-test");
    localStorage.setItem("auth_user", JSON.stringify(user));
    localStorage.setItem("app-language", language);
    localStorage.setItem("i18nextLng", language);
    // Returning-user fixture: keep first-run onboarding overlays separate
    // from the controls exercised by this navigation reachability suite.
    for (const tour of ["project-manpower", "project-alerts", "procurement-new", "procurement-list", "procurement-officer", "procurement-reports", "procurement-inventory", "procurement-transfers", "procurement-blocks", "procurement-detail", "project-costs", "project-contracts"]) {
      localStorage.setItem(`tour_seen_${tour}`, "true");
    }
  }, { user, language });
  await page.route(/^https?:\/\/[^/]+\/api\//, async (route) => {
    const path = new URL(route.request().url()).pathname;
    const json = path.endsWith("/auth/profile/") ? user
      : path.endsWith("/capabilities/") ? [
        { capability_key: "risk", enabled: false, mode: "disabled" },
        { capability_key: "hr", enabled: false, mode: "disabled" },
      ]
      : path.endsWith("/portfolio/dashboard/") ? { projects: [] }
      : path.endsWith("/portfolio/summary/") ? { totals: { project_count: 0 }, totals_by_currency: {} }
      : path.endsWith("/members/") || path.endsWith("/roles/") || path.endsWith("/project-templates/") ? []
      : { results: [], count: 0 };
    await route.fulfill({ json });
  });
}

export async function visit(page: Page, path: string, language = "en") {
  await page.goto(path);
  await page.locator(`#button-language-${language}`).click();
  await expect(page.locator("html")).toHaveAttribute("dir", language === "fa" ? "rtl" : "ltr");
}

