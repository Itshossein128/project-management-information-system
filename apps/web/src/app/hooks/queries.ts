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
} from "@/app/lib/api/unit-reports";
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
      try {
        return await fetchCurrentUnitReport(
          String(businessId),
          unit as CanonicalUnit,
          date!,
        );
      } catch (err) {
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
    mutationFn: (reportDate: string) =>
      openUnitReport(String(businessId), unit, reportDate),
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
    queryFn: () =>
      fetchUnitReportActivities(
        String(businessId),
        unit as CanonicalUnit,
        reportId!,
      ),
  });
}

export function useCreateUnitReportActivity(
  businessId: number | string,
  unit: CanonicalUnit,
  reportId: string | undefined,
) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: UnitReportActivityPayload) => {
      if (!reportId) throw new Error("Missing reportId");
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
    mutationFn: ({
      rowId,
      patch,
    }: {
      rowId: string;
      patch: Partial<UnitReportActivityPayload>;
    }) => {
      if (!reportId) throw new Error("Missing reportId");
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
    mutationFn: (rowId: string) => {
      if (!reportId) throw new Error("Missing reportId");
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

