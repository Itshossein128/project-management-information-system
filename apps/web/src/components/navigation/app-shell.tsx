import { useShellStore } from "@/app/store/shellStore";
import { cn } from "@/app/lib/utils";
import { isRTL } from "@/app/lib/i18n";
import { AppShellHeader } from "@/components/navigation/app-shell-header";
import { Sidebar } from "@/components/navigation/sidebar";
import { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Outlet, useLocation } from "react-router";

// Function to manage AppShell
export function AppShell() {
  const { t } = useTranslation();
  // Variable holding location
  const location = useLocation();
  // Variable holding mobileNavOpen
  const mobileNavOpen = useShellStore((s) => s.mobileNavOpen);
  // Variable holding closeMobileNav
  const closeMobileNav = useShellStore((s) => s.closeMobileNav);
  // Variable holding rtl
  const rtl = isRTL();

  useEffect(() => {
    closeMobileNav();
  }, [location.pathname, closeMobileNav]);

  useEffect(() => {
    if (!mobileNavOpen) return;
    // Function to manage onKeyDown
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeMobileNav();
    };
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKeyDown);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [mobileNavOpen, closeMobileNav]);

  return (
    <div id="container-appShell" className="min-h-dvh bg-background">
      {mobileNavOpen ? (
        <button
          id="button-closeMobileNavOverlay"
          type="button"
          className="fixed inset-0 z-40 bg-overlay lg:hidden"
          aria-label={t("nav.closeMenu")}
          onClick={closeMobileNav}
        />
      ) : null}

      <Sidebar
        className={cn(
          "fixed inset-y-0 z-50 w-[100px] transition-transform duration-200 ease-out",
          "lg:z-30 lg:translate-x-0",
          rtl ? "right-0" : "left-0",
          mobileNavOpen
            ? "translate-x-0"
            : rtl
              ? "translate-x-full lg:translate-x-0"
              : "-translate-x-full lg:translate-x-0",
        )}
      />

      <div
        id="container-appShellContent"
        className={cn(
          "flex h-dvh min-h-dvh flex-col",
          !rtl ? "lg:pe-[100px]" : "lg:ps-[100px]",
        )}
      >
        <AppShellHeader className="z-20 shrink-0" />

        <main
          id="container-appShellMain"
          className="min-h-0 flex-1 overflow-x-hidden overflow-y-auto overscroll-y-contain [scrollbar-gutter:stable]"
        >
          <Outlet />
        </main>
      </div>
    </div>
  );
}
