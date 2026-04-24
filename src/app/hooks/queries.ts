import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiJson } from "@/app/lib/api-client";
import type {
  Business,
  BusinessJobPosition,
  ListResponse,
  UserBusinessAssignment,
} from "@/app/lib/api-types";
import { queryKeys } from "@/app/lib/react-query-keys";
import { PATHS } from "@/app/routeVars";

export interface HrUserRow {
  id: number;
  phone_number: string;
  first_name: string;
  last_name: string;
  full_name: string;
  date_joined: string;
  is_active: boolean;
  roles: string[];
  assignments_preview?: UserBusinessAssignment[];
}

export function useBusinessesQuery(enabled = true) {
  return useQuery({
    queryKey: queryKeys.businesses(),
    enabled,
    queryFn: () => apiJson<ListResponse<Business>>(`/${PATHS.BUSINESS}/`),
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
        `/${PATHS.BUSINESS}/${businessId}/job-positions/?${new URLSearchParams({
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
        `/${PATHS.BUSINESS}/${businessId}/assignments/?${new URLSearchParams({
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
      apiJson<BusinessJobPosition>(`/${PATHS.BUSINESS}/${businessId}/job-positions/`, {
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
        `/${PATHS.BUSINESS}/${businessId}/job-positions/${args.id}/`,
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
      apiJson<{ ok?: boolean }>(`/${PATHS.BUSINESS}/${businessId}/job-positions/${id}/`, {
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
      apiJson<UserBusinessAssignment>(`/${PATHS.BUSINESS}/${businessId}/assignments/`, {
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
        `/${PATHS.BUSINESS}/${businessId}/assignments/${args.id}/`,
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
      apiJson<{ ok?: boolean }>(`/${PATHS.BUSINESS}/${businessId}/assignments/${id}/`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.businessAssignments(businessId) });
    },
  });
}

