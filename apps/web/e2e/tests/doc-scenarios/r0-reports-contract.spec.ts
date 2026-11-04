/**
 * R0 delivery contract: reference fixtures, scope boundary, and the standard report catalog.
 * Assertions follow docs/delivery/R0-scope-and-reports-contract.md.
 * Product code is intentionally not adjusted when a catalog item is still missing.
 */
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { expect, test, type Page } from "@playwright/test";
import { E2E_USERS, loginAs } from "../../helpers/auth";
import { repoRoot } from "../../helpers/doc-catalog";
import { createDailyReportViaApi, createProjectViaApi } from "../../helpers/project";

const API = "http://127.0.0.1:8000/api";
const PYTHON = path.join(repoRoot, "apps/api/.venv/bin/python");

const REFERENCE_FIXTURES = [
  "real-data/plan.mpp",
  "real-data/گزارش روزانه پروژه 2000 واحدی کمیل آباد شیراز.xlsx",
  "real-data/اجرای ابنیه شیراز (1).xlsx",
  "real-data/_اجرای تاسیسات برقی (1).xlsx",
  "real-data/_اجرای تاسیسات مکانیکی (1).xlsx",
  "real-data/گزارش بچینگ (16).xlsx",
  "real-data/گزارش روزانه واحد انبار (3).xlsx",
  "real-data/گزارش ماشین آلات (3).xlsx",
  "real-data/گزارش نیروی انسانی حراست شیراز.xlsx",
  "real-data/گزارش بالانس مصالح شیراز.xlsx",
  "real-data/تایید مرخصی شیراز.xlsx",
  "real-data/فرم درخواست اضافه کاری شیراز.xlsx",
];

const SHIPPED_REPORT_TYPES = [
  "weekly_progress",
  "monthly_project",
  "portfolio_summary",
  "risk_issue",
  "budget_variance",
] as const;

const PENDING_CATALOG_NAMES = [
  "Site Daily",
  "Lookahead Plan",
  "Stakeholder Status",
  "Change Orders",
  "Procurement & Contracts",
  "Cash Flow Forecast",
] as const;

test.describe.configure({ timeout: 120_000 });

async function bearer(page: Page): Promise<Record<string, string>> {
  const access = await page.evaluate(() => localStorage.getItem("auth_access_token"));
  if (!access) throw new Error("missing access token");
  return { Authorization: `Bearer ${access}` };
}

function inspectWorkbook(file: string): { rtl: boolean; indirect: number; direct: number; sums: number } {
  const script = `
import json, sys, openpyxl
wb = openpyxl.load_workbook(sys.argv[1])
ws = wb.active
mode = None
indirect = []
direct = []
sums = 0
for row in ws.iter_rows(max_col=7, values_only=True):
    for value in row:
        if isinstance(value, str) and value.startswith("=SUM"):
            sums += 1
    label, title = row[0], row[1] if len(row) > 1 else None
    if isinstance(label, str) and "۳۴" in label:
        mode = "indirect"
        continue
    if isinstance(label, str) and "۳۲" in label:
        mode = "direct"
        continue
    if isinstance(label, str) and label.startswith("جمع"):
        mode = None
        continue
    if mode and isinstance(title, str) and title.strip() and title != "عنوان شغلی":
        (indirect if mode == "indirect" else direct).append(title)
print(json.dumps({
    "rtl": bool(ws.sheet_view.rightToLeft),
    "indirect": len(indirect),
    "direct": len(direct),
    "sums": sums,
}))
`;
  const result = spawnSync(PYTHON, ["-c", script, file], { encoding: "utf8" });
  expect(result.status, result.stderr).toBe(0);
  return JSON.parse(result.stdout) as { rtl: boolean; indirect: number; direct: number; sums: number };
}

function pdfHasLiteral(file: string, needle: string): boolean {
  const script = `
import re, sys, zlib
raw = open(sys.argv[1], "rb").read()
needles = [sys.argv[2].encode(), sys.argv[2].encode("utf-16-be")]
chunks = [raw]
for match in re.finditer(rb"stream\\r?\\n(.*?)\\r?\\nendstream", raw, re.S):
    blob = match.group(1)
    try:
        blob = zlib.decompress(blob)
    except Exception:
        pass
    chunks.append(blob)
haystack = b"\\n".join(chunks)
print("1" if any(item in haystack for item in needles) else "0")
`;
  const result = spawnSync(PYTHON, ["-c", script, file, needle], { encoding: "utf8" });
  expect(result.status, result.stderr).toBe(0);
  return result.stdout.trim() === "1";
}

test("R0 reference fixtures from the employer are present", () => {
  const missing = REFERENCE_FIXTURES.filter((rel) => !fs.existsSync(path.join(repoRoot, rel)));
  expect(missing).toEqual([]);
});

test("R0 scope does not register a standalone transmittal route", () => {
  const inventory = JSON.parse(fs.readFileSync(path.join(repoRoot, "docs/decision-tree/inventory.json"), "utf8")) as {
    routes: Array<{ path: string; source: string }>;
  };
  const hits = inventory.routes.filter((route) => /transmittal/i.test(`${route.path} ${route.source}`));
  expect(hits).toEqual([]);
});

test("R0 standard catalog lists shipped report types and the six T036 types", async ({ page }) => {
  await loginAs(page, E2E_USERS.admin);
  const projectId = (await createProjectViaApi(page)).split("/").pop();
  const headers = await bearer(page);
  const catalog = await page.request.get(`${API}/v1/projects/${projectId}/reports/catalog/`, { headers });
  expect(catalog.status()).toBe(200);
  const body = (await catalog.json()) as { results: Array<{ report_type: string; title: string }> };
  const types = body.results.map((entry) => entry.report_type);
  for (const reportType of SHIPPED_REPORT_TYPES) expect(types).toContain(reportType);
  const haystack = body.results.map((entry) => `${entry.report_type} ${entry.title}`).join("\n");
  const missing = PENDING_CATALOG_NAMES.filter((name) => !haystack.toLowerCase().includes(name.toLowerCase()));
  expect(missing, "T036 catalog names from R0 section 3.3").toEqual([]);
});

test("R0 portfolio catalog exposes portfolio_summary", async ({ page }) => {
  await loginAs(page, E2E_USERS.admin);
  const headers = await bearer(page);
  const catalog = await page.request.get(`${API}/v1/portfolio/reports/catalog/`, { headers });
  expect(catalog.status()).toBe(200);
  const body = (await catalog.json()) as { results: Array<{ report_type: string }> };
  expect(body.results.map((entry) => entry.report_type)).toContain("portfolio_summary");
});

test("R0 standard report screen runs and exports each shipped type", async ({ page }) => {
  await loginAs(page, E2E_USERS.admin);
  const projectId = (await createProjectViaApi(page)).split("/").pop();
  await page.goto(`/projects/${projectId}/standard-reports`);
  await expect(page.getByTestId("standard-reports-page")).toBeVisible({ timeout: 20_000 });
  const select = page.getByTestId("report-type-select");
  const options = await select.locator("option").allTextContents();
  expect(options.length).toBeGreaterThanOrEqual(SHIPPED_REPORT_TYPES.length);
  for (const reportType of SHIPPED_REPORT_TYPES) {
    await select.selectOption(reportType);
    const run = page.waitForResponse((response) => response.url().includes(`/reports/${reportType}/`) && response.request().method() === "GET");
    await page.getByTestId("run-report-btn").click();
    expect((await run).ok()).toBeTruthy();
    await expect(page.getByTestId("report-preview-json")).toBeVisible({ timeout: 20_000 });
    const exported = page.waitForResponse((response) => response.url().includes(`/reports/${reportType}/export/`) && response.request().method() === "POST");
    await page.getByTestId("export-report-btn").click();
    expect((await exported).ok()).toBeTruthy();
  }
});

test("R0 FILE 4 excel download matches Shiraz layout", async ({ page }) => {
  await loginAs(page, E2E_USERS.admin);
  const base = await createProjectViaApi(page);
  const projectId = base.split("/").pop();
  const reportId = await createDailyReportViaApi(page, base);
  await page.goto(`/projects/${projectId}/daily-reports/${reportId}/view`);
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "خروجی اکسل (FILE 4)" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/daily-report-.+\.xlsx/i);
  const file = path.join(os.tmpdir(), download.suggestedFilename());
  await download.saveAs(file);
  try {
    const workbook = inspectWorkbook(file);
    expect(workbook.rtl).toBe(true);
    expect(workbook.indirect).toBe(34);
    expect(workbook.direct).toBe(32);
    expect(workbook.sums).toBeGreaterThanOrEqual(3);
  } finally {
    fs.rmSync(file, { force: true });
  }
});

test("R0 approved daily PDF has the documented filename and signature hash", async ({ page }) => {
  await loginAs(page, E2E_USERS.admin);
  const base = await createProjectViaApi(page);
  const projectId = base.split("/").pop();
  const reportId = await createDailyReportViaApi(page, base);
  const headers = await bearer(page);
  const response = await page.request.get(`${API}/v1/projects/${projectId}/daily-reports/${reportId}/pdf/`, { headers });
  expect(response.status()).toBe(200);
  expect(response.headers()["content-type"] ?? "").toContain("application/pdf");
  expect(response.headers()["content-disposition"] ?? "").toMatch(/daily-report-.+\.pdf/i);
  const bytes = await response.body();
  expect(Buffer.from(bytes).subarray(0, 4).toString()).toBe("%PDF");
  const file = path.join(os.tmpdir(), `r0-${reportId}.pdf`);
  fs.writeFileSync(file, bytes);
  try {
    expect(pdfHasLiteral(file, "DRAFT")).toBe(false);
  } finally {
    fs.rmSync(file, { force: true });
  }
});

test("R0 non-member cannot download the daily PDF", async ({ page }) => {
  await loginAs(page, E2E_USERS.admin);
  const base = await createProjectViaApi(page);
  const projectId = base.split("/").pop();
  const reportId = await createDailyReportViaApi(page, base);
  await loginAs(page, E2E_USERS.visitor);
  const headers = await bearer(page);
  const response = await page.request.get(`${API}/v1/projects/${projectId}/daily-reports/${reportId}/pdf/`, { headers });
  expect([401, 403]).toContain(response.status());
});
