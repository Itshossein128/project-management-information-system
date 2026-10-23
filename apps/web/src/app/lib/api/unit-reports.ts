/**
 * Typed canonical unit-report API client (feature 032, US1).
 * Not the legacy hr-forms helpers — this targets the canonical unit-report
 * contract under `/projects/{id}/units/{unit}/daily-reports/`.
 */
import { apiJson } from "@/app/lib/api-client";

export type CanonicalUnit =
  | "buildings"
  | "electrical"
  | "mechanical"
  | "machinery"
  | "warehouse"
  | "security";

export type UnitReportStatus = "draft" | "submitted" | "approved" | "rejected";

export interface UnitReportUserRef {
  id: string;
  display_name: string;
}

export interface UnitReportAudit {
  prepared_by: UnitReportUserRef | null;
  submitted_by: UnitReportUserRef | null;
  submitted_at: string | null;
  approved_by: UnitReportUserRef | null;
  approved_at: string | null;
  rejected_by: UnitReportUserRef | null;
  rejected_at: string | null;
  rejection_reason: string;
}

export interface UnitReportCapabilities {
  can_edit: boolean;
  can_submit: boolean;
  can_approve: boolean;
  can_reject: boolean;
  can_correct: boolean;
  can_delete: boolean;
  can_view_history: boolean;
}

export interface UnitReport {
  id: string;
  lineage_id: string;
  version_number: number;
  is_current: boolean;
  project_id: string;
  unit: CanonicalUnit;
  report_date: string;
  status: UnitReportStatus;
  last_changed_at: string | null;
  audit: UnitReportAudit;
  capabilities: UnitReportCapabilities;
  content: {
    activity_records: unknown[];
    legacy_contributions: unknown[];
  };
}

export interface UnitReportVersion {
  id: string;
  version_number: number;
  status: UnitReportStatus;
  is_current: boolean;
  created_at: string;
  supersedes: string | null;
  superseded_by: string | null;
}

export interface UnitReportEvent {
  event_type: string;
  from_status: string;
  to_status: string;
  actor: UnitReportUserRef | null;
  occurred_at: string;
  reason: string;
}

export interface UnitReportHistory {
  lineage_id: string;
  current_version_id: string;
  versions: UnitReportVersion[];
  events: UnitReportEvent[];
}

const base = (projectId: string, unit: CanonicalUnit) =>
  `/v1/projects/${projectId}/units/${unit}/daily-reports`;

export function fetchCurrentUnitReport(
  projectId: string,
  unit: CanonicalUnit,
  date: string,
): Promise<UnitReport> {
  return apiJson<UnitReport>(
    `${base(projectId, unit)}/current/?date=${encodeURIComponent(date)}`,
  );
}

export function openUnitReport(
  projectId: string,
  unit: CanonicalUnit,
  reportDate: string,
): Promise<UnitReport> {
  return apiJson<UnitReport>(`${base(projectId, unit)}/open/`, {
    method: "POST",
    body: JSON.stringify({ report_date: reportDate }),
  });
}

export function fetchUnitReport(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
): Promise<UnitReport> {
  return apiJson<UnitReport>(`${base(projectId, unit)}/${reportId}/`);
}

export function updateUnitReport(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
  patch: Record<string, unknown>,
): Promise<UnitReport> {
  return apiJson<UnitReport>(`${base(projectId, unit)}/${reportId}/`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
}

export function deleteUnitReport(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
): Promise<void> {
  return apiJson<void>(`${base(projectId, unit)}/${reportId}/`, {
    method: "DELETE",
  });
}

export function fetchUnitReportHistory(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
): Promise<UnitReportHistory> {
  return apiJson<UnitReportHistory>(`${base(projectId, unit)}/${reportId}/history/`);
}

function transition(projectId: string, unit: CanonicalUnit, reportId: string, action: string, body?: Record<string, unknown>): Promise<UnitReport> {
  return apiJson<UnitReport>(`${base(projectId, unit)}/${reportId}/${action}/`, {
    method: "POST",
    body: body ? JSON.stringify(body) : undefined,
  });
}

export const submitUnitReport = (p: string, u: CanonicalUnit, id: string) =>
  transition(p, u, id, "submit");

export const approveUnitReport = (p: string, u: CanonicalUnit, id: string) =>
  transition(p, u, id, "approve");

export const rejectUnitReport = (p: string, u: CanonicalUnit, id: string, rejectionReason: string) =>
  transition(p, u, id, "reject", { rejection_reason: rejectionReason });

export const correctUnitReport = (p: string, u: CanonicalUnit, id: string) =>
  transition(p, u, id, "correct");
