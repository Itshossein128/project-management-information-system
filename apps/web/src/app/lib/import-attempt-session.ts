const PREFIX = "schedule-import-attempt:";

export interface ImportAttemptSession {
  user_id: string;
  project_id: string;
  task_id: string;
  file_name: string;
  recognized_kind: string;
  replace: boolean;
}

function storageKey(userId: string, projectId: string) {
  return `${PREFIX}${userId}:${projectId}`;
}

export function readImportAttempt(
  userId: string | undefined,
  projectId: string,
): ImportAttemptSession | null {
  if (!userId || typeof window === "undefined") return null;
  try {
    const value = JSON.parse(sessionStorage.getItem(storageKey(userId, projectId)) ?? "null") as
      | ImportAttemptSession
      | null;
    if (!value || value.user_id !== userId || value.project_id !== projectId) return null;
    if (typeof value.task_id !== "string" || typeof value.file_name !== "string") return null;
    return value;
  } catch {
    return null;
  }
}

export function saveImportAttempt(value: ImportAttemptSession) {
  if (typeof window === "undefined" || !value.user_id) return;
  try {
    sessionStorage.setItem(storageKey(value.user_id, value.project_id), JSON.stringify(value));
  } catch {
    // Storage can be unavailable; keep the active attempt in the screen's state.
  }
}

export function clearImportAttempt(userId: string, projectId: string) {
  try {
    sessionStorage.removeItem(storageKey(userId, projectId));
  } catch {
    // Starting another attempt still works when browser storage is unavailable.
  }
}
