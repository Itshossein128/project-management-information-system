/**
 * API client for IPCAS backend. Attaches Bearer token, refreshes on 401, handles auth cleanup.
 */

import {
  getStoredAccessToken,
  getStoredRefreshToken,
  getStoredUser,
  setStoredAuth,
  clearStoredAuth,
} from "./auth-storage";
import type { AuthUser } from "./auth-types";

const getBaseUrl = (): string => {
  if (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_BASE_URL) {
    return (import.meta.env.VITE_API_BASE_URL as string).replace(/\/$/, "");
  }
  return "http://localhost:8000/api";
};

export const API_BASE = getBaseUrl();

function getAcceptLanguage(): string {
  if (typeof window === "undefined") return "fa";
  const stored =
    window.localStorage.getItem("app-language") ??
    window.localStorage.getItem("i18nextLng") ??
    "fa";
  return stored.startsWith("en") ? "en" : "fa";
}

function withAcceptLanguage(headers: Record<string, string>): Record<string, string> {
  return { ...headers, "Accept-Language": getAcceptLanguage() };
}

export interface ApiError {
  error?: string;
  [key: string]: unknown;
}

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refresh = getStoredRefreshToken();
  if (!refresh) return null;
  if (!refreshPromise) {
    refreshPromise = (async () => {
      try {
        const res = await fetch(`${API_BASE}/auth/token/refresh/`, {
          method: "POST",
          headers: withAcceptLanguage({
            "Content-Type": "application/json",
            Accept: "application/json",
          }),
          body: JSON.stringify({ refresh }),
        });
        if (!res.ok) return null;
        const data = (await res.json()) as { access: string; refresh?: string };
        const user = getStoredUser();
        if (user) {
          setStoredAuth(
            { access: data.access, refresh: data.refresh ?? refresh },
            user,
          );
        }
        return data.access;
      } catch {
        return null;
      } finally {
        refreshPromise = null;
      }
    })();
  }
  return refreshPromise;
}

async function getAuthHeaders(): Promise<HeadersInit> {
  const token = getStoredAccessToken();
  const headers = withAcceptLanguage({
    "Content-Type": "application/json",
    Accept: "application/json",
  });
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

async function getAuthHeadersNoContentType(): Promise<HeadersInit> {
  const token = getStoredAccessToken();
  const headers = withAcceptLanguage({ Accept: "application/json" });
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

export function clearAuth(): void {
  clearStoredAuth();
}

export async function apiFetch(
  path: string,
  options: RequestInit = {},
  retried = false,
): Promise<Response> {
  const url = path.startsWith("http") ? path : `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      ...(await getAuthHeaders()),
      ...(options.headers as Record<string, string>),
    },
  });
  if (res.status === 401 && !retried && !path.includes("/auth/login")) {
    const newAccess = await refreshAccessToken();
    if (newAccess) {
      return apiFetch(path, options, true);
    }
    clearAuth();
  }
  return res;
}

export async function apiJson<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await apiFetch(path, options);
  const raw = await res.text();
  let data: (T & ApiError) | (ApiError & { detail?: unknown }) = {};
  if (raw) {
    try {
      data = JSON.parse(raw) as T & ApiError;
    } catch {
      data = {};
    }
  }
  if (!res.ok) {
    const apiError = data as ApiError & { detail?: unknown; error?: unknown };
    const nested =
      typeof apiError.error === "object" &&
      apiError.error !== null &&
      "message" in (apiError.error as object)
        ? String((apiError.error as { message: string }).message)
        : null;
    const detail =
      typeof apiError.detail === "string"
        ? apiError.detail
        : apiError.detail
          ? JSON.stringify(apiError.detail)
          : null;
    const flatError = typeof apiError.error === "string" ? apiError.error : null;
    const message =
      nested ??
      flatError ??
      detail ??
      (raw && raw.trim() ? raw.trim() : null) ??
      (res.statusText || "Request failed");
    throw new Error(message);
  }
  if (!raw) return {} as T;
  return data as T;
}

export async function apiBlob(path: string): Promise<Blob> {
  const res = await apiFetch(path, { method: "GET", headers: await getAuthHeadersNoContentType() });
  if (!res.ok) {
    const text = await res.text();
    let msg = res.statusText;
    try {
      const j = JSON.parse(text) as ApiError;
      if (j.error) msg = j.error;
    } catch {
      if (text) msg = text;
    }
    throw new Error(msg);
  }
  return res.blob();
}

export async function apiFormData<T>(
  path: string,
  formData: FormData,
  options: { method?: string } = {},
): Promise<T> {
  const res = await apiFetch(path, {
    method: options.method ?? "POST",
    headers: await getAuthHeadersNoContentType(),
    body: formData,
  });
  const raw = await res.text();
  let data: (T & ApiError) | (ApiError & { detail?: unknown }) = {};
  if (raw) {
    try {
      data = JSON.parse(raw) as T & ApiError;
    } catch {
      data = {};
    }
  }
  if (!res.ok) {
    const apiError = data as ApiError & { detail?: unknown; error?: unknown };
    const nested =
      typeof apiError.error === "object" &&
      apiError.error !== null &&
      "message" in (apiError.error as object)
        ? String((apiError.error as { message: string }).message)
        : null;
    const detail =
      typeof apiError.detail === "string"
        ? apiError.detail
        : apiError.detail
          ? JSON.stringify(apiError.detail)
          : null;
    const flatError = typeof apiError.error === "string" ? apiError.error : null;
    const message =
      nested ??
      flatError ??
      detail ??
      (raw && raw.trim() ? raw.trim() : null) ??
      (res.statusText || "Request failed");
    throw new Error(message);
  }
  if (!raw) return {} as T;
  return data as T;
}

export async function apiUploadFile<T = { created: number; errors: unknown[] }>(
  path: string,
  file: File,
): Promise<T> {
  const form = new FormData();
  form.append("file", file);
  const res = await apiFetch(path, {
    method: "POST",
    headers: await getAuthHeadersNoContentType(),
    body: form,
  });
  const data = (await res.json().catch(() => ({}))) as T & ApiError;
  if (!res.ok) {
    throw new Error((data as ApiError).error ?? (res.statusText || "Request failed"));
  }
  return data as T;
}

export async function restoreSessionFromServer(): Promise<AuthUser | null> {
  const token = getStoredAccessToken();
  if (!token) return null;
  try {
    return await apiJson<AuthUser>("/auth/profile/");
  } catch {
    const refreshed = await refreshAccessToken();
    if (!refreshed) {
      clearAuth();
      return null;
    }
    try {
      return await apiJson<AuthUser>("/auth/profile/");
    } catch {
      clearAuth();
      return null;
    }
  }
}
