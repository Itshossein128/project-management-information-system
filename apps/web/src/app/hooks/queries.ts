import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiJson, ApiRequestError } from "@/app/lib/api-client";
import type {
  Business,
  BusinessJobPosition,
  DepartmentActivityRecord,
  DepartmentActivityRecordListParams,
  DepartmentActivityRecordPayload,
  ListResponse,
  UserBusinessAssignment,
} from "@/app/lib/api-types";
import {
  type CanonicalUnit,
  type UnitReport,
  type UnitReportHistory,
  type UnitReportActivityRow,
  type UnitReportActivityPayload,
  fetchCurrentUnitReport,
  openUnitReport,
  submitUnitReport,
  approveUnitReport,
  rejectUnitReport,
  correctUnitReport,
  deleteUnitReport,
  fetchUnitReportHistory,
  fetchUnitReportActivities,
  createUnitReportActivity,
  updateUnitReportActivity,
  deleteUnitReportActivity,
  type UnitReportLaborRow,
  type UnitReportLaborPayload,
  type EffectiveReportingConfiguration,
  fetchEffectiveReportingConfiguration,
  fetchUnitReportLabor,
  createUnitReportLabor,
  updateUnitReportLabor,
  deleteUnitReportLabor,
  type UnitReportMachineryRow,
  type UnitReportMachineryPayload,
  fetchUnitReportMachinery,
  createUnitReportMachinery,
  updateUnitReportMachinery,
  deleteUnitReportMachinery,
  type UnitReportMaterialRow,
  type UnitReportMaterialPayload,
  fetchUnitReportMaterials,
  createUnitReportMaterial,
  updateUnitReportMaterial,
  deleteUnitReportMaterial,
} from "@/app/lib/api/unit-reports";
import {
  findLocalSnapshot,
  generateUUID,
  getLocalSnapshot,
} from "@/app/lib/offlineDB";
import { reconcileServerWithLocalSnapshot } from "@/app/lib/offlineHydration";
import { queueUnitReportOperation } from "@/app/lib/offlineWrite";
import { queryKeys } from "@/app/lib/react-query-keys";
import { PATHS } from "@/app/routeVars";

export interface HrUserRow {
  id: number;
  phone_number: string;
  first_name: string;
  last_name: string;
  full_name: string;
  created_at: string;
  is_active: boolean;
  roles: string[];
  assignments_preview?: UserBusinessAssignment[];
}

export function useBusinessesQuery(enabled = true) {
  return useQuery({
    queryKey: queryKeys.businesses(),
    enabled,
    queryFn: () => apiJson<ListResponse<Business>>(`/${PATHS.API_PROJECTS}/`),
  });
}

export function useHrUsersQuery(
  params: { page: number; page_size?: number; search?: string; ordering?: string },
  enabled = true,
) {
  return useQuery({
    queryKey: queryKeys.authUsers(params),
    enabled,
    queryFn: () =>
      apiJson<ListResponse<HrUserRow>>(
        `/${PATHS.API_AUTH_USERS}/?${new URLSearchParams({
          page: String(params.page),
          ...(params.page_size ? { page_size: String(params.page_size) } : {}),
          ...(params.search ? { search: params.search } : {}),
          ...(params.ordering ? { ordering: params.ordering } : {}),
        }).toString()}`,
      ),
  });
}

export interface CreateHrUserPayload {
  phone_number: string;
  first_name: string;
  last_name: string;
  password: string;
  password_confirm: string;
}

export function useCreateHrUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateHrUserPayload) =>
      apiJson<{ id: number }>(`/${PATHS.API_AUTH_USERS}/`, {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["auth", "users"] });
    },
  });
}

export function useJobPositionsForBusiness(businessId: number | string, enabled = true) {
  return useJobPositionsForBusinessQuery(businessId, {}, enabled);
}

export function useAssignmentsForBusiness(businessId: number | string, enabled = true) {
  return useAssignmentsForBusinessQuery(businessId, {}, enabled);
}

export function useJobPositionsForBusinessQuery(
  businessId: number | string,
  params: { page?: number; page_size?: number; search?: string; ordering?: string } = {},
  enabled = true,
) {
  return useQuery({
    queryKey: queryKeys.businessJobPositions(businessId, params),
    enabled,
    queryFn: () =>
      apiJson<ListResponse<BusinessJobPosition>>(
        `/${PATHS.API_PROJECTS}/${businessId}/positions/?${new URLSearchParams({
          ...(params.page ? { page: String(params.page) } : {}),
          ...(params.page_size ? { page_size: String(params.page_size) } : {}),
          ...(params.search ? { search: params.search } : {}),
          ...(params.ordering ? { ordering: params.ordering } : {}),
        }).toString()}`,
      ),
  });
}

export function useAssignmentsForBusinessQuery(
  businessId: number | string,
  params: { page?: number; page_size?: number; search?: string; ordering?: string } = {},
  enabled = true,
) {
  return useQuery({
    queryKey: queryKeys.businessAssignments(businessId, params),
    enabled,
    queryFn: () =>
      apiJson<ListResponse<UserBusinessAssignment>>(
        `/${PATHS.API_PROJECTS}/${businessId}/members/?${new URLSearchParams({
          ...(params.page ? { page: String(params.page) } : {}),
          ...(params.page_size ? { page_size: String(params.page_size) } : {}),
          ...(params.search ? { search: params.search } : {}),
          ...(params.ordering ? { ordering: params.ordering } : {}),
        }).toString()}`,
      ),
  });
}

export function useCreateJobPosition(businessId: number | string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Partial<BusinessJobPosition>) =>
      apiJson<BusinessJobPosition>(`/${PATHS.API_PROJECTS}/${businessId}/positions/`, {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.businessJobPositions(businessId) });
    },
  });
}

export function useUpdateJobPosition(businessId: number | string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (args: { id: number | string; patch: Partial<BusinessJobPosition> }) =>
      apiJson<BusinessJobPosition>(
        `/${PATHS.API_PROJECTS}/${businessId}/positions/${args.id}/`,
        {
          method: "PATCH",
          body: JSON.stringify(args.patch),
        },
      ),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.businessJobPositions(businessId) });
    },
  });
}

export function useDeleteJobPosition(businessId: number | string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number | string) =>
      apiJson<{ ok?: boolean }>(`/${PATHS.API_PROJECTS}/${businessId}/positions/${id}/`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.businessJobPositions(businessId) });
    },
  });
}

export function useCreateAssignment(businessId: number | string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Partial<UserBusinessAssignment>) =>
      apiJson<UserBusinessAssignment>(`/${PATHS.API_PROJECTS}/${businessId}/members/`, {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.businessAssignments(businessId) });
    },
  });
}

export function useUpdateAssignment(businessId: number | string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (args: { id: number | string; patch: Partial<UserBusinessAssignment> }) =>
      apiJson<UserBusinessAssignment>(
        `/${PATHS.API_PROJECTS}/${businessId}/members/${args.id}/`,
        {
          method: "PATCH",
          body: JSON.stringify(args.patch),
        },
      ),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.businessAssignments(businessId) });
    },
  });
}

export function useDeleteAssignment(businessId: number | string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number | string) =>
      apiJson<{ ok?: boolean }>(`/${PATHS.API_PROJECTS}/${businessId}/members/${id}/`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.businessAssignments(businessId) });
    },
  });
}

const DEPARTMENT_ACTIVITY_RECORDS_PATH = "department-activity-records";

function buildDepartmentActivityRecordsSearch(
  params: DepartmentActivityRecordListParams,
): string {
  const sp = new URLSearchParams();
  sp.set("department", params.department);
  if (params.page) sp.set("page", String(params.page));
  if (params.page_size) sp.set("page_size", String(params.page_size));
  if (params.search) sp.set("search", params.search);
  if (params.ordering) sp.set("ordering", params.ordering);
  if (params.date_from) sp.set("date_from", params.date_from);
  if (params.date_to) sp.set("date_to", params.date_to);
  if (params.location) sp.set("location", params.location);
  if (params.activity_description)
    sp.set("activity_description", params.activity_description);
  if (params.contractor) sp.set("contractor", params.contractor);
  if (params.unit) sp.set("unit", params.unit);
  if (params.material_type) sp.set("material_type", params.material_type);
  if (params.consumption_location)
    sp.set("consumption_location", params.consumption_location);
  if (params.supplier) sp.set("supplier", params.supplier);
  return sp.toString();
}

export function useDepartmentActivityRecordsQuery(
  businessId: number | string,
  params: DepartmentActivityRecordListParams,
  enabled = true,
) {
  return useQuery({
    queryKey: queryKeys.departmentActivityRecords(
      businessId,
      params.department,
      params as unknown as Record<string, unknown>,
    ),
    enabled,
    queryFn: () =>
      apiJson<ListResponse<DepartmentActivityRecord>>(
        `/${PATHS.API_PROJECTS}/${businessId}/${DEPARTMENT_ACTIVITY_RECORDS_PATH}/?${buildDepartmentActivityRecordsSearch(params)}`,
      ),
  });
}

export function useCreateDepartmentActivityRecord(businessId: number | string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: DepartmentActivityRecordPayload) =>
      apiJson<DepartmentActivityRecord>(
        `/${PATHS.API_PROJECTS}/${businessId}/${DEPARTMENT_ACTIVITY_RECORDS_PATH}/`,
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
      ),
    onSuccess: (record) => {
      void qc.invalidateQueries({
        queryKey: queryKeys.departmentActivityRecords(
          businessId,
          record.department,
        ),
      });
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", record.department],
      });
    },
  });
}

export function useUpdateDepartmentActivityRecord(
  businessId: number | string,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (args: {
      id: number | string;
      patch: Partial<DepartmentActivityRecordPayload>;
    }) =>
      apiJson<DepartmentActivityRecord>(
        `/${PATHS.API_PROJECTS}/${businessId}/${DEPARTMENT_ACTIVITY_RECORDS_PATH}/${args.id}/`,
        {
          method: "PATCH",
          body: JSON.stringify(args.patch),
        },
      ),
    onSuccess: (record) => {
      void qc.invalidateQueries({
        queryKey: queryKeys.departmentActivityRecords(
          businessId,
          record.department,
        ),
      });
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", record.department],
      });
    },
  });
}

export function useDeleteDepartmentActivityRecord(
  businessId: number | string,
  department: string,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number | string) =>
      apiJson<{ ok?: boolean }>(
        `/${PATHS.API_PROJECTS}/${businessId}/${DEPARTMENT_ACTIVITY_RECORDS_PATH}/${id}/`,
        {
          method: "DELETE",
        },
      ),
    onSuccess: () => {
      void qc.invalidateQueries({
        queryKey: queryKeys.departmentActivityRecords(businessId, department),
      });
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", department],
      });
    },
  });
}

/**
 * Returns whether activity row mutation is permitted for the given report state.
 * Mutations are only permitted when no report exists yet or the report is draft / rejected.
 */
export function isUnitReportEditable(report: UnitReport | null | undefined): boolean {
  if (!report) return true;
  return report.status === "draft" || report.status === "rejected";
}

export function useCurrentUnitReportQuery(
  businessId: number | string | undefined,
  unit: CanonicalUnit | string | undefined,
  date: string | undefined,
  enabled = true,
) {
  return useQuery<UnitReport | null>({
    queryKey: queryKeys.unitReportCurrent(businessId ?? "", unit ?? "", date ?? ""),
    enabled: Boolean(enabled && businessId && unit && date),
    queryFn: async () => {
      const isOffline = typeof navigator !== "undefined" && !navigator.onLine;
      if (isOffline) {
        const local = await findLocalSnapshot(String(businessId), String(unit), date!);
        if (local) {
          return {
            id: local.local_report_id,
            project_id: local.project_id,
            unit: local.unit as CanonicalUnit,
            report_date: local.report_date,
            status: local.status as any,
            version_number: local.server_version ?? 1,
            is_current: true,
            notes: (local.overlay_header?.notes ?? local.base_header?.notes ?? (local as any).notes ?? "") as string,
            form_code: (local.overlay_header?.form_code ?? local.base_header?.form_code ?? "") as string,
            weather_condition: (local.overlay_header?.weather_condition ?? local.base_header?.weather_condition ?? null) as any,
            site_status: (local.overlay_header?.site_status ?? local.base_header?.site_status ?? "active") as any,
            audit: {
              prepared_by: null,
              submitted_by: null,
              submitted_at: null,
              approved_by: null,
              approved_at: null,
              rejected_by: null,
              rejected_at: null,
              rejection_reason: "",
            },
            capabilities: {
              can_edit: true,
              can_submit: false,
              can_approve: false,
              can_reject: false,
              can_correct: false,
              can_delete: true,
              can_view_history: false,
            },
            content: {
              activity_records: [],
              legacy_contributions: [],
            },
            _offline: true,
          } as unknown as UnitReport;
        }
        return null;
      }
      try {
        const serverReport = await fetchCurrentUnitReport(
          String(businessId),
          unit as CanonicalUnit,
          date!,
        );
        if (serverReport) {
          const local = await findLocalSnapshot(String(businessId), String(unit), date!);
          if (local && (Object.keys(local.overlay_header || {}).length > 0 || Object.keys(local.overlay_rows || {}).length > 0)) {
            return {
              ...serverReport,
              notes: (local.overlay_header?.notes ?? serverReport.notes) as string,
              form_code: (local.overlay_header?.form_code ?? serverReport.form_code) as string,
              weather_condition: (local.overlay_header?.weather_condition ?? serverReport.weather_condition) as any,
              site_status: (local.overlay_header?.site_status ?? serverReport.site_status) as any,
              _offline: true,
            };
          }
        }
        return serverReport;
      } catch (err) {
        const local = await findLocalSnapshot(String(businessId), String(unit), date!);
        if (local) {
          return {
            id: local.local_report_id,
            project_id: local.project_id,
            unit: local.unit as CanonicalUnit,
            report_date: local.report_date,
            status: local.status as any,
            version_number: local.server_version ?? 1,
            is_current: true,
            notes: (local.overlay_header?.notes ?? local.base_header?.notes ?? (local as any).notes ?? "") as string,
            form_code: (local.overlay_header?.form_code ?? local.base_header?.form_code ?? "") as string,
            weather_condition: (local.overlay_header?.weather_condition ?? local.base_header?.weather_condition ?? null) as any,
            site_status: (local.overlay_header?.site_status ?? local.base_header?.site_status ?? "active") as any,
            audit: {
              prepared_by: null,
              submitted_by: null,
              submitted_at: null,
              approved_by: null,
              approved_at: null,
              rejected_by: null,
              rejected_at: null,
              rejection_reason: "",
            },
            capabilities: {
              can_edit: true,
              can_submit: false,
              can_approve: false,
              can_reject: false,
              can_correct: false,
              can_delete: true,
              can_view_history: false,
            },
            content: {
              activity_records: [],
              legacy_contributions: [],
            },
            _offline: true,
          } as unknown as UnitReport;
        }
        if (err instanceof ApiRequestError && err.status === 404) {
          return null;
        }
        throw err;
      }
    },
  });
}

export function useOpenUnitReport(
  businessId: number | string,
  unit: CanonicalUnit,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (reportDate: string) => {
      const isOffline = typeof navigator !== "undefined" && !navigator.onLine;
      if (isOffline) {
        let existing = await findLocalSnapshot(String(businessId), unit, reportDate);
        if (!existing) {
          const localId = generateUUID();
          const { snapshot } = await queueUnitReportOperation({
            actorId: localStorage.getItem("auth_user_id") ?? "offline-user",
            projectId: String(businessId),
            unit,
            reportDate,
            localReportId: localId,
            operationKind: "create_report",
            targetType: "header",
            payload: { form_code: "" },
          });
          existing = snapshot;
        }
        return {
          id: existing.local_report_id,
          project_id: existing.project_id,
          unit: existing.unit as CanonicalUnit,
          report_date: existing.report_date,
          status: existing.status as any,
          version_number: existing.server_version ?? 1,
          is_current: true,
          form_code: (existing.overlay_header?.form_code ?? existing.base_header?.form_code ?? "") as string,
          audit: {
            prepared_by: null,
            submitted_by: null,
            submitted_at: null,
            approved_by: null,
            approved_at: null,
            rejected_by: null,
            rejected_at: null,
            rejection_reason: "",
          },
          capabilities: {
            can_edit: true,
            can_submit: false,
            can_approve: false,
            can_reject: false,
            can_correct: false,
            can_delete: true,
            can_view_history: false,
          },
          content: {
            activity_records: [],
            legacy_contributions: [],
          },
          _offline: true,
        } as unknown as UnitReport;
      }
      return openUnitReport(String(businessId), unit, reportDate);
    },
    onSuccess: () => {
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", unit],
      });
      void qc.invalidateQueries({
        queryKey: queryKeys.departmentActivityRecords(businessId, unit),
      });
    },
  });
}

export function useSubmitUnitReport(
  businessId: number | string,
  unit: CanonicalUnit,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (reportId: string) =>
      submitUnitReport(String(businessId), unit, reportId),
    onSuccess: () => {
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", unit],
      });
      void qc.invalidateQueries({
        queryKey: queryKeys.departmentActivityRecords(businessId, unit),
      });
    },
  });
}

export function useApproveUnitReport(
  businessId: number | string,
  unit: CanonicalUnit,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (reportId: string) =>
      approveUnitReport(String(businessId), unit, reportId),
    onSuccess: () => {
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", unit],
      });
      void qc.invalidateQueries({
        queryKey: queryKeys.departmentActivityRecords(businessId, unit),
      });
    },
  });
}

export function useRejectUnitReport(
  businessId: number | string,
  unit: CanonicalUnit,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ reportId, reason }: { reportId: string; reason: string }) =>
      rejectUnitReport(String(businessId), unit, reportId, reason),
    onSuccess: () => {
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", unit],
      });
      void qc.invalidateQueries({
        queryKey: queryKeys.departmentActivityRecords(businessId, unit),
      });
    },
  });
}

export function useCorrectUnitReport(
  businessId: number | string,
  unit: CanonicalUnit,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (reportId: string) =>
      correctUnitReport(String(businessId), unit, reportId),
    onSuccess: () => {
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", unit],
      });
      void qc.invalidateQueries({
        queryKey: queryKeys.departmentActivityRecords(businessId, unit),
      });
    },
  });
}

export function useDeleteUnitReport(
  businessId: number | string,
  unit: CanonicalUnit,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ reportId }: { reportId: string; date: string }) =>
      deleteUnitReport(String(businessId), unit, reportId),
    onSuccess: () => {
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", unit],
      });
      void qc.invalidateQueries({
        queryKey: queryKeys.departmentActivityRecords(businessId, unit),
      });
    },
  });
}

export function useUnitReportHistoryQuery(
  businessId: number | string | undefined,
  unit: CanonicalUnit | string | undefined,
  reportId: string | undefined,
  enabled = true,
) {
  return useQuery<UnitReportHistory>({
    queryKey: queryKeys.unitReportHistory(businessId ?? "", unit ?? "", reportId ?? ""),
    enabled: Boolean(enabled && businessId && unit && reportId),
    queryFn: () =>
      fetchUnitReportHistory(
        String(businessId),
        unit as CanonicalUnit,
        reportId!,
      ),
  });
}

export function useUnitReportActivitiesQuery(
  businessId: number | string | undefined,
  unit: CanonicalUnit | string | undefined,
  reportId: string | undefined,
  enabled = true,
) {
  return useQuery<UnitReportActivityRow[]>({
    queryKey: queryKeys.unitReportActivities(businessId ?? "", unit ?? "", reportId ?? ""),
    enabled: Boolean(enabled && businessId && unit && reportId),
    queryFn: async () => {
      const isOffline = typeof navigator !== "undefined" && !navigator.onLine;
      if (isOffline && reportId) {
        const local = await getLocalSnapshot(reportId);
        if (local) {
          const base = (local.base_rows?.activities ?? []) as UnitReportActivityRow[];
          return reconcileServerWithLocalSnapshot({}, base, local, "activities").rows as UnitReportActivityRow[];
        }
      }
      try {
        const rows = await fetchUnitReportActivities(
          String(businessId),
          unit as CanonicalUnit,
          reportId!,
        );
        if (reportId) {
          const local = await getLocalSnapshot(reportId);
          if (local) {
            return reconcileServerWithLocalSnapshot({}, rows, local, "activities").rows as UnitReportActivityRow[];
          }
        }
        return rows.map((r) => ({ ...r, sync_status: (r as any).sync_status ?? "synced" }));
      } catch (err) {
        if (reportId) {
          const local = await getLocalSnapshot(reportId);
          if (local) {
            const base = (local.base_rows?.activities ?? []) as UnitReportActivityRow[];
            return reconcileServerWithLocalSnapshot({}, base, local, "activities").rows as UnitReportActivityRow[];
          }
        }
        throw err;
      }
    },
  });
}

export function useCreateUnitReportActivity(
  businessId: number | string,
  unit: CanonicalUnit,
  reportId: string | undefined,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: UnitReportActivityPayload) => {
      if (!reportId) throw new Error("Missing reportId");
      const isOffline = typeof navigator !== "undefined" && !navigator.onLine;
      if (isOffline) {
        const actorId = localStorage.getItem("auth_user_id") ?? "offline-user";
        const { operation } = await queueUnitReportOperation({
          actorId,
          projectId: String(businessId),
          unit,
          reportDate: "",
          localReportId: reportId,
          operationKind: "create",
          targetType: "activities",
          payload: payload as unknown as Record<string, unknown>,
        });
        return [{
          ...payload,
          id: operation.client_id,
          client_id: operation.client_id,
          _offline: true,
          status: "pending",
        }] as unknown as UnitReportActivityRow[];
      }
      return createUnitReportActivity(String(businessId), unit, reportId, payload);
    },
    onSuccess: () => {
      if (reportId) {
        void qc.invalidateQueries({
          queryKey: queryKeys.unitReportActivities(businessId, unit, reportId),
        });
      }
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", unit],
      });
    },
  });
}

export function useUpdateUnitReportActivity(
  businessId: number | string,
  unit: CanonicalUnit,
  reportId: string | undefined,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({
      rowId,
      patch,
    }: {
      rowId: string;
      patch: Partial<UnitReportActivityPayload>;
    }) => {
      if (!reportId) throw new Error("Missing reportId");
      const isOffline = typeof navigator !== "undefined" && !navigator.onLine;
      if (isOffline) {
        const actorId = localStorage.getItem("auth_user_id") ?? "offline-user";
        await queueUnitReportOperation({
          actorId,
          projectId: String(businessId),
          unit,
          reportDate: "",
          localReportId: reportId,
          clientId: rowId,
          targetServerId: rowId,
          operationKind: "update",
          targetType: "activities",
          payload: patch as unknown as Record<string, unknown>,
        });
        return {
          ...patch,
          id: rowId,
          _offline: true,
          status: "pending",
        } as unknown as UnitReportActivityRow;
      }
      return updateUnitReportActivity(
        String(businessId),
        unit,
        reportId,
        rowId,
        patch,
      );
    },
    onSuccess: () => {
      if (reportId) {
        void qc.invalidateQueries({
          queryKey: queryKeys.unitReportActivities(businessId, unit, reportId),
        });
      }
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", unit],
      });
    },
  });
}

export function useDeleteUnitReportActivity(
  businessId: number | string,
  unit: CanonicalUnit,
  reportId: string | undefined,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (rowId: string) => {
      if (!reportId) throw new Error("Missing reportId");
      const isOffline = typeof navigator !== "undefined" && !navigator.onLine;
      if (isOffline) {
        const actorId = localStorage.getItem("auth_user_id") ?? "offline-user";
        await queueUnitReportOperation({
          actorId,
          projectId: String(businessId),
          unit,
          reportDate: "",
          localReportId: reportId,
          clientId: rowId,
          targetServerId: rowId,
          operationKind: "delete",
          targetType: "activities",
          payload: {},
        });
        return;
      }
      return deleteUnitReportActivity(String(businessId), unit, reportId, rowId);
    },
    onSuccess: () => {
      if (reportId) {
        void qc.invalidateQueries({
          queryKey: queryKeys.unitReportActivities(businessId, unit, reportId),
        });
      }
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", unit],
      });
    },
  });
}

// ---------------------------------------------------------------------------
// Feature 033 §2 — Labor Section & Effective Reporting Configuration Queries
// ---------------------------------------------------------------------------

export function useEffectiveReportingConfigurationQuery(
  businessId: number | string | undefined,
  reportDate: string | undefined,
) {
  return useQuery<EffectiveReportingConfiguration>({
    queryKey: queryKeys.effectiveReportingConfiguration(
      businessId ?? "",
      reportDate ?? "",
    ),
    queryFn: () => {
      if (!businessId || !reportDate) {
        throw new Error("Missing businessId or reportDate");
      }
      return fetchEffectiveReportingConfiguration(String(businessId), reportDate);
    },
    enabled: Boolean(businessId && reportDate),
    retry: false,
  });
}

export function useUnitReportLaborQuery(
  businessId: number | string | undefined,
  unit: CanonicalUnit,
  reportId: string | undefined,
) {
  return useQuery<UnitReportLaborRow[]>({
    queryKey: queryKeys.unitReportLabor(businessId ?? "", unit, reportId ?? ""),
    queryFn: async () => {
      if (!businessId || !reportId) {
        throw new Error("Missing unit report labor parameters");
      }
      const isOffline = typeof navigator !== "undefined" && !navigator.onLine;
      if (isOffline) {
        const local = await getLocalSnapshot(reportId);
        if (local) {
          const base = (local.base_rows?.labor ?? []) as UnitReportLaborRow[];
          return reconcileServerWithLocalSnapshot({}, base, local, "labor").rows as UnitReportLaborRow[];
        }
      }
      try {
        const rows = await fetchUnitReportLabor(String(businessId), unit, reportId);
        const local = await getLocalSnapshot(reportId);
        if (local) {
          return reconcileServerWithLocalSnapshot({}, rows, local, "labor").rows as UnitReportLaborRow[];
        }
        return rows.map((r) => ({ ...r, sync_status: (r as any).sync_status ?? "synced" }));
      } catch (err) {
        const local = await getLocalSnapshot(reportId);
        if (local) {
          const base = (local.base_rows?.labor ?? []) as UnitReportLaborRow[];
          return reconcileServerWithLocalSnapshot({}, base, local, "labor").rows as UnitReportLaborRow[];
        }
        throw err;
      }
    },
    enabled: Boolean(businessId && reportId),
  });
}

export function useCreateUnitReportLabor(
  businessId: number | string,
  unit: CanonicalUnit,
  reportId: string | undefined,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: UnitReportLaborPayload) => {
      if (!reportId) throw new Error("Missing reportId");
      const isOffline = typeof navigator !== "undefined" && !navigator.onLine;
      if (isOffline) {
        const actorId = localStorage.getItem("auth_user_id") ?? "offline-user";
        const { operation } = await queueUnitReportOperation({
          actorId,
          projectId: String(businessId),
          unit,
          reportDate: "",
          localReportId: reportId,
          operationKind: "create",
          targetType: "labor",
          payload: payload as unknown as Record<string, unknown>,
        });
        return [{
          ...payload,
          id: operation.client_id,
          client_id: operation.client_id,
          _offline: true,
          status: "pending",
        }] as unknown as UnitReportLaborRow[];
      }
      return createUnitReportLabor(String(businessId), unit, reportId, payload);
    },
    onSuccess: () => {
      if (reportId) {
        void qc.invalidateQueries({
          queryKey: queryKeys.unitReportLabor(businessId, unit, reportId),
        });
      }
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", unit],
      });
    },
  });
}

export function useUpdateUnitReportLabor(
  businessId: number | string,
  unit: CanonicalUnit,
  reportId: string | undefined,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({
      rowId,
      patch,
    }: {
      rowId: string;
      patch: Partial<UnitReportLaborPayload>;
    }) => {
      if (!reportId) throw new Error("Missing reportId");
      const isOffline = typeof navigator !== "undefined" && !navigator.onLine;
      if (isOffline) {
        const actorId = localStorage.getItem("auth_user_id") ?? "offline-user";
        await queueUnitReportOperation({
          actorId,
          projectId: String(businessId),
          unit,
          reportDate: "",
          localReportId: reportId,
          clientId: rowId,
          targetServerId: rowId,
          operationKind: "update",
          targetType: "labor",
          payload: patch as unknown as Record<string, unknown>,
        });
        return {
          ...patch,
          id: rowId,
          _offline: true,
          status: "pending",
        } as unknown as UnitReportLaborRow;
      }
      return updateUnitReportLabor(
        String(businessId),
        unit,
        reportId,
        rowId,
        patch,
      );
    },
    onSuccess: () => {
      if (reportId) {
        void qc.invalidateQueries({
          queryKey: queryKeys.unitReportLabor(businessId, unit, reportId),
        });
      }
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", unit],
      });
    },
  });
}

export function useDeleteUnitReportLabor(
  businessId: number | string,
  unit: CanonicalUnit,
  reportId: string | undefined,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (rowId: string) => {
      if (!reportId) throw new Error("Missing reportId");
      const isOffline = typeof navigator !== "undefined" && !navigator.onLine;
      if (isOffline) {
        const actorId = localStorage.getItem("auth_user_id") ?? "offline-user";
        await queueUnitReportOperation({
          actorId,
          projectId: String(businessId),
          unit,
          reportDate: "",
          localReportId: reportId,
          clientId: rowId,
          targetServerId: rowId,
          operationKind: "delete",
          targetType: "labor",
          payload: {},
        });
        return;
      }
      return deleteUnitReportLabor(String(businessId), unit, reportId, rowId);
    },
    onSuccess: () => {
      if (reportId) {
        void qc.invalidateQueries({
          queryKey: queryKeys.unitReportLabor(businessId, unit, reportId),
        });
      }
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", unit],
      });
    },
  });
}

// ---------------------------------------------------------------------------
// Feature 033 §3 — Machinery Section Queries (T031)
// ---------------------------------------------------------------------------

export function useUnitReportMachineryQuery(
  businessId: number | string | undefined,
  unit: CanonicalUnit,
  reportId: string | undefined,
) {
  return useQuery<UnitReportMachineryRow[]>({
    queryKey: queryKeys.unitReportMachinery(businessId ?? "", unit, reportId ?? ""),
    queryFn: async () => {
      if (!businessId || !reportId) {
        throw new Error("Missing unit report machinery parameters");
      }
      const isOffline = typeof navigator !== "undefined" && !navigator.onLine;
      if (isOffline) {
        const local = await getLocalSnapshot(reportId);
        if (local) {
          const base = (local.base_rows?.machinery ?? []) as UnitReportMachineryRow[];
          return reconcileServerWithLocalSnapshot({}, base, local, "machinery").rows as UnitReportMachineryRow[];
        }
      }
      try {
        const rows = await fetchUnitReportMachinery(String(businessId), unit, reportId);
        const local = await getLocalSnapshot(reportId);
        if (local) {
          return reconcileServerWithLocalSnapshot({}, rows, local, "machinery").rows as UnitReportMachineryRow[];
        }
        return rows.map((row) => ({ ...row, sync_status: (row as { sync_status?: string }).sync_status ?? "synced" }));
      } catch (err) {
        const local = await getLocalSnapshot(reportId);
        if (local) {
          const base = (local.base_rows?.machinery ?? []) as UnitReportMachineryRow[];
          return reconcileServerWithLocalSnapshot({}, base, local, "machinery").rows as UnitReportMachineryRow[];
        }
        throw err;
      }
    },
    enabled: Boolean(businessId && reportId),
  });
}

export function useCreateUnitReportMachinery(
  businessId: number | string,
  unit: CanonicalUnit,
  reportId: string | undefined,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: UnitReportMachineryPayload) => {
      if (!reportId) throw new Error("Missing reportId");
      return createUnitReportMachinery(String(businessId), unit, reportId, payload);
    },
    onSuccess: () => {
      if (reportId) {
        void qc.invalidateQueries({
          queryKey: queryKeys.unitReportMachinery(businessId, unit, reportId),
        });
      }
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", unit],
      });
    },
  });
}

export function useUpdateUnitReportMachinery(
  businessId: number | string,
  unit: CanonicalUnit,
  reportId: string | undefined,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      rowId,
      patch,
    }: {
      rowId: string;
      patch: Partial<UnitReportMachineryPayload>;
    }) => {
      if (!reportId) throw new Error("Missing reportId");
      return updateUnitReportMachinery(
        String(businessId),
        unit,
        reportId,
        rowId,
        patch,
      );
    },
    onSuccess: () => {
      if (reportId) {
        void qc.invalidateQueries({
          queryKey: queryKeys.unitReportMachinery(businessId, unit, reportId),
        });
      }
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", unit],
      });
    },
  });
}

export function useDeleteUnitReportMachinery(
  businessId: number | string,
  unit: CanonicalUnit,
  reportId: string | undefined,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (rowId: string) => {
      if (!reportId) throw new Error("Missing reportId");
      return deleteUnitReportMachinery(String(businessId), unit, reportId, rowId);
    },
    onSuccess: () => {
      if (reportId) {
        void qc.invalidateQueries({
          queryKey: queryKeys.unitReportMachinery(businessId, unit, reportId),
        });
      }
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", unit],
      });
    },
  });
}

// ---------------------------------------------------------------------------
// Feature 033 §4 — Materials Section Queries (T038)
// ---------------------------------------------------------------------------

export function useUnitReportMaterialsQuery(
  businessId: number | string | undefined,
  unit: CanonicalUnit,
  reportId: string | undefined,
) {
  return useQuery<UnitReportMaterialRow[]>({
    queryKey: queryKeys.unitReportMaterials(businessId ?? "", unit, reportId ?? ""),
    queryFn: async () => {
      if (!businessId || !reportId) {
        throw new Error("Missing unit report materials parameters");
      }
      const isOffline = typeof navigator !== "undefined" && !navigator.onLine;
      if (isOffline) {
        const local = await getLocalSnapshot(reportId);
        if (local) {
          const base = (local.base_rows?.materials ?? []) as UnitReportMaterialRow[];
          return reconcileServerWithLocalSnapshot({}, base, local, "materials").rows as UnitReportMaterialRow[];
        }
      }
      try {
        const rows = await fetchUnitReportMaterials(String(businessId), unit, reportId);
        const local = await getLocalSnapshot(reportId);
        if (local) {
          return reconcileServerWithLocalSnapshot({}, rows, local, "materials").rows as UnitReportMaterialRow[];
        }
        return rows.map((r) => ({ ...r, sync_status: (r as any).sync_status ?? "synced" }));
      } catch (err) {
        const local = await getLocalSnapshot(reportId);
        if (local) {
          const base = (local.base_rows?.materials ?? []) as UnitReportMaterialRow[];
          return reconcileServerWithLocalSnapshot({}, base, local, "materials").rows as UnitReportMaterialRow[];
        }
        throw err;
      }
    },
    enabled: Boolean(businessId && reportId),
  });
}

export function useCreateUnitReportMaterial(
  businessId: number | string,
  unit: CanonicalUnit,
  reportId: string | undefined,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: UnitReportMaterialPayload) => {
      if (!reportId) throw new Error("Missing reportId");
      const isOffline = typeof navigator !== "undefined" && !navigator.onLine;
      if (isOffline) {
        const actorId = localStorage.getItem("auth_user_id") ?? "offline-user";
        const { operation } = await queueUnitReportOperation({
          actorId,
          projectId: String(businessId),
          unit,
          reportDate: "",
          localReportId: reportId,
          operationKind: "create",
          targetType: "materials",
          payload: payload as unknown as Record<string, unknown>,
        });
        return [{
          ...payload,
          id: operation.client_id,
          client_id: operation.client_id,
          _offline: true,
          status: "pending",
        }] as unknown as UnitReportMaterialRow[];
      }
      return createUnitReportMaterial(String(businessId), unit, reportId, payload);
    },
    onSuccess: () => {
      if (reportId) {
        void qc.invalidateQueries({
          queryKey: queryKeys.unitReportMaterials(businessId, unit, reportId),
        });
      }
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", unit],
      });
    },
  });
}

export function useUpdateUnitReportMaterial(
  businessId: number | string,
  unit: CanonicalUnit,
  reportId: string | undefined,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({
      rowId,
      patch,
    }: {
      rowId: string;
      patch: Partial<UnitReportMaterialPayload>;
    }) => {
      if (!reportId) throw new Error("Missing reportId");
      const isOffline = typeof navigator !== "undefined" && !navigator.onLine;
      if (isOffline) {
        const actorId = localStorage.getItem("auth_user_id") ?? "offline-user";
        await queueUnitReportOperation({
          actorId,
          projectId: String(businessId),
          unit,
          reportDate: "",
          localReportId: reportId,
          clientId: rowId,
          targetServerId: rowId,
          operationKind: "update",
          targetType: "materials",
          payload: patch as unknown as Record<string, unknown>,
        });
        return {
          ...patch,
          id: rowId,
          _offline: true,
          status: "pending",
        } as unknown as UnitReportMaterialRow;
      }
      return updateUnitReportMaterial(
        String(businessId),
        unit,
        reportId,
        rowId,
        patch,
      );
    },
    onSuccess: () => {
      if (reportId) {
        void qc.invalidateQueries({
          queryKey: queryKeys.unitReportMaterials(businessId, unit, reportId),
        });
      }
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", unit],
      });
    },
  });
}

export function useDeleteUnitReportMaterial(
  businessId: number | string,
  unit: CanonicalUnit,
  reportId: string | undefined,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (rowId: string) => {
      if (!reportId) throw new Error("Missing reportId");
      const isOffline = typeof navigator !== "undefined" && !navigator.onLine;
      if (isOffline) {
        const actorId = localStorage.getItem("auth_user_id") ?? "offline-user";
        await queueUnitReportOperation({
          actorId,
          projectId: String(businessId),
          unit,
          reportDate: "",
          localReportId: reportId,
          clientId: rowId,
          targetServerId: rowId,
          operationKind: "delete",
          targetType: "materials",
          payload: {},
        });
        return;
      }
      return deleteUnitReportMaterial(String(businessId), unit, reportId, rowId);
    },
    onSuccess: () => {
      if (reportId) {
        void qc.invalidateQueries({
          queryKey: queryKeys.unitReportMaterials(businessId, unit, reportId),
        });
      }
      void qc.invalidateQueries({
        queryKey: ["businesses", businessId, "unit-report", unit],
      });
    },
  });
}

