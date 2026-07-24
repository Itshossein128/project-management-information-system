import { useId } from "react";
import { useNavigate } from "react-router";
import { Check, CheckCheck, X } from "lucide-react";
import { cn } from "@/app/lib/utils";
import { formatDisplayDateTime } from "@/app/lib/jalali-utils";
import type {
  AppNotification,
  NotificationType,
} from "@/app/lib/api/notifications";
import {
  useNotificationActions,
  useNotificationList,
} from "@/app/hooks/useNotifications";

const TYPE_ACCENT: Record<NotificationType, string> = {
  report_submitted: "bg-warning-500",
  report_approved: "bg-success-500",
  report_rejected: "bg-danger-500",
  generic: "bg-info-500",
};

export function NotificationPanel({
  onClose,
}: {
  onClose: () => void;
}) {
  const navigate = useNavigate();
  const titleId = useId();
  // We pass `true` to useNotificationList since we only mount this when Popover is open
  const { data, isLoading } = useNotificationList(true);
  const { markRead, markAllRead } = useNotificationActions();

  const handleClick = (n: AppNotification) => {
    if (!n.is_read) markRead.mutate(n.id);
    if (n.link) {
      onClose();
      navigate(n.link);
    }
  };

  return (
    <>
      <div className="flex items-center justify-between border-b border-border px-4 py-2.5">
        <span id={titleId} className="text-sm font-semibold">
          اعلان‌ها
        </span>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => markAllRead.mutate()}
            disabled={markAllRead.isPending}
            className="inline-flex items-center gap-1 rounded-sm text-xs text-primary hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50"
          >
            <CheckCheck className="size-3.5" aria-hidden />
            خواندن همه
          </button>
          <button
            type="button"
            onClick={onClose}
            aria-label="بستن"
            className="inline-flex size-7 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <X className="size-4" aria-hidden />
          </button>
        </div>
      </div>

      <div className="max-h-96 overflow-y-auto">
        {isLoading ? (
          <p className="px-4 py-6 text-center text-sm text-muted-foreground">
            در حال بارگذاری...
          </p>
        ) : !data || data.length === 0 ? (
          <p className="px-4 py-8 text-center text-sm text-muted-foreground">
            اعلانی وجود ندارد
          </p>
        ) : (
          <ul className="divide-y divide-border">
            {data.map((n) => (
              <li key={n.id} className="flex items-stretch gap-0">
                <button
                  type="button"
                  onClick={() => handleClick(n)}
                  className={cn(
                    "flex min-w-0 flex-1 gap-3 px-4 py-3 text-right hover:bg-muted/50 focus-visible:outline-none focus-visible:bg-muted/50 focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-inset",
                    !n.is_read && "bg-primary/5",
                  )}
                >
                  <span
                    className={cn(
                      "mt-1.5 size-2 shrink-0 rounded-full",
                      TYPE_ACCENT[n.notification_type],
                      n.is_read && "opacity-30",
                    )}
                    aria-hidden
                  />
                  <span className="min-w-0 flex-1">
                    <span
                      className={cn(
                        "block truncate text-sm",
                        n.is_read ? "text-muted-foreground" : "font-medium",
                      )}
                    >
                      {n.title}
                    </span>
                    {n.message ? (
                      <span className="mt-0.5 block truncate text-xs text-muted-foreground">
                        {n.message}
                      </span>
                    ) : null}
                    <span className="mt-1 block text-[11px] text-muted-foreground">
                      {formatDisplayDateTime(n.created_at)}
                    </span>
                  </span>
                </button>
                {!n.is_read ? (
                  <button
                    type="button"
                    className="shrink-0 px-3 text-muted-foreground hover:bg-muted/50 hover:text-primary focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    aria-label="خواندن"
                    title="خواندن"
                    onClick={() => markRead.mutate(n.id)}
                  >
                    <Check className="size-3.5" aria-hidden />
                  </button>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </div>
    </>
  );
}
