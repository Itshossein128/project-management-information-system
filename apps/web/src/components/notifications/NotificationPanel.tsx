import { useNavigate } from "react-router";
import { Check, CheckCheck } from "lucide-react";
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
  report_submitted: "bg-amber-500",
  report_approved: "bg-emerald-500",
  report_rejected: "bg-red-500",
  generic: "bg-sky-500",
};

export function NotificationPanel({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const navigate = useNavigate();
  const { data, isLoading } = useNotificationList(open);
  const { markRead, markAllRead } = useNotificationActions();

  const handleClick = (n: AppNotification) => {
    if (!n.is_read) markRead.mutate(n.id);
    if (n.link) {
      onClose();
      navigate(n.link);
    }
  };

  return (
    <div className="absolute inset-e-0 z-50 mt-2 w-80 overflow-hidden rounded-xl border border-border bg-card shadow-lg sm:w-96">
      <div className="flex items-center justify-between border-b border-border px-4 py-2.5">
        <span className="text-sm font-semibold">اعلان‌ها</span>
        <button
          type="button"
          onClick={() => markAllRead.mutate()}
          disabled={markAllRead.isPending}
          className="inline-flex items-center gap-1 text-xs text-primary hover:underline disabled:opacity-50"
        >
          <CheckCheck className="size-3.5" />
          خواندن همه
        </button>
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
              <li key={n.id}>
                <button
                  type="button"
                  onClick={() => handleClick(n)}
                  className={cn(
                    "flex w-full gap-3 px-4 py-3 text-right hover:bg-muted/50",
                    !n.is_read && "bg-primary/5",
                  )}
                >
                  <span
                    className={cn(
                      "mt-1.5 size-2 shrink-0 rounded-full",
                      TYPE_ACCENT[n.notification_type],
                      n.is_read && "opacity-30",
                    )}
                  />
                  <span className="min-w-0 flex-1">
                    <span className="flex items-center justify-between gap-2">
                      <span
                        className={cn(
                          "truncate text-sm",
                          n.is_read ? "text-muted-foreground" : "font-medium",
                        )}
                      >
                        {n.title}
                      </span>
                      {!n.is_read ? (
                        <button
                          type="button"
                          className="rounded-sm text-muted-foreground hover:text-primary focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                          aria-label="خواندن"
                          title="خواندن"
                          onClick={(e) => {
                            e.stopPropagation();
                            markRead.mutate(n.id);
                          }}
                        >
                          <Check className="size-3.5 shrink-0" />
                        </button>
                      ) : null}
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
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
