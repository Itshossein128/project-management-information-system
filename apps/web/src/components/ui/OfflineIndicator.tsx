import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router";
import { useTranslation } from "react-i18next";
import { AlertTriangle, CloudOff, RefreshCw } from "lucide-react";
import { cn } from "@/app/lib/utils";
import { useOnlineStatus } from "@/app/hooks/useOnlineStatus";
import {
  countUnresolvedConflicts,
  getQueueStats,
  isOfflineDBAvailable,
  type QueueStats,
} from "@/app/lib/offlineDB";
import { PATHS } from "@/app/routeVars";

const PROJECT_RE = /\/projects\/([0-9a-fA-F-]{36})/;

const EMPTY_STATS: QueueStats = { pending: 0, syncing: 0, failed: 0, total: 0 };

/**
 * Full-width connectivity banner rendered above the app header.
 * Hidden when online with an empty sync queue (no permanent chrome noise).
 */
export function OfflineIndicator() {
  const { t } = useTranslation();
  const isOnline = useOnlineStatus();
  const location = useLocation();
  const [stats, setStats] = useState<QueueStats>(EMPTY_STATS);
  const [conflicts, setConflicts] = useState(0);

  useEffect(() => {
    if (!isOfflineDBAvailable()) return;
    let active = true;
    const refresh = async () => {
      try {
        const [nextStats, nextConflicts] = await Promise.all([
          getQueueStats(),
          countUnresolvedConflicts(),
        ]);
        if (!active) return;
        setStats(nextStats);
        setConflicts(nextConflicts);
      } catch {
        /* DB not ready yet */
      }
    };
    void refresh();
    const id = window.setInterval(refresh, 5000);
    return () => {
      active = false;
      window.clearInterval(id);
    };
  }, []);

  const projectMatch = location.pathname.match(PROJECT_RE);
  const conflictsHref = projectMatch
    ? `/${PATHS.PROJECT}/${projectMatch[1]}/${PATHS.PROJECT_SYNC_CONFLICTS}`
    : null;

  if (conflicts > 0) {
    return (
      <div
        data-testid="offline-indicator"
        className="flex w-full items-center justify-between gap-3 bg-danger-600 px-4 py-2 text-sm text-white"
      >
        <span className="flex items-center gap-2">
          <AlertTriangle className="size-4" aria-hidden />
          {t("offline.conflictsBanner", { count: conflicts })}
        </span>
        {conflictsHref ? (
          <Link
            to={conflictsHref}
            className="rounded bg-white/20 px-3 py-1 font-medium hover:bg-white/30"
          >
            {t("offline.viewConflicts")}
          </Link>
        ) : null}
      </div>
    );
  }

  if (isOnline && stats.syncing > 0) {
    return (
      <div
        data-testid="offline-indicator"
        className="flex w-full items-center gap-2 bg-info-600 px-4 py-2 text-sm text-white"
      >
        <RefreshCw className="size-4 animate-spin" aria-hidden />
        {t("offline.syncingCount", { count: stats.syncing })}
      </div>
    );
  }

  if (!isOnline) {
    return (
      <div
        data-testid="offline-indicator"
        className="flex w-full items-center justify-between gap-3 bg-warning-500 px-4 py-2 text-sm text-warning-950"
      >
        <span className="flex items-center gap-2">
          <CloudOff className="size-4" aria-hidden />
          {t("offline.offlineLocal")}
        </span>
        {stats.pending > 0 ? (
          <span className="rounded-full bg-warning-950/15 px-3 py-0.5 font-medium">
            {t("offline.queuedCount", { count: stats.pending })}
          </span>
        ) : null}
      </div>
    );
  }

  if (stats.pending > 0 || stats.failed > 0) {
    return (
      <div
        data-testid="offline-indicator"
        className={cn(
          "flex w-full items-center justify-between gap-3 bg-warning-100 px-4 py-2 text-sm text-warning-900",
          "dark:bg-warning-950 dark:text-warning-100",
        )}
      >
        <span className="flex items-center gap-2">
          <CloudOff className="size-4" aria-hidden />
          {stats.failed > 0
            ? t("offline.failedQueued", {
                failed: stats.failed,
                pending: stats.pending,
              })
            : t("offline.pendingSync", { count: stats.pending })}
        </span>
        {conflictsHref && stats.failed > 0 ? (
          <Link to={conflictsHref} className="font-medium underline">
            {t("offline.manageQueue")}
          </Link>
        ) : null}
      </div>
    );
  }

  return null;
}
