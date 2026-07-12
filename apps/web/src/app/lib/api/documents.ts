import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export interface DocumentRow {
  id: string;
  doc_code: string;
  title: string;
  doc_type: string;
  discipline: string;
  revision: string;
  revision_date: string | null;
  file_url: string;
  file_name: string;
  access_level: string;
}

export interface CorrespondenceRow {
  id: string;
  corr_number: string;
  corr_type: string;
  subject: string;
  from_party: string;
  to_party: string;
  corr_date: string;
  response_due_date: string | null;
  response_date: string | null;
  status: string;
}

export interface MeetingRow {
  id: string;
  meeting_date: string;
  meeting_type: string;
  location: string;
  decisions: string;
  action_items: string;
}

export function fetchDocuments(projectId: string, params: Record<string, string> = {}) {
  const qs = new URLSearchParams(params).toString();
  return apiJson<{ results: DocumentRow[] }>(`${base(projectId)}/documents/${qs ? `?${qs}` : ""}`);
}

export function fetchCorrespondence(projectId: string, params: Record<string, string> = {}) {
  const qs = new URLSearchParams(params).toString();
  return apiJson<{ results: CorrespondenceRow[] }>(
    `${base(projectId)}/correspondence/${qs ? `?${qs}` : ""}`,
  );
}

export function fetchMeetings(projectId: string) {
  return apiJson<{ results: MeetingRow[] }>(`${base(projectId)}/meetings/`);
}

export const CORR_TYPE_LABELS: Record<string, string> = {
  outgoing: "صادره",
  incoming: "وارده",
  internal: "داخلی",
};

export const CORR_STATUS_LABELS: Record<string, string> = {
  open: "باز",
  responded: "پاسخ داده شده",
  closed: "بسته",
  no_response_needed: "بدون نیاز به پاسخ",
};

export const MEETING_TYPE_LABELS: Record<string, string> = {
  weekly_progress: "جلسه پیشرفت هفتگی",
  employer_meeting: "جلسه کارفرما",
  subcontractor: "جلسه پیمانکار",
  safety: "جلسه ایمنی",
  other: "سایر",
};
