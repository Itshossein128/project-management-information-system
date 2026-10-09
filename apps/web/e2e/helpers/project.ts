import type { Page } from "@playwright/test";

const API_BASE = "http://127.0.0.1:8000/api";

async function authHeaders(page: Page): Promise<Record<string, string>> {
  // Prefer storageState-style read; fall back after ensuring a document is loaded.
  let access = await page
    .evaluate(() => localStorage.getItem("auth_access_token"))
    .catch(() => null);
  if (!access) {
    await page.goto("/projects", { waitUntil: "domcontentloaded" });
    access = await page.evaluate(() => localStorage.getItem("auth_access_token"));
  }
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

/** Upsert a budget row via API. */
export async function createBudgetViaApi(
  page: Page,
  projectBasePath: string,
  opts: {
    wbsId?: string;
    activityId?: string;
    costCategory?: string;
    budgetAmount: number;
  },
): Promise<void> {
  const projectId = projectBasePath.split("/").pop();
  if (!projectId) throw new Error("invalid projectBasePath");
  const res = await page.request.post(`${API_BASE}/v1/projects/${projectId}/budgets/bulk/`, {
    headers: await authHeaders(page),
    data: [
      {
        wbs: opts.wbsId ?? null,
        activity: opts.activityId ?? null,
        cost_category: opts.costCategory ?? "labor",
        budget_amount: opts.budgetAmount,
      },
    ],
  });
  if (!res.ok()) {
    throw new Error(`createBudgetViaApi failed: ${res.status()} ${await res.text()}`);
  }
}

/** Submit + approve a draft project so protected-field CR rules apply. */
export async function activateProjectViaApi(
  page: Page,
  projectBasePath: string,
): Promise<void> {
  const projectId = projectBasePath.split("/").pop();
  if (!projectId) throw new Error("invalid projectBasePath");
  const headers = await authHeaders(page);
  const patch = await page.request.patch(`${API_BASE}/v1/projects/${projectId}/`, {
    headers,
    data: {
      scope_description: "E2E activation scope",
      contract_amount: "1000000",
    },
  });
  if (!patch.ok()) {
    throw new Error(`activateProjectViaApi patch failed: ${patch.status()} ${await patch.text()}`);
  }
  const submit = await page.request.post(
    `${API_BASE}/v1/projects/${projectId}/submit/`,
    { headers },
  );
  if (!submit.ok()) {
    throw new Error(`activateProjectViaApi submit failed: ${submit.status()} ${await submit.text()}`);
  }
  const approve = await page.request.post(
    `${API_BASE}/v1/projects/${projectId}/approve/`,
    { headers },
  );
  if (!approve.ok()) {
    throw new Error(
      `activateProjectViaApi approve failed: ${approve.status()} ${await approve.text()}`,
    );
  }
}

/** Disable or enable a project capability via API. */
export async function updateCapabilityViaApi(
  page: Page,
  projectBasePath: string,
  capabilityKey: string,
  enabled: boolean,
): Promise<void> {
  const projectId = projectBasePath.split("/").pop();
  if (!projectId) throw new Error("invalid projectBasePath");
  const res = await page.request.patch(
    `${API_BASE}/v1/projects/${projectId}/capabilities/${capabilityKey}/`,
    {
      headers: await authHeaders(page),
      data: {
        enabled,
        mode: enabled ? "optional" : "disabled",
      },
    },
  );
  if (!res.ok()) {
    throw new Error(
      `updateCapabilityViaApi failed: ${res.status()} ${await res.text()}`,
    );
  }
}

/** Create an active fiscal period lock via API. */
export async function createFiscalLockViaApi(
  page: Page,
  projectBasePath: string,
  opts: {
    periodStart?: string;
    periodEnd?: string;
    reason?: string;
  } = {},
): Promise<string> {
  const projectId = projectBasePath.split("/").pop();
  if (!projectId) throw new Error("invalid projectBasePath");
  const res = await page.request.post(
    `${API_BASE}/v1/projects/${projectId}/fiscal-period-locks/`,
    {
      headers: await authHeaders(page),
      data: {
        period_start: opts.periodStart ?? "2020-01-01",
        period_end: opts.periodEnd ?? "2030-12-31",
        reason: opts.reason ?? "E2E fiscal lock",
      },
    },
  );
  if (!res.ok()) {
    throw new Error(
      `createFiscalLockViaApi failed: ${res.status()} ${await res.text()}`,
    );
  }
  const body = (await res.json()) as { id?: string };
  if (!body.id) {
    throw new Error(`createFiscalLockViaApi missing id: ${JSON.stringify(body)}`);
  }
  return body.id;
}

/** Create an actual cost via API. Returns cost id. */
export async function createActualCostViaApi(
  page: Page,
  projectBasePath: string,
  opts: {
    costDate?: string;
    costCategory?: string;
    amount: number;
    wbsId?: string;
    activityId?: string;
    description?: string;
  },
): Promise<string> {
  const projectId = projectBasePath.split("/").pop();
  if (!projectId) throw new Error("invalid projectBasePath");
  const res = await page.request.post(`${API_BASE}/v1/projects/${projectId}/costs/`, {
    headers: await authHeaders(page),
    data: {
      cost_date: opts.costDate ?? "2026-01-15",
      cost_category: opts.costCategory ?? "labor",
      amount: opts.amount,
      wbs: opts.wbsId ?? null,
      activity: opts.activityId ?? null,
      description: opts.description ?? "E2E actual cost",
    },
  });
  if (!res.ok()) {
    throw new Error(`createActualCostViaApi failed: ${res.status()} ${await res.text()}`);
  }
  const body = (await res.json()) as { id?: string };
  if (!body.id) throw new Error(`createActualCostViaApi missing id: ${JSON.stringify(body)}`);
  return body.id;
}

/** Create an activity via API. Returns activity id. */
export async function createActivityViaApi(
  page: Page,
  projectBasePath: string,
  opts: { code: string; name: string; wbsId: string; totalQuantity?: number },
): Promise<string> {
  const projectId = projectBasePath.split("/").pop();
  if (!projectId) throw new Error("invalid projectBasePath");
  const res = await page.request.post(`${API_BASE}/v1/projects/${projectId}/activities/`, {
    headers: await authHeaders(page),
    data: {
      activity_code: opts.code,
      activity_name: opts.name,
      wbs_id: opts.wbsId,
      status: "not_started",
      ...(opts.totalQuantity != null ? { total_quantity: opts.totalQuantity } : {}),
    },
  });
  if (!res.ok()) {
    throw new Error(`createActivityViaApi failed: ${res.status()} ${await res.text()}`);
  }
  const body = (await res.json()) as { activity_id?: string; id?: string };
  const id = body.activity_id ?? body.id;
  if (!id) throw new Error(`createActivityViaApi missing id: ${JSON.stringify(body)}`);
  return id;
}

/** Create a draft daily report with one activity row. Returns report id. */
export async function createDailyReportViaApi(
  page: Page,
  projectBasePath: string,
  opts: {
    reportDate?: string;
    shift?: "day" | "night" | "full";
    activityId?: string;
    activityDescription?: string;
    quantity?: number;
  } = {},
): Promise<string> {
  const projectId = projectBasePath.split("/").pop();
  if (!projectId) throw new Error("invalid projectBasePath");
  const headers = await authHeaders(page);
  const createRes = await page.request.post(`${API_BASE}/v1/projects/${projectId}/daily-reports/`, {
    headers,
    data: {
      report_date: opts.reportDate ?? "1404/04/26",
      shift: opts.shift ?? "full",
      site_status: "active",
      weather_condition: "sunny",
    },
  });
  if (!createRes.ok()) {
    throw new Error(`createDailyReportViaApi failed: ${createRes.status()} ${await createRes.text()}`);
  }
  const created = (await createRes.json()) as { report_id?: string; id?: string };
  const reportId = created.report_id ?? created.id;
  if (!reportId) {
    throw new Error(`createDailyReportViaApi missing id: ${JSON.stringify(created)}`);
  }

  const activityRes = await page.request.post(
    `${API_BASE}/v1/projects/${projectId}/daily-reports/${reportId}/activities/`,
    {
      headers,
      data: {
        activity_ref: opts.activityId ?? null,
        activity_description: opts.activityDescription ?? "E2E activity row",
        shift: "shift_1",
        quantity: opts.quantity ?? 10,
        quantity_measured: true,
        unit: "m3",
      },
    },
  );
  if (!activityRes.ok()) {
    throw new Error(
      `createDailyReportViaApi activity failed: ${activityRes.status()} ${await activityRes.text()}`,
    );
  }
  return reportId;
}
