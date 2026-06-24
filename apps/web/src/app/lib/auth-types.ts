/**
 * Auth types shared by storage, API client, and context.
 * Uses phone_number as identifier; display name is first_name + last_name.
 * Roles: visitor, manager, commentor, business-setup (extensible for future roles).
 * business-setup: add business and control features per business; support team only.
 */

import type { ROLES } from "@/config/roles";

export interface AuthUser {
  id: number;
  phone_number: string;
  first_name: string;
  last_name: string;
  full_name: string;
  roles: ROLES[];
  date_joined?: string;
}


export interface AuthTokens {
  access: string;
  refresh: string;
}

export const AUTH_STORAGE_KEYS = {
  accessToken: "auth_access_token",
  refreshToken: "auth_refresh_token",
  user: "auth_user",
} as const;
