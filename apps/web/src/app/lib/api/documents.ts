import { PATHS } from "@/app/routeVars";
import { apiFormData, apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export interface DocumentRevisionRow {
  id: string;
  revision_label: string;
  revision_date: string | null;
  file_url: string;
  change_description: string;
  uploaded_by: string | null;
  created_at: string;
}

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
  status: string;
  approver: string | null;
  revisions?: DocumentRevisionRow[];
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
  related_contract: string | null;
}

export interface MeetingRow {
  id: string;
  meeting_date: string;
  meeting_type: string;
  topic: string;
  location: string;
  decisions: string;
  action_items: string;
}

export interface MeetingActionRow {
  id: string;
  meeting: string;
  description: string;
  owner: string | null;
  due_date: string | null;
  status: string;
  completed_at: string | null;
  is_overdue?: boolean;
}

export function fetchDocuments(projectId: string, params: Record<string, string> = {}) {
  const qs = new URLSearchParams(params).toString();
  return apiJson<{ results: DocumentRow[] }>(`${base(projectId)}/documents/${qs ? `?${qs}` : ""}`);
}

export function uploadDocument(projectId: string, formData: FormData) {
  return apiFormData<DocumentRow>(`${base(projectId)}/documents/`, formData);
}

export function fetchDocument(projectId: string, documentId: string) {
  return apiJson<DocumentRow>(`${base(projectId)}/documents/${documentId}/`);
}

export function uploadDocumentRevision(
  projectId: string,
  documentId: string,
  formData: FormData,
) {
  return apiFormData<DocumentRow>(
    `${base(projectId)}/documents/${documentId}/revisions/`,
    formData,
  );
}

export function fetchCorrespondence(projectId: string, params: Record<string, string> = {}) {
  const qs = new URLSearchParams(params).toString();
  return apiJson<{ results: CorrespondenceRow[] }>(
    `${base(projectId)}/correspondence/${qs ? `?${qs}` : ""}`,
  );
}

export function createCorrespondence(
  projectId: string,
  body: Partial<CorrespondenceRow> & {
    corr_type: string;
    subject: string;
    from_party: string;
    to_party: string;
    corr_date: string;
    related_contract?: string | null;
  },
) {
  return apiJson<CorrespondenceRow>(`${base(projectId)}/correspondence/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function respondCorrespondence(
  projectId: string,
  id: string,
  body: { response_date?: string } = {},
) {
  return apiJson<CorrespondenceRow>(`${base(projectId)}/correspondence/${id}/respond/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function fetchMeetings(projectId: string) {
  return apiJson<{ results: MeetingRow[] }>(`${base(projectId)}/meetings/`);
}

export function createMeeting(
  projectId: string,
  body: {
    meeting_date: string;
    meeting_type: string;
    topic?: string;
    location?: string;
    decisions?: string;
    action_items?: string;
  },
) {
  return apiJson<MeetingRow>(`${base(projectId)}/meetings/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function fetchMeetingActions(projectId: string, meetingId: string) {
  return apiJson<{ results: MeetingActionRow[] }>(
    `${base(projectId)}/meetings/${meetingId}/actions/`,
  );
}

export function createMeetingAction(
  projectId: string,
  meetingId: string,
  body: {
    description: string;
    owner?: string | null;
    due_date?: string | null;
  },
) {
  return apiJson<MeetingActionRow>(
    `${base(projectId)}/meetings/${meetingId}/actions/`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

export function updateMeetingAction(
  projectId: string,
  actionId: string,
  body: Partial<Pick<MeetingActionRow, "description" | "owner" | "due_date" | "status">>,
) {
  return apiJson<MeetingActionRow>(
    `${base(projectId)}/meeting-actions/${actionId}/`,
    {
      method: "PATCH",
      body: JSON.stringify(body),
    },
  );
}

export function fetchOpenMeetingActions(projectId: string) {
  return apiJson<{ results: MeetingActionRow[] }>(
    `${base(projectId)}/meeting-actions/open/`,
  );
}

export const DOC_STATUS_LABELS: Record<string, string> = {
  draft: "پیش‌نویس",
  in_review: "در حال بررسی",
  approved: "تأیید شده",
  superseded: "جایگزین شده",
  obsolete: "منسوخ",
};

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

export const DOC_TYPE_LABELS: Record<string, string> = {
  drawing: "نقشه",
  specification: "مشخصات",
  contract: "قرارداد",
  report: "گزارش",
  correspondence: "مکاتبه",
  minutes: "صورتجلسه",
  photo: "عکس",
  other: "سایر",
};
