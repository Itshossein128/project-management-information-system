import { useEffect } from "react";
import { initDB, isOfflineDBAvailable } from "@/app/lib/offlineDB";

/**
 * Registers the vite-plugin-pwa service worker on the client and eagerly opens
 * the offline IndexedDB so stores exist before the first offline write.
 * Renders nothing.
 */
export function PwaManager() {
  useEffect(() => {
    if (isOfflineDBAvailable()) {
      void initDB().catch(() => {
        /* private mode / unsupported browser */
      });
    }

    if (import.meta.env.DEV) return;
    let cancelled = false;
    void import("virtual:pwa-register")
      .then(({ registerSW }) => {
        if (cancelled) return;
        registerSW({ immediate: true });
      })
      .catch(() => {
        /* SW registration unavailable */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return null;
}
