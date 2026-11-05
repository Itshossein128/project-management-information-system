import { expect, test, type APIRequestContext, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";

// Real isolated PostgreSQL + real Django + real frontend: never intercept API responses.
const f = JSON.parse(readFileSync(process.env.A6_P1_E2E_FIXTURES!, "utf8"));
const api = process.env.A6_P1_E2E_API!.replace(/\/$/, "");
const a = `/v1/projects/${f.project_a}/`;
const b = `/v1/projects/${f.project_b}/`;
const invalidRole = "00000000-0000-4000-8000-000000000000";
const tokens: Record<string, string> = f.tokens;
const hdr = (actor: string, lang = "en") => ({ Authorization: `Bearer ${tokens[actor]}`, "Accept-Language": lang });
async function browserLogin(page: Page, lang: "fa" | "en", actor = "manager") {
  await page.addInitScript(language => { localStorage.setItem("app-language", language); localStorage.setItem("i18nextLng", language); }, lang);
  await page.goto("/login");
  await page.waitForLoadState("networkidle");
  await page.getByRole("textbox", { name: lang === "fa" ? "شماره تلفن" : "Phone number" }).fill(f.users[actor].mobile);
  await page.getByLabel(lang === "fa" ? "رمز عبور" : "Password", { exact: true }).fill(f.password);
  await page.getByRole("button", { name: lang === "fa" ? "ورود" : "Sign in", exact: true }).click();
  await expect(page).not.toHaveURL(/\/login/);
}
async function memberList(request: APIRequestContext) {
  const r = await request.get(`${api}${a}members/`, { headers: hdr("manager") }); expect(r.status()).toBe(200);
  const data = await r.json(); return Array.isArray(data) ? data : data.results;
}

test.beforeAll(async ({ request }) => {
  expect((await request.get(`${api}/auth/profile/`, { headers: hdr("manager") })).status()).toBe(200);
});


for (const lang of ["fa", "en"] as const) {
  test(`US1.1 ${lang}: stale role is rejected in actual member form`, async ({ page, request }) => {
    await browserLogin(page, lang);
    await page.goto(`/projects/${f.project_a}/settings/members`);
    await page.getByRole("button", { name: lang === "fa" ? "افزودن عضو" : "Add member", exact: true }).click();
    const dialog = page.getByRole("dialog");
    await dialog.getByRole("textbox").first().fill(f.users.new.username);
    await dialog.getByRole("button", { name: lang === "fa" ? "جستجو" : "Search", exact: true }).click();
    await dialog.getByRole("button", { name: new RegExp(f.users.new.name) }).click();
    await dialog.getByRole("checkbox", { name: new RegExp(f.temporary_roles[lang].name) }).check();
    // Real server deletion after selection: no mocked network responses or fake DOM state.
    const del = await request.delete(`${api}/v1/roles/${f.temporary_roles[lang].id}/`, { headers: hdr("admin") });
    expect(del.status()).toBe(204);
    await dialog.getByRole("button", { name: lang === "fa" ? "ذخیره" : "Save", exact: true }).click();
    await expect(page.getByRole("alert").filter({ hasText: lang === "fa" ? "وجود ندارد" : "do not exist" })).toBeVisible();
    await expect(dialog).toBeVisible();
    expect((await memberList(request)).some((m: any) => m.user_id === f.users.new.id)).toBe(false);
  });
}

test("US1.2–3: mixed role IDs on create and update preserve membership, roles and override", async ({ request }) => {
  const body = { user_id: f.users.new.id, role_ids: [f.viewer_role, invalidRole] };
  const add = await request.post(`${api}${a}members/`, { headers: hdr("manager"), data: body });
  expect(add.status()).toBe(400); expect((await add.json()).error.code).toBe("unknown_role");
  expect((await memberList(request)).some((m: any) => m.user_id === f.users.new.id)).toBe(false);
  const before = (await memberList(request)).find((m: any) => m.user_id === f.users.target.id);
  const permUrl = `${api}${a}members/${f.users.target.id}/permissions/`;
  const beforePerm = await (await request.get(permUrl, { headers: hdr("manager") })).json();
  const patch = await request.patch(`${api}${a}members/${f.users.target.id}/`, { headers: hdr("manager"), data: { status: "inactive", role_ids: [f.viewer_role, invalidRole] } });
  expect(patch.status()).toBe(400);
  const after = (await memberList(request)).find((m: any) => m.user_id === f.users.target.id);
  const afterPerm = await (await request.get(permUrl, { headers: hdr("manager") })).json();
  expect(after.status).toBe(before.status); expect(after.roles).toEqual(before.roles); expect(afterPerm.effective.edit_wbs).toBe(beforePerm.effective.edit_wbs);
});

test("US2.1–3: visitor reads catalog but cannot create, update, delete or import; writer can create", async ({ request }) => {
  expect((await request.get(`${api}/items/`, { headers: hdr("visitor") })).status()).toBe(200);
  for (const [method, tail, data] of [["post", "", {name:`blocked-${f.run}`,quantity:1,category:f.category}], ["patch", `${f.item}/`, {name:"blocked"}], ["delete", `${f.item}/`, undefined], ["post", "import_items/", {}]] as const) {
    const r = await request.fetch(`${api}/items/${tail}`, { method, headers: hdr("visitor"), data }); expect(r.status(), `${method} ${tail}`).toBe(403);
  }
  const read = await request.get(`${api}/items/${f.item}/`, { headers: hdr("visitor") }); expect(read.status()).toBe(200); expect((await read.json()).name).toBe(`A6 item ${f.run}`);
  const created = await request.post(`${api}/items/`, { headers: hdr("writer"), data: { name:`allowed-${f.run}`,quantity:1,category:f.category } }); expect(created.status()).toBe(201);
});

test("US3.1–3: inactive membership denies both positions and direct helper callers", async ({ request }) => {
  for (const tail of ["positions/", `positions/${f.position}/`, "space-material-requests/", "department-activity-records/"]) {
    expect((await request.get(`${api}${a}${tail}`, { headers: hdr("inactive") })).status(), tail).toBe(403);
    const active = await request.get(`${api}${a}${tail}`, { headers: hdr("manager") });
    expect(active.status(), tail).toBe(200);
    if (tail === "positions/") {
      const data = await active.json();
      expect((Array.isArray(data) ? data : data.results).some((row: any) => String(row.id) === f.position)).toBe(true);
    }
  }
});

test("US4.1: project A manager cannot manage project B or organization accounts", async ({ request, page }) => {
  const r = await request.post(`${api}${b}members/`, { headers: hdr("manager"), data: { user_id:f.users.new.id, role_ids:[f.viewer_role] } }); expect(r.status()).toBe(403);
  expect((await request.get(`${api}/auth/users/`, { headers: hdr("manager") })).status()).toBe(403);
  await browserLogin(page, "en"); await page.goto(`/projects/${f.project_b}/settings/members`);
  await expect(page.getByText(f.users.manager.name).first()).toBeVisible();
  await expect(page.getByRole("button", { name:"Add member", exact:true })).toHaveCount(0);
  await expect(page.getByRole("table").getByRole("button", { name:"Edit", exact:true })).toHaveCount(0);
});

test("US4.2–3: observation exception is read-only; staff, HR and inactive membership denied", async ({ request }) => {
  const path = `${api}${a}positions/`;
  for (const actor of ["staff", "hr", "inactive"]) {
    expect((await request.get(path, {headers:hdr(actor)})).status(),actor).toBe(403);
    expect((await request.get(`${path}${f.position}/`, {headers:hdr(actor)})).status(),actor).toBe(403);
  }
  for (const actor of ["admin", "superuser"]) {
    const list=await request.get(path,{headers:hdr(actor)});expect(list.status(),actor).toBe(200);
    const data=await list.json(), rows=Array.isArray(data)?data:data.results;
    expect(rows.some((x:any)=>String(x.id)===f.position)).toBe(true);
    for(const row of rows){expect(row).not.toHaveProperty("wage");expect(row).not.toHaveProperty("email");expect(row).not.toHaveProperty("phone");}
    expect((await request.get(`${path}${f.position}/`,{headers:hdr(actor)})).status()).toBe(200);
    expect((await request.post(path,{headers:hdr(actor),data:{position_name:"blocked",slug:`blocked-${f.run}`}})).status()).toBe(403);
    expect((await request.patch(`${path}${f.position}/`,{headers:hdr(actor),data:{position_name:"blocked"}})).status()).toBe(403);
    expect((await request.delete(`${path}${f.position}/`,{headers:hdr(actor)})).status()).toBe(403);
    expect((await request.post(`${api}${a}members/`,{headers:hdr(actor),data:{user_id:f.users.new.id,role_ids:[f.viewer_role]}})).status()).toBe(403);
  }
});

test("US4.4 and US5.1/3: approved policy and deferred sensitive-data boundary are traceable", async () => {
  // These acceptance criteria concern the delivered policy document, not a fictitious UI.
  const spec=readFileSync("specs/045-a6-p1-access-policy/spec.md","utf8");
  for(const id of ["PM-07","PM-08","PM-09","PM-10","PM-11","PM-12","PM-13","PM-15","PM-16","PM-17"]) expect(spec).toContain(`| ${id} |`);
  const lines=spec.split("\n");
  for (let n=1; n<=18; n++) {
    const id=`PM-${String(n).padStart(2,"0")}`;
    const line=lines.find(x=>x.startsWith(`| ${id} |`));
    expect(line, id).toBeDefined();
    const columns=line!.split("|").map(x=>x.trim());
    expect(["تصمیم‌گرفته‌شده", "پیشنهاد", "حل‌نشده", "خارج از دامنه"]).toContain(columns[3]);
    expect(columns[4], `${id} owner`).not.toBe("");
  }
  const operations=lines.find(x=>x.startsWith("| PM-13 |"))!;
  expect(operations).toContain("ویرایش می‌تواند مجاز و حذف و تأیید ممنوع باشد");
  expect(lines.find(x=>x.startsWith("| PM-09 |"))).toContain("P4");
  expect(lines.find(x=>x.startsWith("| PM-15 |"))).toContain("پیشنهاد");
  expect(lines.find(x=>x.startsWith("| PM-16 |"))).toContain("حل‌نشده");
  expect(lines.find(x=>x.startsWith("| PM-17 |"))).toContain("حل‌نشده");
});

test("US5.2: edit-only actor edits activity but cannot delete or approve", async ({ request, page }) => {
  const path=`${api}${a}activities/${f.activity}/`;
  const update=await request.patch(path,{headers:hdr("editor"),data:{activity_name:`edited-${f.run}`}});expect(update.status()).toBe(200);
  expect((await request.delete(path,{headers:hdr("editor")})).status()).toBe(403);
  expect((await request.post(`${path}measurement/approve/`,{headers:hdr("editor"),data:{}})).status()).toBe(403);
  const after=await request.get(path,{headers:hdr("editor")});expect(after.status()).toBe(200);expect((await after.json()).activity_name).toBe(`edited-${f.run}`);
  await browserLogin(page, "en", "editor");
  await page.goto(`/projects/${f.project_a}/activities`);
  await expect(page.getByRole("button", { name:"Edit A6-1" })).toBeVisible();
  await expect(page.getByRole("button", { name:"حذف", exact:true })).toHaveCount(0);
  await page.getByRole("button", { name:"Edit A6-1" }).click();
  const dialog=page.getByRole("dialog");
  await expect(dialog.getByRole("textbox", { name:"نام فعالیت" })).toBeEnabled();
  await expect(dialog.getByTestId("measurement-editor")).toBeVisible();
  await expect(dialog.getByTestId("measurement-approve-btn")).toHaveCount(0);
});
