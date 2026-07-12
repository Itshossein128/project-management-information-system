import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export interface SubcontractorRow {
  id: string;
  company_name: string;
  discipline: string;
  status: string;
  latest_score: number | null;
  financial_summary: {
    total_billed: number;
    total_paid: number;
    outstanding: number;
    retention_held: number;
    advance_remaining: number;
  };
  risk_flag: boolean;
  risk_reasons: string[];
  warning_count: number;
}

export function fetchSubcontractors(projectId: string) {
  return apiJson<{ results: SubcontractorRow[] }>(`${base(projectId)}/subcontractors/`);
}

export function fetchSubcontractor(projectId: string, id: string) {
  return apiJson<SubcontractorRow>(`${base(projectId)}/subcontractors/${id}/`);
}

export function createSubcontractor(projectId: string, body: Record<string, unknown>) {
  return apiJson<SubcontractorRow>(`${base(projectId)}/subcontractors/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function formatFaAmount(v: number) {
  return new Intl.NumberFormat("fa-IR").format(Math.round(v));
}

export const STATUS_LABELS: Record<string, string> = {
  active: "فعال",
  suspended: "تعلیق‌شده",
  completed: "تکمیل‌شده",
  terminated: "فسخ‌شده",
};
