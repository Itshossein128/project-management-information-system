/**
 * Typed canonical unit-report API client (feature 032, US1).
 * Not the legacy hr-forms helpers — this targets the canonical unit-report
 * contract under `/projects/{id}/units/{unit}/daily-reports/`.
 */
import { apiFormData, apiJson, ApiRequestError } from "@/app/lib/api-client";

export type CanonicalUnit =
  | "buildings"
  | "electrical"
  | "mechanical"
  | "machinery"
  | "warehouse"
  | "security";

export const ACTIVITY_ENABLED_UNITS: readonly CanonicalUnit[] = [
  "buildings",
  "electrical",
  "mechanical",
] as const;

export function unitSupportsActivitiesSection(unit: CanonicalUnit | string): boolean {
  return (ACTIVITY_ENABLED_UNITS as readonly string[]).includes(unit);
}

export const LABOR_ENABLED_UNITS: readonly CanonicalUnit[] = [
  "buildings",
  "electrical",
  "mechanical",
] as const;

export function unitSupportsLaborSection(unit: CanonicalUnit | string): boolean {
  return (LABOR_ENABLED_UNITS as readonly string[]).includes(unit);
}

export const MACHINERY_ENABLED_UNITS: readonly CanonicalUnit[] = [
  "machinery",
] as const;

export function unitSupportsMachinerySection(unit: CanonicalUnit | string): boolean {
  return (MACHINERY_ENABLED_UNITS as readonly string[]).includes(unit);
}

export const MATERIALS_ENABLED_UNITS: readonly CanonicalUnit[] = [
  "warehouse",
] as const;

export function unitSupportsConcreteSection(unit: CanonicalUnit | string): boolean {
  return unit === "buildings" || unit === "mechanical";
}

export function unitSupportsGeneralSection(_unit: CanonicalUnit | string): boolean {
  return true;
}

export function unitSupportsIssuesSection(unit: CanonicalUnit | string): boolean {
  return ["buildings", "electrical", "mechanical", "security"].includes(unit);
}

export function unitSupportsVisitsSection(unit: CanonicalUnit | string): boolean {
  return unit === "buildings" || unit === "security";
}

export function unitSupportsHseSection(unit: CanonicalUnit | string): boolean {
  return unit === "security";
}

export function unitSupportsMaterialsSection(unit: CanonicalUnit | string): boolean {
  return (MATERIALS_ENABLED_UNITS as readonly string[]).includes(unit);
}

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

// ---------------------------------------------------------------------------
// Feature 033 §1 — Executed Activities Section CRUD & Validation Contract
// ---------------------------------------------------------------------------

export interface UnitReportActivityRow {
  id: string;
  row_number: number;
  shift: string;
  crew_name: string;
  foreman_count: number | null;
  worker_count: number | null;
  headcount: number | null;
  activity_ref: string;
  activity_code?: string | null;
  activity_name?: string | null;
  activity_description: string;
  contractor_ref: string;
  contractor_name?: string | null;
  parcel: string | null;
  zone: string | null;
  block: string | null;
  floor: string | null;
  quantity: string | null;
  unit: string | null;
  notes: string;
}

export interface UnitReportActivityPayload {
  row_number?: number;
  shift: string;
  crew_name?: string;
  foreman_count?: number | null;
  worker_count?: number | null;
  activity_ref: string | null;
  activity_description: string;
  contractor_ref: string | null;
  parcel?: string | null;
  zone?: string | null;
  block?: string | null;
  floor?: string | null;
  quantity?: string | number | null;
  unit?: string | null;
  notes?: string;
}

export interface SectionFieldError {
  row?: number;
  field: string | null;
  code: string;
  message: string;
}

export interface ParsedSectionError {
  topCode: string | null;
  topMessage: string;
  fieldErrors: Record<string, SectionFieldError[]>;
  allErrors: SectionFieldError[];
}

export function extractSectionErrors(err: unknown): ParsedSectionError {
  const fieldErrors: Record<string, SectionFieldError[]> = {};
  const allErrors: SectionFieldError[] = [];
  let topCode: string | null = null;
  let topMessage = err instanceof Error ? err.message : String(err);

  if (err instanceof ApiRequestError) {
    topCode = err.code ?? null;
    topMessage = err.message;
    const details = err.details as { errors?: unknown[] } | undefined;
    if (details && Array.isArray(details.errors)) {
      for (const item of details.errors) {
        if (item && typeof item === "object") {
          const raw = item as Record<string, unknown>;
          const code = typeof raw.code === "string" ? raw.code : topCode ?? "invalid";
          const field = typeof raw.field === "string" ? raw.field : null;
          const message = typeof raw.message === "string" ? raw.message : topMessage;
          const entry: SectionFieldError = {
            row: typeof raw.row === "number" ? raw.row : 0,
            field,
            code,
            message,
          };
          allErrors.push(entry);
          if (field) {
            if (!fieldErrors[field]) fieldErrors[field] = [];
            fieldErrors[field].push(entry);
          }
        }
      }
    }
    if (allErrors.length === 0 && topCode) {
      allErrors.push({
        field: null,
        code: topCode,
        message: topMessage,
      });
    }
  }

  return {
    topCode,
    topMessage,
    fieldErrors,
    allErrors,
  };
}

export function fetchUnitReportActivities(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
): Promise<UnitReportActivityRow[]> {
  return apiJson<UnitReportActivityRow[]>(
    `${base(projectId, unit)}/${reportId}/activities/`,
  );
}

export function createUnitReportActivity(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
  payload: UnitReportActivityPayload | UnitReportActivityPayload[],
): Promise<UnitReportActivityRow[]> {
  return apiJson<UnitReportActivityRow[]>(
    `${base(projectId, unit)}/${reportId}/activities/`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function updateUnitReportActivity(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
  rowId: string,
  payload: Partial<UnitReportActivityPayload>,
): Promise<UnitReportActivityRow> {
  return apiJson<UnitReportActivityRow>(
    `${base(projectId, unit)}/${reportId}/activities/${rowId}/`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
  );
}

export function deleteUnitReportActivity(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
  rowId: string,
): Promise<void> {
  return apiJson<void>(
    `${base(projectId, unit)}/${reportId}/activities/${rowId}/`,
    {
      method: "DELETE",
    },
  );
}

// ---------------------------------------------------------------------------
// Feature 033 §2 — Labor Section CRUD, Effective Catalog & Validation Contract
// ---------------------------------------------------------------------------

export type UnitLaborCategory = "indirect" | "direct";

export interface EffectiveLaborTitle {
  title_code: string;
  title_label: string;
  title_label_fa: string;
  category: UnitLaborCategory;
  display_order: number;
  legacy_alias?: string;
  source_catalog_version?: string;
}

export interface EffectiveReportingConfiguration {
  id?: string;
  project_id?: string;
  effective_from?: string;
  state?: string;
  required_units: string[];
  labor_titles?: EffectiveLaborTitle[];
  man_hours_rule?: {
    rule_code: string;
    parameters?: {
      standard_shift_hours?: string;
    };
  };
  stoppage_reasons?: Array<{
    reason_code: string;
    reason_label: string;
    reason_label_fa: string;
    display_order: number;
  }>;
}

export interface UnitReportLaborRow {
  id: string;
  labor_category: UnitLaborCategory;
  job_title: string;
  present_count: number;
  leave_count: number;
  overtime_hours: string;
  contractor_ref: string | null;
  contractor_name?: string | null;
  title_code: string;
  display_order: number;
}

export interface UnitReportLaborPayload {
  labor_category: string;
  job_title: string;
  custom_title?: string;
  present_count: number;
  leave_count: number;
  overtime_hours?: string | number;
  contractor_ref?: string | null;
}

export function fetchEffectiveReportingConfiguration(
  projectId: string,
  reportDate: string,
): Promise<EffectiveReportingConfiguration> {
  return apiJson<EffectiveReportingConfiguration>(
    `/api/v1/projects/${projectId}/reporting-configuration/?date=${encodeURIComponent(reportDate)}`,
  );
}

export function fetchUnitReportLabor(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
): Promise<UnitReportLaborRow[]> {
  return apiJson<UnitReportLaborRow[]>(
    `${base(projectId, unit)}/${reportId}/labor/`,
  );
}

export function createUnitReportLabor(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
  payload: UnitReportLaborPayload | UnitReportLaborPayload[],
): Promise<UnitReportLaborRow[]> {
  return apiJson<UnitReportLaborRow[]>(
    `${base(projectId, unit)}/${reportId}/labor/`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function updateUnitReportLabor(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
  rowId: string,
  payload: Partial<UnitReportLaborPayload>,
): Promise<UnitReportLaborRow> {
  return apiJson<UnitReportLaborRow>(
    `${base(projectId, unit)}/${reportId}/labor/${rowId}/`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
  );
}

export function deleteUnitReportLabor(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
  rowId: string,
): Promise<void> {
  return apiJson<void>(
    `${base(projectId, unit)}/${reportId}/labor/${rowId}/`,
    {
      method: "DELETE",
    },
  );
}

// ---------------------------------------------------------------------------
// Feature 033 §3 — Machinery Section CRUD & Validation Contract (T031)
// ---------------------------------------------------------------------------

export interface EffectiveStoppageReason {
  reason_code: string;
  reason_label: string;
  reason_label_fa: string;
  display_order?: number;
}

export interface UnitReportMachineryRow {
  id: string;
  row_number: number;
  equipment_type: string;
  equipment_ref: string | null;
  equipment_code?: string | null;
  equipment_name?: string | null;
  status_total: number;
  status_active: number;
  status_ready: number;
  status_inactive: number;
  status_under_repair: number;
  operating_hours: string | null;
  stoppage_hours: string | null;
  repair_hours: string | null;
  stoppage_reason_code: string;
  stoppage_reason_label?: string;
  stoppage_reason_label_fa?: string;
}

export interface UnitReportMachineryPayload {
  row_number?: number;
  equipment_type: string;
  equipment_ref?: string | null;
  status_total: number;
  status_active: number;
  status_ready: number;
  status_inactive: number;
  status_under_repair: number;
  operating_hours?: string | number | null;
  stoppage_hours?: string | number | null;
  repair_hours?: string | number | null;
  stoppage_reason_code?: string;
}

export function fetchUnitReportMachinery(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
): Promise<UnitReportMachineryRow[]> {
  return apiJson<UnitReportMachineryRow[]>(
    `${base(projectId, unit)}/${reportId}/machinery/`,
  );
}

export function createUnitReportMachinery(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
  payload: UnitReportMachineryPayload | UnitReportMachineryPayload[],
): Promise<UnitReportMachineryRow[]> {
  return apiJson<UnitReportMachineryRow[]>(
    `${base(projectId, unit)}/${reportId}/machinery/`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function updateUnitReportMachinery(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
  rowId: string,
  payload: Partial<UnitReportMachineryPayload>,
): Promise<UnitReportMachineryRow> {
  return apiJson<UnitReportMachineryRow>(
    `${base(projectId, unit)}/${reportId}/machinery/${rowId}/`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
  );
}

export function deleteUnitReportMachinery(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
  rowId: string,
): Promise<void> {
  return apiJson<void>(
    `${base(projectId, unit)}/${reportId}/machinery/${rowId}/`,
    {
      method: "DELETE",
    },
  );
}

// ---------------------------------------------------------------------------
// Feature 033 §4 — Materials Section CRUD & Validation Contract (T038)
// ---------------------------------------------------------------------------

export type UnitMaterialTransactionType = "receipt" | "consumption";
export type UnitMaterialReceiptEvidence =
  | "resolved"
  | "unresolved_reference"
  | null;

export interface UnitReportMaterialRow {
  id: string;
  transaction_type: UnitMaterialTransactionType;
  material_ref: string | null;
  material_code?: string | null;
  material_name?: string | null;
  material_description: string;
  quantity: string;
  unit: string;
  supplier: string;
  warehouse_document_reference: string;
  consumption_location: string;
  receipt_evidence?: UnitMaterialReceiptEvidence;
  receipt_resolved?: boolean;
}

export interface UnitReportMaterialPayload {
  transaction_type: UnitMaterialTransactionType;
  material_ref?: string | null;
  material_description: string;
  quantity: string | number;
  unit: string;
  supplier?: string;
  warehouse_document_reference?: string;
  consumption_location?: string;
}

export function fetchUnitReportMaterials(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
): Promise<UnitReportMaterialRow[]> {
  return apiJson<UnitReportMaterialRow[]>(
    `${base(projectId, unit)}/${reportId}/materials/`,
  );
}

export function createUnitReportMaterial(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
  payload: UnitReportMaterialPayload | UnitReportMaterialPayload[],
): Promise<UnitReportMaterialRow[]> {
  return apiJson<UnitReportMaterialRow[]>(
    `${base(projectId, unit)}/${reportId}/materials/`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function updateUnitReportMaterial(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
  rowId: string,
  payload: Partial<UnitReportMaterialPayload>,
): Promise<UnitReportMaterialRow> {
  return apiJson<UnitReportMaterialRow>(
    `${base(projectId, unit)}/${reportId}/materials/${rowId}/`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
  );
}

export interface UnitSectionRow {
  id: string;
  row_number?: number;
  text?: string;
  kind?: string;
  owner_user?: string | null;
  due_date?: string | null;
  severity?: string;
  immediate_action?: string;
  activity_description?: string;
  location?: string;
  quantity?: string | null;
  unit?: string | null;
  notes?: string;
  concrete_description?: string;
  volume_m3?: string;
  sampling_state?: string;
  lab_sample_code?: string;
  test_sheet_count?: number | null;
  batching_plant?: string;
  structural_element?: string;
  parcel?: string | null;
  zone?: string | null;
  block?: string | null;
  floor?: string | null;
  truck_delivery_note_number?: string;
}

export interface UnitReportAttachment {
  id: string;
  row_kind: string;
  row_id: string;
  declared_content_type?: string;
  size_bytes?: number | null;
  capture_date?: string | null;
  work_front?: string;
}

export function uploadUnitReportAttachment(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
  { file, rowId, captureDate, workFront }: {
    file: File;
    rowId: string;
    captureDate?: string;
    workFront?: string;
  },
): Promise<UnitReportAttachment> {
  const data = new FormData();
  data.append("file", file);
  data.append("row_id", rowId);
  data.append("declared_content_type", file.type);
  if (captureDate) data.append("capture_date", captureDate);
  if (workFront) data.append("work_front", workFront);
  return apiFormData<UnitReportAttachment>(`${base(projectId, unit)}/${reportId}/attachments/`, data);
}

export function fetchUnitSection(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
  section: string,
): Promise<UnitSectionRow[]> {
  return apiJson<UnitSectionRow[]>(`${base(projectId, unit)}/${reportId}/${section}/`);
}

export function createUnitSection(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
  section: string,
  payload: Record<string, unknown>,
): Promise<UnitSectionRow[]> {
  return apiJson<UnitSectionRow[]>(`${base(projectId, unit)}/${reportId}/${section}/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function deleteUnitSection(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
  section: string,
  rowId: string,
): Promise<void> {
  return apiJson<void>(`${base(projectId, unit)}/${reportId}/${section}/${rowId}/`, {
    method: "DELETE",
  });
}

export function deleteUnitReportMaterial(
  projectId: string,
  unit: CanonicalUnit,
  reportId: string,
  rowId: string,
): Promise<void> {
  return apiJson<void>(
    `${base(projectId, unit)}/${reportId}/materials/${rowId}/`,
    {
      method: "DELETE",
    },
  );
}
