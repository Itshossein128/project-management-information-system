import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

export interface ManpowerRow {
  id: string;
  report_date: string;
  labor_category: "indirect" | "direct";
  job_title: string;
  shift_1_count: number;
  shift_2_count: number;
  shift_3_count: number;
  total_count: number;
}

export interface JobTitles {
  indirect: { id: string; title: string }[];
  direct: { id: string; title: string }[];
}

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export function fetchJobTitles(projectId: string) {
  return apiJson<{ results: { category: string; title: string }[] }>(
    `${base(projectId)}/manpower/job-titles/`,
  ).then((data) => {
    const indirect = data.results.filter((r) => r.category === "indirect").map((r) => ({ id: r.title, title: r.title }));
    const direct = data.results.filter((r) => r.category === "direct").map((r) => ({ id: r.title, title: r.title }));
    return { indirect, direct } as JobTitles;
  });
}

export function fetchManpower(projectId: string, date: string) {
  return apiJson<ManpowerRow[]>(`${base(projectId)}/manpower/?date=${encodeURIComponent(date)}`);
}

export function saveManpowerDay(projectId: string, rows: Partial<ManpowerRow>[]) {
  return apiJson(`${base(projectId)}/manpower/`, { method: "POST", body: JSON.stringify(rows) });
}
