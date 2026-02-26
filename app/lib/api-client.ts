/**
 * API client for the inventory backend. Attaches Bearer token and handles 401.
 * Base URL can be overridden via env (e.g. VITE_API_BASE_URL).
 */

import { getStoredAccessToken, clearStoredAuth } from "./auth-storage";

const getBaseUrl = (): string => {
  if (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_BASE_URL) {
    return (import.meta.env.VITE_API_BASE_URL as string).replace(/\/$/, "");
  }
  return "http://localhost:8000/api";
};

export const API_BASE = getBaseUrl();

export interface ApiError {
  error?: string;
  [key: string]: unknown;
}

async function getAuthHeaders(): Promise<HeadersInit> {
  const token = getStoredAccessToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

/**
 * Call this after 401 to clear local auth so the app can redirect to login.
 */
export function clearAuth(): void {
  clearStoredAuth();
}

/**
 * Fetch with auth and JSON. On 401, clears stored auth (caller should redirect to login).
 */
export async function apiFetch(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  const url = path.startsWith("http") ? path : `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      ...(await getAuthHeaders()),
      ...(options.headers as Record<string, string>),
    },
  });
  if (res.status === 401) {
    clearAuth();
  }
  return res;
}

export async function apiJson<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await apiFetch(path, options);
  const data = (await res.json().catch(() => ({}))) as T & ApiError;
  if (!res.ok) {
    throw new Error((data as ApiError).error ?? (res.statusText || "Request failed"));
  }
  return data as T;
}
