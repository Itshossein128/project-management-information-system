import type { Page } from "@playwright/test";

const API_BASE = "http://127.0.0.1:8000/api";

async function authHeaders(page: Page): Promise<Record<string, string>> {
  const access = await page.evaluate(() => localStorage.getItem("auth_access_token"));
  if (!access) throw new Error("authHeaders requires loginAs first");
  return {
    Authorization: `Bearer ${access}`,
    "Content-Type": "application/json",
  };
}

/** Create a project via API (authenticated) and return its `/projects/{uuid}` base path. */
export async function createProjectViaApi(page: Page): Promise<string> {
  const code = `s3-${Date.now()}`;
  const res = await page.request.post(`${API_BASE}/v1/projects/`, {
    headers: await authHeaders(page),
    data: {
      project_code: code,
      project_name: `Sprint3 ${code}`,
      employer: "E2E Employer",
      start_date: "2026-01-01",
    },
  });
  if (!res.ok()) {
    throw new Error(`createProjectViaApi failed: ${res.status()} ${await res.text()}`);
  }
  const body = (await res.json()) as { id?: string; project_id?: string };
  const id = body.project_id ?? body.id;
  if (!id) throw new Error(`createProjectViaApi missing id: ${JSON.stringify(body)}`);
  return `/projects/${id}`;
}

/** Create a root WBS node via API. Returns the node id. */
export async function createRootWbs(
  page: Page,
  projectBasePath: string,
  opts: { code?: string; name?: string } = {},
): Promise<string> {
  const projectId = projectBasePath.split("/").pop();
  if (!projectId) throw new Error("invalid projectBasePath");
  const res = await page.request.post(`${API_BASE}/v1/projects/${projectId}/wbs/`, {
    headers: await authHeaders(page),
    data: {
      wbs_code: opts.code ?? "1",
      wbs_name: opts.name ?? "Root Phase",
    },
  });
  if (!res.ok()) {
    throw new Error(`createRootWbs failed: ${res.status()} ${await res.text()}`);
  }
  const body = (await res.json()) as { wbs_id: string };
  return body.wbs_id;
}

/** Create a child WBS node via API. */
export async function createChildWbs(
  page: Page,
  projectBasePath: string,
  parentId: string,
  opts: { code: string; name: string },
): Promise<string> {
  const projectId = projectBasePath.split("/").pop();
  if (!projectId) throw new Error("invalid projectBasePath");
  const res = await page.request.post(`${API_BASE}/v1/projects/${projectId}/wbs/`, {
    headers: await authHeaders(page),
    data: {
      parent_id: parentId,
      wbs_code: opts.code,
      wbs_name: opts.name,
    },
  });
  if (!res.ok()) {
    throw new Error(`createChildWbs failed: ${res.status()} ${await res.text()}`);
  }
  const body = (await res.json()) as { wbs_id: string };
  return body.wbs_id;
}

/** Move a WBS node under a new parent (reparent as sorted_child). */
export async function moveWbsViaApi(
  page: Page,
  projectBasePath: string,
  wbsId: string,
  newParentId: string,
): Promise<void> {
  const projectId = projectBasePath.split("/").pop();
  if (!projectId) throw new Error("invalid projectBasePath");
  const res = await page.request.post(
    `${API_BASE}/v1/projects/${projectId}/wbs/${wbsId}/move/`,
    {
      headers: await authHeaders(page),
      data: { new_parent_id: newParentId, position: "sorted_child" },
    },
  );
  if (!res.ok()) {
    throw new Error(`moveWbsViaApi failed: ${res.status()} ${await res.text()}`);
  }
}
