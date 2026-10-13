import { expect, type Page, type Route } from "@playwright/test";
import { createProjectViaApi } from "../../helpers/project";
import { readFileSync } from "node:fs";
export const copies = {
  en: JSON.parse(readFileSync("apps/web/src/app/locales/en.json", "utf8"))
    .decisionSupport,
  fa: JSON.parse(readFileSync("apps/web/src/app/locales/fa.json", "utf8"))
    .decisionSupport,
};
export function gate() {
  let release!: () => void;
  const held = new Promise<void>((r) => (release = r));
  return { held, release };
}
export async function setup(
  page: Page,
  locale: "en" | "fa" = "en",
  overrides: Record<string, unknown> = {},
) {
  await page.goto("/projects");
  const path = await createProjectViaApi(page);
  const projectId = path.split("/").pop()!;
  const token = await page.evaluate(() =>
    localStorage.getItem("auth_access_token"),
  );
  const headers = { Authorization: "Bearer " + token };
  const base =
    "http://127.0.0.1:8000/api/v1/projects/" + projectId + "/decision-cases/";
  const r = await page.request.post(base, {
    headers,
    data: {
      title: "Records " + Date.now(),
      selected_methods: ["saw", "topsis", "ahp", "ism"],
      criteria: ["Cost", "Quality"],
      alternatives: ["Alpha", "Beta"],
      weights: [2, 3],
      types: ["cost", "benefit"],
      performance_matrix: [
        [4, 6],
        [2, 3],
      ],
      ahp_matrix: [
        [1, 2],
        [0.5, 1],
      ],
      ism_matrix: [
        [0, 1],
        [0, 0],
      ],
      ...overrides,
    },
  });
  expect(r.status(), await r.text()).toBe(201);
  const c = await r.json();
  await page.goto(path + "/decision-support");
  await page.locator("#button-language-" + locale).click();
  await page.getByRole("button", { name: c.title, exact: true }).click();
  await expect(page.locator("#ds-title")).toHaveValue(c.title);
  return { path, projectId, base, headers, c, copy: copies[locale] };
}
export async function commitThenReplace(route: Route, body: string) {
  const response = await route.fetch();
  expect(response.status()).toBe(201);
  const committed = await response.json();
  await route.fulfill({ status: 201, contentType: "application/json", body });
  return committed.id as string;
}
// Controlled historical fixtures are local test ORM inserts only; never live calculation proof.
import { execFileSync } from "node:child_process";
export function insertHistorical(
  caseId: string,
  records: { method: string; input_snapshot: unknown; result: unknown }[],
) {
  const data = JSON.stringify(records);
  const code =
    "import json\nfrom decision_support.models import DecisionCase,DecisionRun\nfrom django.utils import timezone\nfrom django.db.models import Value,JSONField\nc=DecisionCase.objects.get(pk=" +
    JSON.stringify(caseId) +
    ")\nrows=json.loads(" +
    JSON.stringify(data) +
    ')\nfor r in rows:\n for k in ("input_snapshot","result"):\n  if r[k] is None: r[k]=Value(None,output_field=JSONField())\n DecisionRun.objects.create(case=c,project=c.project,extracted_by=c.created_by,extracted_at=timezone.now(),**r)';
  execFileSync("bash", ["apps/api/django.sh", "shell", "-c", code], {
    stdio: "pipe",
  });
}
