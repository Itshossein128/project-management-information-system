/**
 * FLOW: Spec 027 — contractor from ذینفعان + department ContractorSelect
 * MODULE: Stakeholders / department activity filter
 * ROLES: admin (mocked shell)
 */

import { expect, test, type Page } from "@playwright/test";
import { session, visit } from "../helpers/navigation";

const projectId = "11111111-1111-4111-8111-111111111111";
const base = `/api/v1/projects/${projectId}`;
const contractorId = "22222222-2222-4222-8222-222222222222";

const project = {
  project_id: projectId,
  id: projectId,
  project_name: "Contractor select project",
  name: "Contractor select project",
  project_code: "CSEL",
  slug: "csel",
  status: "active",
  currency: "IRR",
  start_date: null,
  planned_finish_date: null,
  contract_amount: null,
};

const permissions = Object.fromEntries(
  ["view_project", "edit_project", "view_reports", "edit_reports", "view_dashboard"].map(
    (key) => [key, true],
  ),
);

const contractorRow = {
  id: contractorId,
  name: "Acme Contractor",
  organization_name: "Acme Org",
  role: "contractor",
  email: null,
  phone: null,
  influence: null,
  interest: null,
  communication_need: "",
  relationship_owner: null,
  status: "active",
  contacts_redacted: false,
};

async function mockProjectShell(page: Page, opts?: { contractors?: typeof contractorRow[] }) {
  const contractors = opts?.contractors ?? [];
  await page.route(/^https?:\/\/[^/]+\/api\/v1\//, async (route) => {
    const path = new URL(route.request().url()).pathname;
    const list = (results: unknown[]) => ({
      results,
      count: results.length,
      next: null,
      previous: null,
    });

    if (path.endsWith("/permissions/")) {
      return route.fulfill({ json: { effective: permissions, permissions: [] } });
    }
    if (path === "/api/v1/projects/") {
      return route.fulfill({ json: list([project]) });
    }
    if (path === `${base}/`) {
      return route.fulfill({ json: project });
    }
    if (path === `${base}/stakeholders/` || path.startsWith(`${base}/stakeholders?`)) {
      const url = new URL(route.request().url());
      const role = url.searchParams.get("role");
      const status = url.searchParams.get("status");
      let rows = contractors;
      if (role === "contractor") {
        rows = rows.filter((r) => r.role === "contractor");
      }
      if (status === "active") {
        rows = rows.filter((r) => r.status === "active");
      }
      return route.fulfill({ json: { results: rows } });
    }
    if (path === `${base}/stakeholders/matrix/`) {
      return route.fulfill({ json: { cells: [] } });
    }
    if (path === `${base}/communication-plans/`) {
      return route.fulfill({ json: { results: [] } });
    }
    if (/\/(capabilities|roles|members|project-templates|job-titles)\/$/.test(path)) {
      return route.fulfill({ json: [] });
    }
    if (path.includes("/department") || path.includes("/activities")) {
      return route.fulfill({ json: list([]) });
    }
    return route.fulfill({ json: list([]) });
  });
}

test.describe("027 contractor stakeholder select", () => {
  test.setTimeout(90_000);

  test("ذینفعان create form exposes contractor role option", async ({ page }) => {
    await session(page, ["admin"]);
    await mockProjectShell(page, { contractors: [] });
    await visit(page, `/projects/${projectId}/stakeholders`);
    await expect(page.getByTestId("stakeholders-page")).toBeVisible({ timeout: 15_000 });
    await expect(page.locator("#stakeholder-create-role")).toBeVisible();
    await page.locator("#stakeholder-create-role").click();
    await expect(page.getByRole("option", { name: /پیمانکار|Contractor/i })).toBeVisible();
  });

  test("department ContractorSelect shows empty help then populated option", async ({
    page,
  }) => {
    await session(page, ["admin"]);
    await mockProjectShell(page, { contractors: [] });
    await visit(page, `/projects/${projectId}/buildings`);
    const emptySelect = page.getByTestId("input-departmentActivityFilterContractor");
    await expect(emptySelect).toBeVisible({ timeout: 20_000 });
    await expect(
      page.getByText(/No contractors yet|ذینفعان/i).first(),
    ).toBeVisible({ timeout: 10_000 });

    await mockProjectShell(page, { contractors: [contractorRow] });
    await page.reload();
    await visit(page, `/projects/${projectId}/buildings`);
    const filled = page.getByTestId("input-departmentActivityFilterContractor");
    await expect(filled).toBeVisible({ timeout: 20_000 });
    await filled.click();
    await expect(page.getByRole("option", { name: /Acme Contractor/i })).toBeVisible({
      timeout: 10_000,
    });
  });
});
