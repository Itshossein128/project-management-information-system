export const ROUTES = {
  INDEX: "routes/index.tsx",
  LOGIN: "routes/login.tsx",
  REGISTER: "routes/register.tsx",
  FORGOT_PASSWORD: "routes/forgot-password.tsx",
  RESET_PASSWORD: "routes/reset-password.tsx",
  AUTH_LAYOUT: "routes/_auth.tsx",
  PROTECTED_LAYOUT: "routes/_protected.tsx",
  HR_PROTECTED_LAYOUT: "routes/hr/_protected-human-resource.tsx",
  HR_HUB: "routes/hr/home.tsx",
  HR_JOB_POSITIONS: "routes/hr/job-positions.tsx",
  HOME: "routes/home.tsx",
  BUSINESS: "routes/business.tsx",
  BUSINESS_USERS: "routes/business-users.tsx",
  BUSINESS_JOB_POSITIONS: "routes/business-job-positions.tsx",
  BUSINESS_TABLE: "routes/business-table.tsx",
  BUSINESS_SETUP: "routes/business-setup.tsx",
  BUSINESS_CREATE: "routes/business-create.tsx",
  BUSINESS_SETUP_SCHEMA: "routes/business-setup-schema.tsx",
  USERS: "routes/hr/users.tsx"
} as const;

/** URL segments (no leading slash). */
export const PATHS = {
  LOGIN: "login",
  REGISTER: "register",
  FORGOT_PASSWORD: "forgot-password",
  RESET_PASSWORD: "reset-password",
  HOME: "home",
  /** Business workspace & admin URLs under `/businesses/...`. */
  BUSINESS: "businesses",
  /** `/businesses/create` */
  BUSINESS_CREATE: "create",
  /** `/businesses/:id/setup` (tables & fields admin) */
  BUSINESS_ADMIN_SETUP: "setup",
  /** App HR area: `/hr` (hub) and `hr/...` sub-routes. */
  HR: "hr",
  HR_JOB_POSITIONS: "job-positions",
  USERS: "hr/users",
  /** `GET /api/auth/users/` — HR / admin user list (not a React route). */
  API_AUTH_USERS: "auth/users",
} as const;
