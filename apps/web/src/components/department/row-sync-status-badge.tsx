import { useTranslation } from "react-i18next";
import {
  Cloud,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
} from "lucide-react";

export type RowSyncStatus = "pending" | "sending" | "synced" | "failed" | "conflict";

export interface RowSyncStatusBadgeProps {
  status?: RowSyncStatus | string;
  className?: string;
}

export function RowSyncStatusBadge({
  status = "synced",
  className = "",
}: RowSyncStatusBadgeProps) {
  const { t } = useTranslation();

  const normalizedStatus: RowSyncStatus =
    status === "pending" ||
    status === "sending" ||
    status === "synced" ||
    status === "failed" ||
    status === "conflict"
      ? status
      : "synced";

  const config = {
    pending: {
      label: t("offline.statusPending", "در انتظار همگام‌سازی"),
      icon: (
        <Cloud
          data-testid="icon-cloud-pending"
          className="h-3.5 w-3.5 text-amber-500 fill-amber-100 dark:fill-amber-950"
          aria-hidden="true"
        />
      ),
      badgeClass:
        "bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/30",
    },
    sending: {
      label: t("offline.statusSending", "در حال ارسال…"),
      icon: (
        <RefreshCw
          data-testid="icon-refresh-sending"
          className="h-3.5 w-3.5 animate-spin text-blue-500"
          aria-hidden="true"
        />
      ),
      badgeClass:
        "bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/30",
    },
    synced: {
      label: t("offline.statusSynced", "همگام‌سازی‌شده"),
      icon: (
        <CheckCircle2
          data-testid="icon-check-synced"
          className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400"
          aria-hidden="true"
        />
      ),
      badgeClass:
        "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/30",
    },
    failed: {
      label: t("offline.statusFailed", "خطا در همگام‌سازی"),
      icon: (
        <AlertCircle
          data-testid="icon-alert-failed"
          className="h-3.5 w-3.5 text-rose-600 dark:text-rose-400"
          aria-hidden="true"
        />
      ),
      badgeClass:
        "bg-rose-500/10 text-rose-700 dark:text-rose-400 border-rose-500/30",
    },
    conflict: {
      label: t("offline.statusConflict", "تعارض همگام‌سازی"),
      icon: (
        <AlertTriangle
          data-testid="icon-triangle-conflict"
          className="h-3.5 w-3.5 text-orange-600 dark:text-orange-400"
          aria-hidden="true"
        />
      ),
      badgeClass:
        "bg-orange-500/10 text-orange-700 dark:text-orange-400 border-orange-500/30",
    },
  }[normalizedStatus];

  return (
    <span
      data-testid="row-sync-status"
      data-status={normalizedStatus}
      role="status"
      tabIndex={0}
      aria-label={config.label}
      title={config.label}
      className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-1 ${config.badgeClass} ${className}`}
    >
      {config.icon}
      <span className="select-none">{config.label}</span>
    </span>
  );
}
