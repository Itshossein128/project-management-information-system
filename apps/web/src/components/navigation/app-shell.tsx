import { useShellStore } from "@/app/store/shellStore";
import { cn } from "@/app/lib/utils";
import { isRTL } from "@/app/lib/i18n";
import { AppShellHeader } from "@/components/navigation/app-shell-header";
import { Sidebar } from "@/components/navigation/sidebar";
import { ProjectNavigation } from "@/components/navigation/project-navigation";
import { OfflineIndicator } from "@/components/ui/OfflineIndicator";
import { useAutoSync } from "@/app/hooks/useAutoSync";
import { useEffect, useLayoutEffect, useSyncExternalStore } from "react";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { useTranslation } from "react-i18next";
import { Outlet, useLocation } from "react-router";

const desktopQuery = "(min-width: 1024px)";
function subscribeDesktop(callback: () => void) {
  const query = window.matchMedia(desktopQuery);
  query.addEventListener("change", callback);
  return () => query.removeEventListener("change", callback);
}
const desktopSnapshot = () => window.matchMedia(desktopQuery).matches;
const serverDesktopSnapshot = () => false;

export function AppShell() {
  const { t } = useTranslation();
  const location = useLocation();
  const mobileNavOpen = useShellStore((s) => s.mobileNavOpen);
  const closeMobileNav = useShellStore((s) => s.closeMobileNav);
  const rtl = isRTL();
  const desktop = useSyncExternalStore(subscribeDesktop, desktopSnapshot, serverDesktopSnapshot);

  useAutoSync();

  // Finish closing the old page's drawer before the new page is interactive.
  useLayoutEffect(() => {
    closeMobileNav();
  }, [location.pathname, closeMobileNav]);

  useEffect(() => {
    if (desktop) closeMobileNav();
  }, [desktop, closeMobileNav]);

  return (
    <div id="container-appShell" className="min-h-dvh bg-background">
      {desktop ? <Sidebar
        className={cn(
          "fixed inset-y-0 z-30 w-[248px]",
          rtl ? "right-0" : "left-0",
        )}
      /> : (
        <Dialog open={mobileNavOpen} onOpenChange={(open) => { if (!open) closeMobileNav(); }}>
          <DialogContent
            id="container-mobileNavigation"
            showCloseButton={false}
            aria-describedby={undefined}
            className={cn("top-0 bottom-0 h-dvh w-72 max-w-[calc(100vw-2rem)] translate-x-0 translate-y-0 gap-0 rounded-none border-0 p-0 sm:max-w-72 motion-reduce:animate-none", rtl ? "right-0 left-auto" : "left-0")}
            onCloseAutoFocus={(event) => {
              event.preventDefault();
              document.getElementById("button-openMobileNav")?.focus();
            }}
          >
            <DialogTitle className="sr-only">{t("nav.main")}</DialogTitle>
            <Sidebar onClose={closeMobileNav} />
          </DialogContent>
        </Dialog>
      )}

      <div
        id="container-appShellContent"
        className={cn(
          "flex h-dvh min-h-dvh flex-col",
          "lg:ps-[248px]",
        )}
      >
        <OfflineIndicator />
        <AppShellHeader className="z-20 shrink-0" />

        <main
          id="container-appShellMain"
          className="app-aurora min-h-0 flex-1 overflow-x-hidden overflow-y-auto overscroll-y-contain [scrollbar-gutter:stable]"
        >
          <ProjectNavigation />
          <div key={location.pathname} className="page-enter">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
