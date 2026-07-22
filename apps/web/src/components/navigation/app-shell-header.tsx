import { AppPreferencesBar } from "@/components/AppPreferencesBar";
import { NotificationBell } from "@/components/notifications/NotificationBell";
import { Button } from "@/components/form";
import { cn } from "@/app/lib/utils";
import { useShellStore } from "@/app/store/shellStore";
import { Menu } from "lucide-react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";
import { useAuth } from "~/contexts/auth-context";

export interface AppShellHeaderProps {
  className?: string;
}

/**
 * Top bar for the app shell. Sidebar is fixed (Home + HR); it does not reflect
 * the current business or project page.
 */
export function AppShellHeader({ className }: AppShellHeaderProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const openMobileNav = useShellStore((s) => s.openMobileNav);
  const displayName =
    user?.full_name ||
    `${user?.first_name ?? ""} ${user?.last_name ?? ""}`.trim() ||
    user?.phone_number ||
    "User";

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <header
      className={cn(
        "app-chrome shrink-0 border-b px-3 py-3 sm:px-5 sm:py-4",
        className,
      )}
    >
      <div className="mx-auto flex min-w-0 flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex min-w-0 items-center gap-2 sm:gap-3">
          <Button
            id="button-openMobileNav"
            type="button"
            variant="outline"
            size="icon-sm"
            className="shrink-0 lg:hidden"
            aria-label={t("nav.openMenu")}
            onClick={openMobileNav}
          >
            <Menu id="icon-menu" className="size-4" aria-hidden />
          </Button>
          <h1
            className="text-page-title min-w-0 truncate"
            id="text-appHeaderTitle"
          >
            {t("home.headerTitle")}
          </h1>
        </div>

        <div className="flex min-w-0 flex-wrap items-center justify-end gap-2.5 sm:gap-3">
          <NotificationBell />
          <AppPreferencesBar />
          <span
            className="hidden max-w-[10rem] truncate text-muted-foreground text-sm sm:inline md:max-w-[14rem]"
            id="text-appHeaderUser"
            title={displayName}
          >
            {displayName}
            {user?.roles?.length ? (
              <span className="ms-1 hidden text-xs lg:inline">
                ({user.roles.join(", ")})
              </span>
            ) : null}
          </span>
          <Button
            id="button-appHeaderSignOut"
            variant="outline"
            size="sm"
            className="shrink-0"
            onClick={handleLogout}
          >
            {t("common.signOut")}
          </Button>
        </div>
      </div>
    </header>
  );
}
