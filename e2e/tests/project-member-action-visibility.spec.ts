import { expect, test } from "@playwright/test";
import { session, visit } from "../helpers/navigation";

const projectId = "11111111-1111-4111-8111-111111111111";

for (const scenario of [
  { name: "viewer", active: true, grant: false, visible: false },
  { name: "active manager", active: true, grant: true, visible: true },
  { name: "inactive manager with retained grant", active: false, grant: true, visible: false },
]) {
  test(`${scenario.name} sees only permitted team actions`, async ({ page }, info) => {
    test.skip(info.project.name === "pwa-offline", "Requires dev server");
    await session(page);
    const base = `/api/v1/projects/${projectId}`;
    await page.route(`**${base}/`, route => route.fulfill({ json: {
      id: projectId, project_id: projectId, project_name: "Access test", status: "active",
    } }));
    await page.route(`**${base}/members/`, route => route.fulfill({ json: [{
      user_id: "navigation-user", full_name: "Test member", email: "", mobile: "", roles: ["viewer"],
      status: scenario.active ? "active" : "inactive", joined_at: "2026-10-15", last_login: null,
    }] }));
    await page.route(`**${base}/members/*/permissions/`, route => route.fulfill({ json: {
      effective: { view_project: true, manage_members: scenario.grant }, permissions: [],
    } }));
    const permissionResponse = page.waitForResponse(response =>
      response.url().includes(`${base}/members/navigation-user/permissions/`) && response.ok(),
    );
    await visit(page, `/projects/${projectId}/settings/members`, "en");
    await permissionResponse;
    const table = page.getByRole("table");
    await expect(table.getByText("Test member")).toBeVisible();
    const add = page.getByRole("button", { name: "Add member", exact: true });
    const edit = table.getByRole("button", { name: "Edit", exact: true });
    if (scenario.visible) {
      await expect(add).toBeVisible();
      await expect(edit).toBeVisible();
    } else {
      await expect(add).toHaveCount(0);
      await expect(edit).toHaveCount(0);
      await expect(table.getByRole("button", { name: "Deactivate", exact: true })).toHaveCount(0);
    }
  });
}
