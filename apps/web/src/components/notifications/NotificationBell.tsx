import { useEffect, useRef, useState } from "react";
import { Bell } from "lucide-react";
import { cn } from "@/app/lib/utils";
import { useAuth } from "~/contexts/auth-context";
import { useTranslation } from "react-i18next";
import { useUnreadCount } from "@/app/hooks/useNotifications";
import { NotificationPanel } from "./NotificationPanel";

export function NotificationBell() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const enabled = Boolean(user);
  const { data: unread = 0 } = useUnreadCount(enabled);
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDocClick = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    const onEsc = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    document.addEventListener("mousedown", onDocClick);
    document.addEventListener("keydown", onEsc);
    return () => {
      document.removeEventListener("mousedown", onDocClick);
      document.removeEventListener("keydown", onEsc);
    };
  }, [open]);

  if (!enabled) return null;

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        aria-label={t("notifications.title")}
        title={t("notifications.title")}
        aria-expanded={open}
        aria-haspopup="dialog"
        aria-controls={open ? "notification-panel" : undefined}
        onClick={() => setOpen((v) => !v)}
        className={cn(
          "relative inline-flex size-9 items-center justify-center rounded-md border border-border bg-transparent hover:bg-muted outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]",
          open && "bg-muted",
        )}
      >
        <Bell className="size-4" />
        {unread > 0 ? (
          <span className="absolute -inset-e-1 -top-1 inline-flex min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-semibold leading-4 text-white">
            {unread > 99 ? "99+" : unread}
          </span>
        ) : null}
      </button>
      {open ? <NotificationPanel open={open} onClose={() => setOpen(false)} /> : null}
    </div>
  );
}
