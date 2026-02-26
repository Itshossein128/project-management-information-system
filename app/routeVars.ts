export const ROUTES = {
  INDEX: "routes/index.tsx",
  LOGIN: "routes/login.tsx",
  REGISTER: "routes/register.tsx",
  FORGOT_PASSWORD: "routes/forgot-password.tsx",
  RESET_PASSWORD: "routes/reset-password.tsx",
  PROTECTED_LAYOUT: "routes/_protected.tsx",
  HOME: "routes/home.tsx",
  BUSINESS: "routes/business.tsx",
  BUSINESS_TABLE: "routes/business-table.tsx",
  BUSINESS_SETUP_LAYOUT: "routes/_business-setup.tsx",
  BUSINESS_SETUP: "routes/business-setup.tsx",
  BUSINESS_SETUP_SCHEMA: "routes/business-setup-schema.tsx",
} as const;

export const PATHS = {
  LOGIN: "login",
  REGISTER: "register",
  FORGOT_PASSWORD: "forgot-password",
  RESET_PASSWORD: "reset-password",
  HOME: "home",
  BUSINESS: "businesses",
  BUSINESS_SETUP: "business-setup",
} as const;
