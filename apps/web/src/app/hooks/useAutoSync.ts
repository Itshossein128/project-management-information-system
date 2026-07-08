import { useEffect, useRef } from "react";
import { useToast } from "@/components/ui/toast";
import { useOnlineStatus } from "@/app/hooks/useOnlineStatus";
import { isOfflineDBAvailable } from "@/app/lib/offlineDB";
import { syncPendingQueue } from "@/app/lib/syncService";

/**
 * Runs the offline sync queue on mount and whenever connectivity is restored.
 * Reports the outcome via toasts (Sprint 4, Section 1.6).
 */
export function useAutoSync(): void {
  const isOnline = useOnlineStatus();
  const toast = useToast();
  const wasOnline = useRef(isOnline);
  const running = useRef(false);

  useEffect(() => {
    if (!isOfflineDBAvailable()) return;

    const justReconnected = isOnline && !wasOnline.current;
    wasOnline.current = isOnline;

    // Sync on mount (isOnline true) or on reconnect transition.
    if (!isOnline) return;
    if (running.current) return;
    // Only auto-run on mount or reconnect, not on every render.
    if (!justReconnected && running.current) return;

    running.current = true;
    void syncPendingQueue()
      .then((result) => {
        if (result.synced > 0) toast.success(`${result.synced} مورد همگام‌سازی شد`);
        if (result.failed > 0) toast.warning(`${result.failed} مورد همگام‌سازی نشد`);
        if (result.conflicts > 0)
          toast.error(`${result.conflicts} تعارض داده شناسایی شد — بررسی کنید`);
      })
      .catch(() => {
        /* offline DB not ready or network dropped mid-sync; ignore */
      })
      .finally(() => {
        running.current = false;
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOnline]);
}
