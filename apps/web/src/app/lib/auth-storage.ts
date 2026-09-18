/**
 * Single place for reading/writing auth state to localStorage and cookie.
 * Cookie is used so loaders can read auth on the server (SSR).
 */

import type { AuthUser, AuthTokens } from "./auth-types";
import { AUTH_STORAGE_KEYS } from "./auth-types";

const AUTH_COOKIE_NAME = "auth_token";
const AUTH_COOKIE_MAX_AGE = 7 * 24 * 60 * 60;

type AuthStorageListener = () => void;
const authStorageListeners = new Set<AuthStorageListener>();

function isClient(): boolean {
  return typeof window !== "undefined";
}

function writeAuthCookie(accessToken: string): void {
  document.cookie = `${AUTH_COOKIE_NAME}=${encodeURIComponent(accessToken)}; path=/; max-age=${AUTH_COOKIE_MAX_AGE}; SameSite=Lax`;
}

function notifyAuthStorageListeners(): void {
  for (const listener of authStorageListeners) {
    listener();
  }
}

/** Subscribe to same-tab auth storage clears/writes (storage event is cross-tab only). */
export function subscribeAuthStorage(listener: AuthStorageListener): () => void {
  authStorageListeners.add(listener);
  return () => {
    authStorageListeners.delete(listener);
  };
}

export function getStoredAccessToken(): string | null {
  if (!isClient()) return null;
  return localStorage.getItem(AUTH_STORAGE_KEYS.accessToken);
}

export function getStoredRefreshToken(): string | null {
  if (!isClient()) return null;
  return localStorage.getItem(AUTH_STORAGE_KEYS.refreshToken);
}

export function getStoredUser(): AuthUser | null {
  if (!isClient()) return null;
  try {
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
  const cookie = request.headers.get("Cookie") ?? "";
  const match = cookie.match(new RegExp(`${AUTH_COOKIE_NAME}=([^;]+)`));
  return match ? decodeURIComponent(match[1]) : null;
}

/**
 * Whether the current navigation is allowed through auth-gated loaders.
 * Client navigations must use localStorage — browser Request objects often omit Cookie.
 */
export function hasLoaderAuth(request: Request): boolean {
  if (isClient()) {
    return hasStoredSession();
  }
  return !!getAccessTokenFromRequest(request);
}

export function setStoredAuth(tokens: AuthTokens, user: AuthUser): void {
  if (!isClient()) return;
  localStorage.setItem(AUTH_STORAGE_KEYS.accessToken, tokens.access);
  localStorage.setItem(AUTH_STORAGE_KEYS.refreshToken, tokens.refresh);
  localStorage.setItem(AUTH_STORAGE_KEYS.user, JSON.stringify(user));
  writeAuthCookie(tokens.access);
  notifyAuthStorageListeners();
}

export function clearStoredAuth(): void {
  if (!isClient()) return;
  localStorage.removeItem(AUTH_STORAGE_KEYS.accessToken);
  localStorage.removeItem(AUTH_STORAGE_KEYS.refreshToken);
  localStorage.removeItem(AUTH_STORAGE_KEYS.user);
  document.cookie = `${AUTH_COOKIE_NAME}=; path=/; max-age=0`;
  notifyAuthStorageListeners();
}

/**
 * If localStorage has a session but the SSR cookie is missing/stale, rewrite it.
 * Prevents hard navigations from bouncing authenticated users to /login.
 */
export function syncAuthCookieFromStorage(): void {
  if (!isClient()) return;
  const access = getStoredAccessToken();
  if (!access) return;
  const cookie = document.cookie.match(new RegExp(`${AUTH_COOKIE_NAME}=([^;]+)`));
  const current = cookie ? decodeURIComponent(cookie[1]) : null;
  if (current !== access) {
    writeAuthCookie(access);
  }
}

/**
 * Returns whether we have enough stored data to consider the user "authenticated"
 * for route protection. Does not validate the token with the server.
 */
export function hasStoredSession(): boolean {
  return !!getStoredAccessToken() && !!getStoredUser();
}
