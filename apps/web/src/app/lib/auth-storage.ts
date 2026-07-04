/**
 * Single place for reading/writing auth state to localStorage and cookie.
 * Cookie is used so loaders can read auth on the server (SSR).
 */

import type { AuthUser, AuthTokens } from "./auth-types";
import { AUTH_STORAGE_KEYS } from "./auth-types";

const AUTH_COOKIE_NAME = "auth_token";

// Function to manage isClient
function isClient(): boolean {
  return typeof window !== "undefined";
}

// Function to manage getStoredAccessToken
export function getStoredAccessToken(): string | null {
  if (!isClient()) return null;
  return localStorage.getItem(AUTH_STORAGE_KEYS.accessToken);
}

// Function to manage getStoredRefreshToken
export function getStoredRefreshToken(): string | null {
  if (!isClient()) return null;
  return localStorage.getItem(AUTH_STORAGE_KEYS.refreshToken);
}

// Function to manage getStoredUser
export function getStoredUser(): AuthUser | null {
  if (!isClient()) return null;
  try {
    // Variable holding raw
    const raw = localStorage.getItem(AUTH_STORAGE_KEYS.user);
    if (!raw) return null;
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
}

/**
 * Parse access token from request Cookie header (for use in loaders).
 */
export function getAccessTokenFromRequest(request: Request): string | null {
  // Variable holding cookie
  const cookie = request.headers.get("Cookie") ?? "";
  // Variable holding match
  const match = cookie.match(new RegExp(`${AUTH_COOKIE_NAME}=([^;]+)`));
  return match ? decodeURIComponent(match[1]) : null;
}

// Function to manage setStoredAuth
export function setStoredAuth(tokens: AuthTokens, user: AuthUser): void {
  if (!isClient()) return;
  localStorage.setItem(AUTH_STORAGE_KEYS.accessToken, tokens.access);
  localStorage.setItem(AUTH_STORAGE_KEYS.refreshToken, tokens.refresh);
  localStorage.setItem(AUTH_STORAGE_KEYS.user, JSON.stringify(user));
  // Cookie for SSR loaders (7 days, same as refresh)
  document.cookie = `${AUTH_COOKIE_NAME}=${encodeURIComponent(tokens.access)}; path=/; max-age=${7 * 24 * 60 * 60}; SameSite=Lax`;
}

// Function to manage clearStoredAuth
export function clearStoredAuth(): void {
  if (!isClient()) return;
  localStorage.removeItem(AUTH_STORAGE_KEYS.accessToken);
  localStorage.removeItem(AUTH_STORAGE_KEYS.refreshToken);
  localStorage.removeItem(AUTH_STORAGE_KEYS.user);
  document.cookie = `${AUTH_COOKIE_NAME}=; path=/; max-age=0`;
}

/**
 * Returns whether we have enough stored data to consider the user "authenticated"
 * for route protection. Does not validate the token with the server.
 */
export function hasStoredSession(): boolean {
  return !!getStoredAccessToken() && !!getStoredUser();
}
