import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export interface FinancialSummary {
  outstanding: number;
  retention_held: number;
}

export interface FinancialStatus extends FinancialSummary {
  total_billed: number;
  total_paid: number;
  advance_paid: number;
  advance_recovered: number;
  advance_remaining: number;
}

export interface PerformanceScore {
  id: string;
  score_date: string;
  progress_score: number | null;
  quality_score: number | null;
  hse_score: number | null;
  payment_compliance_score: number | null;
  cooperation_score: number | null;
  overall_score: number | null;
  evaluator: string;
  notes: string;
}

export interface SubcontractorWarning {
  id: string;
  warning_date: string;
  warning_type: string;
  reason: string;
  issued_by: string;
  resolved: boolean;
  resolved_date: string | null;
  resolution_notes: string;
}

export interface RecentActivity {
  id: string;
  report_id: string;
  report_date: string;
  shift: string;
  zone: string | null;
  block: string | null;
  floor: string | null;
  activity_description: string;
  headcount: number | null;
  quantity: number | null;
  unit: string | null;
}

export interface SubcontractorRow {
  id: string;
  company_name: string;
  contract: string | null;
  discipline: string;
  responsible_person?: string;
  phone?: string;
  status: string;
  latest_score: number | null;
  latest_score_date?: string | null;
  financial_summary: FinancialSummary;
  risk_flag: boolean;
  risk_reasons: string[];
  warning_count: number;
  active_warning_types?: string[];
}

export interface SubcontractorDetail extends SubcontractorRow {
  contract_summary: {
    id: string;
    contract_number: string;
    counterparty: string;
    contract_type: string;
    original_amount: number;
    adjusted_amount: number;
    status: string;
  } | null;
  financial_status: FinancialStatus;
  performance_history: PerformanceScore[];
  warnings: SubcontractorWarning[];
  recent_activities: RecentActivity[];
  average_overall: number | null;
  trend: "improving" | "declining" | "stable";
}

export interface ScoreListResponse {
  results: PerformanceScore[];
  average_overall: number | null;
  trend: string;
}

export function fetchSubcontractors(projectId: string, params: Record<string, string> = {}) {
  const qs = new URLSearchParams(params).toString();
  return apiJson<{ results: SubcontractorRow[] }>(
    `${base(projectId)}/subcontractors/${qs ? `?${qs}` : ""}`,
  );
}

export function fetchSubcontractor(projectId: string, id: string) {
  return apiJson<SubcontractorDetail>(`${base(projectId)}/subcontractors/${id}/`);
}

export function createSubcontractor(projectId: string, body: Record<string, unknown>) {
  return apiJson<SubcontractorRow>(`${base(projectId)}/subcontractors/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function updateSubcontractor(projectId: string, id: string, body: Record<string, unknown>) {
  return apiJson<SubcontractorDetail>(`${base(projectId)}/subcontractors/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function fetchScores(projectId: string, subId: string) {
  return apiJson<ScoreListResponse>(`${base(projectId)}/subcontractors/${subId}/scores/`);
}

export function createScore(projectId: string, subId: string, body: Record<string, unknown>) {
  return apiJson<PerformanceScore>(`${base(projectId)}/subcontractors/${subId}/scores/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function createWarning(projectId: string, subId: string, body: Record<string, unknown>) {
  return apiJson<SubcontractorWarning>(`${base(projectId)}/subcontractors/${subId}/warnings/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function resolveWarning(
  projectId: string,
  subId: string,
  warningId: string,
  body: Record<string, unknown>,
) {
  return apiJson<SubcontractorWarning>(
    `${base(projectId)}/subcontractors/${subId}/warnings/${warningId}/`,
    { method: "PATCH", body: JSON.stringify(body) },
  );
}

export function formatFaAmount(v: number) {
  return new Intl.NumberFormat("fa-IR").format(Math.round(v));
}

export const STATUS_LABELS: Record<string, string> = {
  active: "فعال",
  suspended: "تعلیق",
  completed: "تکمیل شده",
  terminated: "فسخ",
};

export const STATUS_COLORS: Record<string, string> = {
  active: "bg-success-100 text-success-800",
  suspended: "bg-warning-100 text-warning-800",
  completed: "bg-info-100 text-info-800",
  terminated: "bg-danger-100 text-danger-800",
};

export const WARNING_TYPE_LABELS: Record<string, string> = {
  verbal: "تذکر شفاهی",
  written: "اخطار کتبی",
  final: "اخطار نهایی",
  contract_suspension: "تعلیق قرارداد",
};

export const WARNING_TYPE_COLORS: Record<string, string> = {
  verbal: "bg-neutral-100 text-neutral-700",
  written: "bg-warning-100 text-warning-800",
  final: "bg-danger-100 text-danger-800",
  contract_suspension: "bg-danger-200 text-danger-900",
};

export function scoreColor(score: number | null | undefined): string {
  if (score == null) return "text-muted-foreground";
  if (score >= 8) return "text-success-600";
  if (score >= 6) return "text-warning-600";
  return "text-danger-600";
}

export function scoreBg(score: number | null | undefined): string {
  if (score == null) return "";
  if (score >= 8) return "bg-success-50";
  if (score >= 6) return "bg-warning-50";
  return "bg-danger-50";
}

export function computeOverallLive(scores: Record<string, number | null>): number | null {
  const progress = scores.progress_score;
  const hse = scores.hse_score;
  if (progress == null || hse == null) return null;
  const weights: [number | null, number][] = [
    [progress, 0.3],
    [scores.quality_score, 0.25],
    [hse, 0.25],
    [scores.payment_compliance_score, 0.1],
    [scores.cooperation_score, 0.1],
  ];
  let sum = 0;
  let wTotal = 0;
  for (const [val, w] of weights) {
    if (val != null) {
      sum += val * w;
      wTotal += w;
    }
  }
  return wTotal > 0 ? Math.round((sum / wTotal) * 100) / 100 : null;
}
