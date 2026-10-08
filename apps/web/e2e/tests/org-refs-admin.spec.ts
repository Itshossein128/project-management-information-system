/**
 * FLOW: Spec 02 org-refs admin + wizard ManagedContractType catalog
 * MODULE: Central data / master data
 * ROLES: admin
 */

import { expect, test } from "@playwright/test";
import { E2E_USERS, loginAs } from "../helpers/auth";

test.describe("Org refs admin — Spec 02", () => {
  test.setTimeout(120_000);

  test.beforeEach(async ({ page }) => {
    await loginAs(page, E2E_USERS.admin);
  });

  test("settings org-refs page can create OrganizationUnit and ManagedContractType", async ({
    page,
  }) => {
    const suffix = `${Date.now()}`;
    const unitCode = `OU${suffix.slice(-6)}`;
    const typeCode = `CT${suffix.slice(-6)}`;

    await page.goto("/settings/org-refs");
    await expect(page.getByTestId("org-refs-page")).toBeVisible({ timeout: 15_000 });

    await page.getByTestId("org-unit-code").fill(unitCode);
    await page.getByTestId("org-unit-name").fill(`Unit ${unitCode}`);
    await page.getByTestId("org-unit-create-btn").click();
    await expect(page.getByTestId("org-unit-list")).toContainText(unitCode, {
      timeout: 10_000,
    });

    await page.getByTestId("contract-type-code").fill(typeCode);
    await page.getByTestId("contract-type-name-fa").fill(`نوع ${typeCode}`);
    await page.getByTestId("contract-type-name-en").fill(`Type ${typeCode}`);
    await page.getByTestId("contract-type-create-btn").click();
    await expect(page.getByTestId("contract-type-list")).toContainText(typeCode, {
      timeout: 10_000,
    });

    await page.goto("/projects/new");
    await expect(page.getByTestId("wizard-contract-type")).toBeVisible({ timeout: 15_000 });
    await expect(
      page.getByTestId("wizard-contract-type").locator(`option[value="${typeCode}"]`),
    ).toHaveCount(1, { timeout: 15_000 });
  });
});

