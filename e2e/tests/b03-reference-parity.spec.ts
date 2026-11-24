import { readFile } from "node:fs/promises";
import { expect, test, type Locator, type Page, type TestInfo } from "@playwright/test";

const project = "fbed68bb-3382-44ba-a87e-3b4119cc3f2b";
const reference = "fb9bcd42-a786-4b19-ba7b-1548c9526393";
const date = "2027-05-22";
const root = `/projects/${project}`;
const api = process.env.B03_TEST_API_URL ?? "http://localhost:8000/api";
const password = process.env.B03_TEST_PASSWORD;
const units = ["buildings", "electrical", "mechanical", "machinery", "warehouse", "security"] as const;

async function saveDownload(page: Page, button: Locator, filename: string, testInfo: TestInfo) {
  await expect(button).toBeVisible({ timeout: 15_000 });
  await button.focus();
  const [download] = await Promise.all([page.waitForEvent("download"), button.press("Enter")]);
  expect(download.suggestedFilename()).toBe(filename);
  const destination = testInfo.outputPath(filename);
  await download.saveAs(destination);
  const bytes = await readFile(destination);
  expect(bytes.length).toBeGreaterThan(1000);
  expect(bytes.subarray(0, filename.endsWith(".pdf") ? 4 : 2).toString()).toBe(
    filename.endsWith(".pdf") ? "%PDF" : "PK",
  );
}

for (const language of ["fa", "en"] as const) {
  test(`B03 signed-in report downloads in ${language}`, async ({ page, request }, testInfo) => {
    test.skip(!password, "Prepare the isolated B03 browser fixture and set B03_TEST_PASSWORD");
    test.setTimeout(120_000);
    const login = await request.post(`${api}/auth/login/`, {
      data: { username: "b03-browser-viewer", password },
    });
    expect(login.status()).toBe(200);
    const session = await login.json();
    await page.addInitScript(({ language, session }) => {
      localStorage.setItem("app-language", language);
      localStorage.setItem("i18nextLng", language);
      localStorage.setItem("auth_access_token", session.access);
      localStorage.setItem("auth_refresh_token", session.refresh);
      localStorage.setItem("auth_user", JSON.stringify(session.user));
    }, { language, session });

    await page.goto(`${root}/daily-reports/${reference}/view`);
    await expect(page.getByText("SIM-A1-001-12-1406-03-01", { exact: true })).toBeVisible({ timeout: 15_000 });
    const dailyExcel = language === "fa" ? "دریافت اکسل روزانه (FILE 4)" : "Download daily Excel (FILE 4)";
    const dailyPdf = language === "fa" ? "دریافت PDF روزانه" : "Download daily PDF";
    await saveDownload(page, page.getByRole("button", { name: dailyExcel }), "daily-report-1406-03-01-full.xlsx", testInfo);
    await saveDownload(page, page.getByRole("button", { name: dailyPdf }), "daily-report-1406-03-01-full.pdf", testInfo);

    const rangeLabel = language === "fa" ? "دریافت اکسل گزارش‌های تأییدشده" : "Download approved reports (Excel)";
    await page.goto(`${root}/daily-reports`);
    const dateText = language === "fa" ? "۱۴۰۶/۰۳/۰۱" : date;
    const start = page.getByLabel(language === "fa" ? "از تاریخ" : "Start date");
    const end = page.getByLabel(language === "fa" ? "تا تاریخ" : "End date");
    await start.fill(dateText);
    await start.press("Tab");
    await expect(page).toHaveURL(/date_from=2027-05-22/);
    await end.fill(dateText);
    await end.press("Tab");
    await expect(page).toHaveURL(/date_from=2027-05-22.*date_to=2027-05-22/);
    await saveDownload(
      page, page.getByRole("button", { name: rangeLabel }), "daily-reports-1406-03-01-1406-03-01.xlsx", testInfo,
    );
    await page.goto(`${root}/daily-reports?date_from=2027-05-23&date_to=${date}`);
    const rangeButton = page.getByRole("button", { name: rangeLabel });
    await rangeButton.focus();
    const [errorResponse] = await Promise.all([
      page.waitForResponse((response) => response.url().includes("/daily-reports/excel/")),
      rangeButton.press("Enter"),
    ]);
    expect(errorResponse.status()).toBe(400);
    await expect(page.getByText(language === "fa"
      ? "تاریخ شروع و پایان معتبر و به ترتیب زمانی وارد کنید."
      : "Enter valid start and end dates in chronological order.")).toBeVisible();

    for (const unit of units) {
      const configurationResponse = unit === "machinery"
        ? page.waitForResponse((response) => response.url().includes("/reporting-configuration/"))
        : undefined;
      await page.goto(`${root}/${unit}?date=${date}`);
      await expect(page.locator("#text-unitReportVersion")).toBeVisible();
      if (configurationResponse) {
        const response = await configurationResponse;
        expect(response.status()).toBe(200);
        expect(new URL(response.url()).searchParams.get("date")).toBe(date);
      }
      const pdfLabel = language === "fa" ? "دریافت PDF واحد" : "Download unit PDF";
      await saveDownload(
        page, page.getByRole("button", { name: pdfLabel, exact: true }), `unit-daily-report-${unit}-1406-03-01.pdf`, testInfo,
      );
      if (unit === "buildings" || unit === "electrical") {
        const filename = unit === "buildings" ? "civil-subreport" : "electrical-subreport";
        await saveDownload(page, page.locator("#button-exportUnitReportExcel"), `${filename}-1406-03-01.xlsx`, testInfo);
      }
    }
  });
}

test("B03 project viewer downloads a validated attachment through the linked report", async ({ page, request }) => {
  test.skip(!password || process.env.B03_TEST_ATTACHMENTS !== "1", "Use the isolated B03 storage fixture");
  const editorLogin = await request.post(`${api}/auth/login/`, {
    data: { username: "b03-browser-editor", password },
  });
  expect(editorLogin.status()).toBe(200);
  const editor = await editorLogin.json();
  const editorOptions = { headers: { Authorization: `Bearer ${editor.access}` } };
  const collection = `${api}/v1/projects/${project}/units/buildings/daily-reports`;
  const currentResponse = await request.get(`${collection}/current/?date=${date}`, editorOptions);
  expect(currentResponse.status()).toBe(200);
  const unit = await currentResponse.json();
  const rowsResponse = await request.get(`${collection}/${unit.id}/activities/`, editorOptions);
  expect(rowsResponse.status()).toBe(200);
  const activities = await rowsResponse.json();
  const bytes = Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAFklEQVR4nGOUi+phYGBgYmBgYGBgAAAL7AEIG73urAAAAABJRU5ErkJggg==", "base64");
  const uploaded = await request.post(`${collection}/${unit.id}/attachments/`, {
    ...editorOptions,
    multipart: { row_id: activities[0].id, file: { name: "fixture.png", mimeType: "image/png", buffer: bytes } },
  });
  expect(uploaded.status()).toBe(201);

  const viewerLogin = await request.post(`${api}/auth/login/`, {
    data: { username: "b03-browser-viewer", password },
  });
  expect(viewerLogin.status()).toBe(200);
  const viewer = await viewerLogin.json();
  await page.addInitScript((session) => {
    localStorage.setItem("app-language", "en");
    localStorage.setItem("i18nextLng", "en");
    localStorage.setItem("auth_access_token", session.access);
    localStorage.setItem("auth_refresh_token", session.refresh);
    localStorage.setItem("auth_user", JSON.stringify(session.user));
  }, viewer);
  await page.goto(`${root}/daily-reports/${reference}/view`);
  const button = page.getByRole("button", { name: "Download photo 1" });
  await button.focus();
  const [download] = await Promise.all([page.waitForEvent("download"), button.press("Enter")]);
  const file = await download.path();
  expect(file).toBeTruthy();
  expect(await readFile(file!)).toEqual(bytes);
});
