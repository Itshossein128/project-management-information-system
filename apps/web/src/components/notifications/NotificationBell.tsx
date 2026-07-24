import { useState } from "react";
import { Bell } from "lucide-react";
import { cn } from "@/app/lib/utils";
import { useAuth } from "~/contexts/auth-context";
import { useTranslation } from "react-i18next";
import { useUnreadCount } from "@/app/hooks/useNotifications";
import { NotificationPanel } from "./NotificationPanel";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

export function NotificationBell() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const enabled = Boolean(user);
  const { data: unread = 0 } = useUnreadCount(enabled);
  const [open, setOpen] = useState(false);

  if (!enabled) return null;

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button
          type="button"
          aria-label={t("notifications.title")}
          title={t("notifications.title")}
          className={cn(
            "relative inline-flex size-9 items-center justify-center rounded-md border border-border bg-transparent hover:bg-muted outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]",
            open && "bg-muted",
          )}
        >
          <Bell className="size-4" />
          {unread > 0 ? (
            <span className="absolute -inset-e-1 -top-1 inline-flex h-4 min-w-4 items-center justify-center rounded-full border-2 border-background bg-danger-500 px-1 text-[10px] font-semibold leading-none text-white">
              {unread > 99 ? "99+" : unread}
            </span>
          ) : null}
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-80 sm:w-96 p-0 overflow-hidden" align="end">
        <NotificationPanel onClose={() => setOpen(false)} />
      </PopoverContent>
    </Popover>
  );
}
