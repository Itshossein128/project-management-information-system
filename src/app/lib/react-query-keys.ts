export const queryKeys = {
  businesses: () => ["businesses"] as const,
  business: (businessId: number | string) => ["businesses", businessId] as const,

  businessJobPositions: (
    businessId: number | string,
    params?: Record<string, unknown>,
  ) => ["businesses", businessId, "job-positions", params ?? {}] as const,

  businessAssignments: (businessId: number | string, params?: Record<string, unknown>) =>
    ["businesses", businessId, "assignments", params ?? {}] as const,

  authUsers: (params: Record<string, unknown>) => ["auth", "users", params] as const,

  userAssignments: (userId: number | string) =>
    ["auth", "users", userId, "assignments"] as const,
};

