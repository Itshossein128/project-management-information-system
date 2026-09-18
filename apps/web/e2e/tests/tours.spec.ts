/**
 * Driver.js product tours: auto-start gating, step navigation, translated copy,
 * and the procurement/alerts steps that explain fast-track requisitions.
 */
import { expect, test, type Page } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";
import { createProjectViaApi } from "../helpers/project";
import {
  goToNextStep,
  goToPreviousStep,
  markToursSeen,
  readCurrentStep,
  readSeenFlag,
  startTourFromButton,
  tourPopover,
  walkTourToEnd,
} from "../helpers/tour";

/** Every tour reachable on a project with no seeded domain data. */
const TOURS = [
  { id: "procurement-list", path: "procurement" },
  { id: "procurement-new", path: "procurement/new" },
  { id: "procurement-blocks", path: "procurement/blocks" },
  { id: "procurement-inventory", path: "procurement/inventory" },
  { id: "procurement-transfers", path: "procurement/transfers" },
  { id: "procurement-officer", path: "procurement/officer" },
  { id: "procurement-reports", path: "procurement/reports" },
  { id: "project-alerts", path: "alerts" },
  { id: "project-manpower", path: "manpower" },
] as const;

/** An untranslated step renders the raw i18n key instead of a sentence. */
const RAW_I18N_KEY = /^tour\.[A-Za-z]/;

test.describe("Product tours", () => {
  test.setTimeout(120_000);

  let projectBase: string;
  let session: { access: string; refresh: string; user: string };

  // Log in once for the whole file: /auth/login/ is rate limited, and one call
  // per test is enough to trip it.
  test.beforeAll(async ({ browser }) => {
    const page = await browser.newPage();
    await loginAs(page, E2E_USERS.admin);
    session = await page.evaluate(() => ({
      access: localStorage.getItem("auth_access_token")!,
      refresh: localStorage.getItem("auth_refresh_token")!,
      user: localStorage.getItem("auth_user")!,
    }));
    projectBase = await createProjectViaApi(page);
    await page.close();
  });

  test.beforeEach(async ({ page }) => {
    await page.addInitScript((s: typeof session) => {
      localStorage.setItem("auth_access_token", s.access);
      localStorage.setItem("auth_refresh_token", s.refresh);
      localStorage.setItem("auth_user", s.user);
      document.cookie = `auth_token=${encodeURIComponent(s.access)}; path=/; max-age=${7 * 24 * 60 * 60}; SameSite=Lax`;
    }, session);
  });

  async function openTour(page: Page, tour: (typeof TOURS)[number]) {
    await markToursSeen(page, tour.id);
    await page.goto(`${projectBase}/${tour.path}`);
    await startTourFromButton(page);
  }

  for (const tour of TOURS) {
    test(`${tour.id} tour plays through every step with translated copy`, async ({ page }) => {
      await openTour(page, tour);
      const steps = await walkTourToEnd(page);

      expect(steps.length).toBeGreaterThan(0);
      expect(steps.map((s) => s.index)).toEqual(
        steps.map((_, i) => i + 1),
      );

      for (const step of steps) {
        expect(step.title, `step ${step.index} title`).not.toBe("");
        expect(step.description, `step ${step.index} description`).not.toBe("");
        // A missing fa.json/en.json entry surfaces as the literal key.
        expect(step.title, `step ${step.index} title is untranslated`).not.toMatch(RAW_I18N_KEY);
        expect(step.description, `step ${step.index} description is untranslated`).not.toMatch(
          RAW_I18N_KEY,
        );
        // useProductTour drops steps whose element is missing, so every step
        // that does render must be anchored to a real data-tour element.
        expect(step.target, `step ${step.index} highlighted no data-tour element`).not.toBeNull();
      }

      // Distinct steps should not repeat the same anchor or the same wording.
      const targets = steps.map((s) => s.target);
      expect(new Set(targets).size, `duplicate anchors: ${targets.join(", ")}`).toBe(targets.length);
      const titles = steps.map((s) => s.title);
      expect(new Set(titles).size, `duplicate titles: ${titles.join(", ")}`).toBe(titles.length);
    });
  }

  test("a tour auto-starts on the first visit and never again after it is dismissed", async ({
    page,
  }) => {
    // Each test gets a fresh context, so no tour has been marked seen yet.
    await page.goto(`${projectBase}/procurement`);

    // useProductTour polls for its first target for up to ~6s before giving up.
    await expect(tourPopover(page)).toBeVisible({ timeout: 15_000 });
    await expect.poll(() => readSeenFlag(page, "procurement-list")).toBe("true");

    await page.locator(".driver-popover-close-btn").click();
    await expect(tourPopover(page)).toHaveCount(0);

    // Same page again: the flag is now set, so nothing should pop up.
    await page.goto(`${projectBase}/procurement`);
    await expect(page.getByTestId("product-tour-button")).toBeVisible();
    await page.waitForTimeout(7_000);
    await expect(tourPopover(page)).toHaveCount(0);
  });

  test("dismissing a tour immediately still stops it replaying later", async ({ page }) => {
    // Closing during driver's entry animation used to lose the seen flag,
    // because driver skips onDestroyed until the animation commits its step.
    await page.goto(`${projectBase}/procurement/blocks`);
    await expect(tourPopover(page)).toBeVisible({ timeout: 15_000 });
    await page.locator(".driver-popover-close-btn").click();
    await expect(tourPopover(page)).toHaveCount(0);
    await expect.poll(() => readSeenFlag(page, "procurement-blocks")).toBe("true");

    await page.goto(`${projectBase}/procurement/blocks`);
    await expect(page.getByTestId("product-tour-button")).toBeVisible();
    await page.waitForTimeout(7_000);
    await expect(tourPopover(page)).toHaveCount(0);
  });

  test("the help button replays a tour that was already dismissed", async ({ page }) => {
    await markToursSeen(page, "procurement-new");
    await page.goto(`${projectBase}/procurement/new`);
    await expect(page.getByTestId("product-tour-button")).toBeVisible();
    await expect(tourPopover(page)).toHaveCount(0);

    await startTourFromButton(page);
    await expect(tourPopover(page)).toBeVisible();
  });

  test("next and previous move between steps without losing content", async ({ page }) => {
    await openTour(page, { id: "procurement-new", path: "procurement/new" });

    const first = await readCurrentStep(page);
    expect(first.index).toBe(1);
    expect(first.total).toBeGreaterThan(1);

    await goToNextStep(page, 2, first.total);
    const second = await readCurrentStep(page);
    expect(second.title).not.toBe(first.title);
    expect(second.target).not.toBe(first.target);

    await goToPreviousStep(page, 1, first.total);
    const backAgain = await readCurrentStep(page);
    expect(backAgain.title).toBe(first.title);
    expect(backAgain.target).toBe(first.target);
  });

  test("steps whose anchor is not rendered are skipped instead of showing an empty popover", async ({
    page,
  }) => {
    // This project has no requisitions, so the row-actions step has no anchor.
    await openTour(page, { id: "procurement-list", path: "procurement" });
    const steps = await walkTourToEnd(page);
    const targets = steps.map((s) => s.target);

    expect(targets).toContain("list-filters");
    expect(targets).not.toContain("requisition-row-actions");
  });

  test("the requisitions tour points at the bell where fast-track alerts arrive", async ({
    page,
  }) => {
    await openTour(page, { id: "procurement-list", path: "procurement" });
    const steps = await walkTourToEnd(page);

    const bellStep = steps.find((s) => s.target === "notification-bell");
    expect(bellStep, "procurement list tour never highlights the notification bell").toBeDefined();
    expect(bellStep!.description).toMatch(/فورس‌ماژور|fast-track/i);
  });

  test("the alert centre tour opens the rules tab while it explains the rules", async ({ page }) => {
    await openTour(page, { id: "project-alerts", path: "alerts" });

    // The rules table is only mounted once the tour switches tabs for us.
    await expect(page.getByRole("button", { name: /افزودن قانون هشدار/ })).toHaveCount(0);

    const steps = await walkTourToEnd(page);
    const targets = steps.map((s) => s.target);
    expect(targets).toContain("alerts-rules-tab");
    expect(targets).toContain("notification-bell");

    await expect(page.getByRole("button", { name: /افزودن قانون هشدار/ })).toBeVisible();
  });

  test("each tour records its own seen flag independently", async ({ page }) => {
    await markToursSeen(page, "procurement-blocks");
    await page.goto(`${projectBase}/procurement/blocks`);
    await startTourFromButton(page);
    await walkTourToEnd(page);

    await expect.poll(() => readSeenFlag(page, "procurement-blocks")).toBe("true");
    expect(await readSeenFlag(page, "procurement-transfers")).toBeNull();
  });
});
