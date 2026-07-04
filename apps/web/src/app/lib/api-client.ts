/**
 * API client for the inventory backend. Attaches Bearer token and handles 401.
 * Base URL can be overridden via env (e.g. VITE_API_BASE_URL).
 */

import { getStoredAccessToken, clearStoredAuth } from "./auth-storage";

// Function to manage getBaseUrl
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
  // Variable holding token
  const token = getStoredAccessToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

async function getAuthHeadersNoContentType(): Promise<HeadersInit> {
  // Variable holding token
  const token = getStoredAccessToken();
  const headers: Record<string, string> = { Accept: "application/json" };
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
  // Variable holding url
  const url = path.startsWith("http") ? path : `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
  // Variable holding res
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
  // Variable holding res
  const res = await apiFetch(path, options);
  // Variable holding raw
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
    // Variable holding apiError
    const apiError = data as ApiError & { detail?: unknown };
    // Variable holding detail
    const detail =
      typeof apiError.detail === "string"
        ? apiError.detail
        : apiError.detail
          ? JSON.stringify(apiError.detail)
          : null;
    // Variable holding message
    const message =
      apiError.error ??
      detail ??
      (raw && raw.trim() ? raw.trim() : null) ??
      (res.statusText || "Request failed");
    throw new Error(message);
  }
  if (!raw) return {} as T;
  return data as T;
}

/** GET and return response as Blob (e.g. Excel download). */
export async function apiBlob(path: string): Promise<Blob> {
  // Variable holding url
  const url = path.startsWith("http") ? path : `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
  // Variable holding res
  const res = await fetch(url, {
    method: "GET",
    headers: await getAuthHeadersNoContentType(),
  });
  if (res.status === 401) clearAuth();
  if (!res.ok) {
    // Variable holding text
    const text = await res.text();
    // Variable holding msg
    let msg = res.statusText;
    try {
      // Variable holding j
      const j = JSON.parse(text) as ApiError;
      if (j.error) msg = j.error;
    } catch {
      if (text) msg = text;
    }
    throw new Error(msg);
  }
  return res.blob();
}

/** POST multipart/form-data with a file (e.g. Excel import). Do not set Content-Type. */
export async function apiUploadFile<T = { created: number; errors: unknown[] }>(
  path: string,
  file: File
): Promise<T> {
  // Variable holding url
  const url = path.startsWith("http") ? path : `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
  // Variable holding form
  const form = new FormData();
  form.append("file", file);
  // Variable holding res
  const res = await fetch(url, {
    method: "POST",
    headers: await getAuthHeadersNoContentType(),
    body: form,
  });
  if (res.status === 401) clearAuth();
  // Function to manage data
  const data = (await res.json().catch(() => ({}))) as T & ApiError;
  if (!res.ok) {
    throw new Error((data as ApiError).error ?? (res.statusText || "Request failed"));
  }
  return data as T;
}
