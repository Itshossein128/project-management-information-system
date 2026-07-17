import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router";
import { AlertTriangle, CloudOff, RefreshCw, Wifi } from "lucide-react";
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
 */
export function OfflineIndicator() {
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
        className="flex w-full items-center justify-between gap-3 bg-red-600 px-4 py-2 text-sm text-white"
      >
        <span className="flex items-center gap-2">
          <AlertTriangle className="size-4" />
          {`⚠ ${conflicts} تعارض داده نیاز به بررسی دارد`}
        </span>
        {conflictsHref ? (
          <Link
            to={conflictsHref}
            className="rounded bg-white/20 px-3 py-1 font-medium hover:bg-white/30"
          >
            مشاهده تعارض‌ها
          </Link>
        ) : null}
      </div>
    );
  }

  if (isOnline && stats.syncing > 0) {
    return (
      <div
        data-testid="offline-indicator"
        className="flex w-full items-center gap-2 bg-blue-600 px-4 py-2 text-sm text-white"
      >
        <RefreshCw className="size-4 animate-spin" />
        {`در حال همگام‌سازی... (${stats.syncing} مورد)`}
      </div>
    );
  }

  if (!isOnline) {
    return (
      <div
        data-testid="offline-indicator"
        className="flex w-full items-center justify-between gap-3 bg-amber-500 px-4 py-2 text-sm text-amber-950"
      >
        <span className="flex items-center gap-2">
          <CloudOff className="size-4" />
          offline — داده‌ها به صورت محلی ذخیره می‌شوند
        </span>
        {stats.pending > 0 ? (
          <span className="rounded-full bg-amber-950/15 px-3 py-0.5 font-medium">
            {`در صف: ${stats.pending} مورد`}
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
          "flex w-full items-center justify-between gap-3 bg-amber-100 px-4 py-2 text-sm text-amber-900",
          "dark:bg-amber-950 dark:text-amber-100",
        )}
      >
        <span className="flex items-center gap-2">
          <CloudOff className="size-4" />
          {stats.failed > 0
            ? `${stats.failed} مورد ناموفق — ${stats.pending} در صف`
            : `${stats.pending} مورد در انتظار همگام‌سازی`}
        </span>
        {conflictsHref && stats.failed > 0 ? (
          <Link to={conflictsHref} className="font-medium underline">
            مدیریت صف
          </Link>
        ) : null}
      </div>
    );
  }

  return (
    <div
      data-testid="offline-indicator"
      className="flex w-full items-center gap-2 bg-emerald-700 px-4 py-1.5 text-xs text-white"
    >
      <Wifi className="size-3.5" />
      آنلاین
    </div>
  );
}
