import { apiFetch, apiJson } from "@/app/lib/api-client";
import { isoRangeToJalali, isoToJalali } from "@/app/lib/jalali-utils";
import { PATHS } from "@/app/routeVars";

export type WeatherCondition =
  | "sunny"
  | "cloudy"
  | "partly_cloudy"
  | "rainy"
  | "stormy"
  | "snowy"
  | "foggy";

export type SiteStatus = "active" | "inactive";

export interface WeatherLog {
  id: string;
  log_date: string;
  day_of_week: string;
  temp_max: string | null;
  temp_min: string | null;
  weather_condition: WeatherCondition;
  weather_condition_label: string;
  site_status: SiteStatus;
  site_status_label: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedWeatherLogs {
  count: number;
  next: string | null;
  previous: string | null;
  results: WeatherLog[];
}

export interface WeatherLogPayload {
  log_date: string;
  temp_max?: string | null;
  temp_min?: string | null;
  weather_condition: WeatherCondition;
  site_status: SiteStatus;
}

export interface WeatherLogFormInput {
  log_date_iso: string;
  temp_max: string;
  temp_min: string;
  weather_condition: WeatherCondition;
  site_status: SiteStatus;
}

export const WEATHER_CONDITIONS: { value: WeatherCondition; label: string }[] = [
  { value: "sunny", label: "آفتابی" },
  { value: "cloudy", label: "ابری" },
  { value: "partly_cloudy", label: "نیمه‌ابری" },
  { value: "rainy", label: "بارانی" },
  { value: "stormy", label: "طوفانی" },
  { value: "snowy", label: "برفی" },
  { value: "foggy", label: "مه‌آلود" },
];

export function formToPayload(form: WeatherLogFormInput): WeatherLogPayload {
  return {
    log_date: isoToJalali(form.log_date_iso),
    temp_max: form.temp_max.trim() ? form.temp_max : null,
    temp_min: form.temp_min.trim() ? form.temp_min : null,
    weather_condition: form.weather_condition,
    site_status: form.site_status,
  };
}

export function fetchWeatherLogs(
  projectId: string,
  params: {
    page?: number;
    per_page?: number;
    date_from?: string;
    date_to?: string;
    ordering?: string;
  } = {},
) {
  const search = new URLSearchParams();
  if (params.page) search.set("page", String(params.page));
  if (params.per_page) search.set("per_page", String(params.per_page));
  if (params.ordering) search.set("ordering", params.ordering);
  const jalaliRange = isoRangeToJalali(params.date_from ?? "", params.date_to ?? "");
  if (jalaliRange.date_from) search.set("date_from", jalaliRange.date_from);
  if (jalaliRange.date_to) search.set("date_to", jalaliRange.date_to);
  const qs = search.toString();
  return apiJson<PaginatedWeatherLogs>(
    `/${PATHS.API_PROJECTS}/${projectId}/weather${qs ? `?${qs}` : ""}`,
  );
}

export function createWeatherLog(projectId: string, payload: WeatherLogPayload) {
  return apiJson<WeatherLog>(`/${PATHS.API_PROJECTS}/${projectId}/weather/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateWeatherLog(projectId: string, id: string, payload: Partial<WeatherLogPayload>) {
  return apiJson<WeatherLog>(`/${PATHS.API_PROJECTS}/${projectId}/weather/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteWeatherLog(projectId: string, id: string) {
  const res = await apiFetch(`/${PATHS.API_PROJECTS}/${projectId}/weather/${id}/`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const raw = await res.text();
    let message = "حذف ناموفق بود";
    try {
      const data = JSON.parse(raw) as { error?: { message?: string } | string };
      if (typeof data.error === "object" && data.error?.message) message = data.error.message;
      else if (typeof data.error === "string") message = data.error;
    } catch {
      if (raw) message = raw;
    }
    throw new Error(message);
  }
}
