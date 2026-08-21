import { apiJson } from "@/app/lib/api-client";

export const client = {
  async get<T>(path: string, options?: { params?: Record<string, unknown> }): Promise<{ data: T }> {
    let fullPath = path;
    if (options?.params) {
      const searchParams = new URLSearchParams();
      Object.entries(options.params).forEach(([key, val]) => {
        if (val !== undefined && val !== null) {
          searchParams.append(key, String(val));
        }
      });
      const queryString = searchParams.toString();
      if (queryString) {
        fullPath += (fullPath.includes("?") ? "&" : "?") + queryString;
      }
    }
    const res = await apiJson<T>(fullPath, { method: "GET" });
    return { data: res };
  },

  async post<T>(path: string, payload?: unknown): Promise<{ data: T }> {
    const res = await apiJson<T>(path, {
      method: "POST",
      body: payload !== undefined ? JSON.stringify(payload) : undefined,
    });
    return { data: res };
  },

  async put<T>(path: string, payload?: unknown): Promise<{ data: T }> {
    const res = await apiJson<T>(path, {
      method: "PUT",
      body: payload !== undefined ? JSON.stringify(payload) : undefined,
    });
    return { data: res };
  },

  async patch<T>(path: string, payload?: unknown): Promise<{ data: T }> {
    const res = await apiJson<T>(path, {
      method: "PATCH",
      body: payload !== undefined ? JSON.stringify(payload) : undefined,
    });
    return { data: res };
  },

  async delete<T>(path: string): Promise<{ data: T }> {
    const res = await apiJson<T>(path, { method: "DELETE" });
    return { data: res };
  },
};
