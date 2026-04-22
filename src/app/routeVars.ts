export const ROUTES = {
  INDEX: "routes/index.tsx",
  LOGIN: "routes/login.tsx",
  REGISTER: "routes/register.tsx",
  FORGOT_PASSWORD: "routes/forgot-password.tsx",
  RESET_PASSWORD: "routes/reset-password.tsx",
  PROTECTED_LAYOUT: "routes/_protected.tsx",
  HR_PROTECTED_LAYOUT: "routes/hr/_protected-human-resource.tsx",
  HOME: "routes/home.tsx",
  BUSINESS: "routes/business.tsx",
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
  USERS: "hr/users"
} as const;
