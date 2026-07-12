import { useCallback } from "react";
import { useOnlineStatus } from "@/app/hooks/useOnlineStatus";
import {
  createDailyReport,
  type HeaderPayload,
  updateDailyReport,
} from "@/app/lib/api/daily-reports";
import { isOfflineDBAvailable } from "@/app/lib/offlineDB";
import { queueReportHeader } from "@/app/lib/offlineWrite";

export interface SaveHeaderResult {
  reportId: string;
  offline: boolean;
}

/**
 * Transparent online/offline save for a daily-report header. When online it
 * hits the API directly; when offline (or the request fails while the browser
 * reports offline) it falls back to the IndexedDB queue and returns a local id.
 */
export function useDailyReportForm(projectId: string, reportId?: string) {
  const isOnline = useOnlineStatus();

  const saveHeader = useCallback(
    async (payload: HeaderPayload): Promise<SaveHeaderResult> => {
      const goOffline = () => queueReportHeader(projectId, reportId ?? null, payload);

      if (!isOnline && isOfflineDBAvailable()) {
        const localId = await goOffline();
        return { reportId: localId, offline: true };
      }

      try {
        const res = reportId
          ? await updateDailyReport(projectId, reportId, payload)
          : await createDailyReport(projectId, payload);
        return { reportId: res.report_id, offline: false };
      } catch (err) {
        // If we dropped offline mid-request, queue instead of failing.
        if (typeof navigator !== "undefined" && !navigator.onLine && isOfflineDBAvailable()) {
          const localId = await goOffline();
          return { reportId: localId, offline: true };
        }
        throw err;
      }
    },
    [projectId, reportId, isOnline],
  );

  return { saveHeader, isOnline };
}
