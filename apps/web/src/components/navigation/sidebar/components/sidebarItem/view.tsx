import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { NavLink, useLocation } from "react-router";
import { ChevronDown } from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "@/app/lib/utils";
import { isRTL } from "@/app/lib/i18n";
import { ICONS, type IconName } from "@/components/icons";
import type { NavigationChildItem } from "@/types/navigation";

export interface SidebarItemProps {
  name: string;
  label: string;
  icon: IconName;
  path: string;
  activePathPrefix?: string;
  activePathExclude?: string;
  activeExact?: boolean;
  children?: NavigationChildItem[];
}

function isNavActive(
  pathname: string,
  path: string,
  options: {
    activePathPrefix?: string;
    activePathExclude?: string;
    activeExact?: boolean;
  },
): boolean {
  const base = `/${path}`.replace(/\/+/g, "/") || "/";

  if (options.activePathPrefix) {
    const prefix =
      `/${options.activePathPrefix}`.replace(/\/+/g, "/") || "/";
    const prefixMatches =
      pathname === prefix || pathname.startsWith(`${prefix}/`);
    if (!prefixMatches) return false;
    if (options.activePathExclude) {
      const re = new RegExp(options.activePathExclude);
      if (re.test(pathname)) return false;
    }
    return true;
  }

  if (options.activeExact) {
    return pathname === base || pathname === `${base}/`;
  }

  return pathname === base || pathname.startsWith(`${base}/`);
}

function childPathIsNavigable(path: string): boolean {
  return !path.includes(":");
}

function normalizeNavPath(path: string): string {
  return `/${path}`.replace(/\/+/g, "/");
}

function isChildRouteActive(pathname: string, childPath: string): boolean {
  const childTo = normalizeNavPath(childPath);
  return pathname === childTo || pathname.startsWith(`${childTo}/`);
}

const itemBaseClass =
  "group flex min-h-[72px] flex-col items-center justify-center gap-1 rounded-xl px-1.5 py-2 text-center text-xs font-medium text-sidebar-foreground transition-all duration-200 ease-[cubic-bezier(0.2,0,0,1)] hover:-translate-y-0.5 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground focus-visible:ring-2 focus-visible:ring-sidebar-ring focus-visible:outline-none";

const itemActiveClass =
  "bg-gradient-to-br from-brand-500 to-brand-700 text-white shadow-[var(--shadow-glow-sm)] ring-1 ring-white/15";

const iconClass =
  "size-7 shrink-0 opacity-90 transition-transform duration-200 group-hover:scale-110";

interface FlyoutCoords {
  top: number;
  left?: number;
  right?: number;
  maxHeight: number;
}

export const SidebarItem = ({
  name,
  label,
  icon,
  path,
  activePathPrefix,
  activePathExclude,
  activeExact,
  children,
}: SidebarItemProps) => {
  const { t } = useTranslation();
  const location = useLocation();
  const Icon = ICONS[icon];

  const to = normalizeNavPath(path);

  const active = useMemo(
    () =>
      isNavActive(location.pathname, path, {
        activePathPrefix,
        activePathExclude,
        activeExact,
      }),
    [location.pathname, path, activePathPrefix, activePathExclude, activeExact],
  );

  const hasChildren = Boolean(children?.length);
  const navigableChildren =
    children?.filter((c) => childPathIsNavigable(c.path)) ?? [];

  const childActive = useMemo(
    () =>
      (children ?? [])
        .filter((c) => childPathIsNavigable(c.path))
        .some((c) => isChildRouteActive(location.pathname, c.path)),
    [location.pathname, children],
  );

  const [open, setOpen] = useState(false);
  const [coords, setCoords] = useState<FlyoutCoords>({ top: 0, maxHeight: 0 });
  const rowRef = useRef<HTMLDivElement>(null);
  const flyoutRef = useRef<HTMLDivElement>(null);
  const closeTimer = useRef<number | null>(null);

  const positionFlyout = useCallback(() => {
    const el = rowRef.current;
    if (!el || typeof window === "undefined") return;
    const rect = el.getBoundingClientRect();
    const gap = 8;
    const margin = 12;
    const top = Math.max(margin, rect.top);
    const base = { top, maxHeight: window.innerHeight - top - margin };
    // Flyout opens toward the content area (inline-start of the rail).
    setCoords(
      isRTL()
        ? { ...base, right: window.innerWidth - rect.left + gap }
        : { ...base, left: rect.right + gap },
    );
  }, []);

  const cancelClose = useCallback(() => {
    if (closeTimer.current) {
      window.clearTimeout(closeTimer.current);
      closeTimer.current = null;
    }
  }, []);

  const openFlyout = useCallback(() => {
    cancelClose();
    positionFlyout();
    setOpen(true);
  }, [cancelClose, positionFlyout]);

  const scheduleClose = useCallback(() => {
    cancelClose();
    closeTimer.current = window.setTimeout(() => setOpen(false), 140);
  }, [cancelClose]);

  // Close the flyout whenever the route changes.
  useEffect(() => {
    setOpen(false);
  }, [location.pathname]);

  // While open: close on Escape / outside click, and keep it anchored.
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    const onPointerDown = (e: MouseEvent) => {
      const target = e.target as Node;
      if (rowRef.current?.contains(target)) return;
      if (flyoutRef.current?.contains(target)) return;
      setOpen(false);
    };
    const onReflow = () => positionFlyout();
    window.addEventListener("keydown", onKey);
    window.addEventListener("mousedown", onPointerDown);
    window.addEventListener("resize", onReflow);
    window.addEventListener("scroll", onReflow, true);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("mousedown", onPointerDown);
      window.removeEventListener("resize", onReflow);
      window.removeEventListener("scroll", onReflow, true);
    };
  }, [open, positionFlyout]);

  useEffect(() => () => cancelClose(), [cancelClose]);

  if (hasChildren && navigableChildren.length > 0) {
    const parentHighlighted = active || childActive;
    return (
      <div id={`container-sidebarItem-${name}`} className="px-2 pb-1">
        <div
          ref={rowRef}
          className="flex items-stretch gap-0.5"
          onMouseEnter={openFlyout}
          onMouseLeave={scheduleClose}
        >
          <NavLink
            id={`button-sidebarNav-${name}`}
            to={to}
            end={Boolean(activeExact)}
            className={cn(
              itemBaseClass,
              "flex-1",
              parentHighlighted && itemActiveClass,
            )}
          >
            <Icon aria-hidden className={iconClass} />
            <span id={`text-sidebarLabel-${name}`} className="leading-tight">
              {label}
            </span>
          </NavLink>
          <button
            id={`button-sidebarExpand-${name}`}
            type="button"
            aria-expanded={open}
            aria-haspopup="menu"
            aria-label={open ? t("nav.closeSubmenu") : t("nav.openSubmenu")}
            className={cn(
              "flex w-7 shrink-0 items-center justify-center rounded-lg border border-transparent text-sidebar-foreground/80 transition-colors",
              "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
              "focus-visible:ring-2 focus-visible:ring-sidebar-ring focus-visible:outline-none",
              open && "bg-sidebar-accent text-sidebar-accent-foreground",
            )}
            onClick={() => (open ? setOpen(false) : openFlyout())}
          >
            <ChevronDown
              className={cn(
                "size-4 transition-transform duration-200",
                open && "-rotate-90",
              )}
            />
          </button>
        </div>

        {open && typeof document !== "undefined"
          ? createPortal(
              <div
                ref={flyoutRef}
                role="menu"
                aria-label={label}
                onMouseEnter={cancelClose}
                onMouseLeave={scheduleClose}
                style={{
                  position: "fixed",
                  top: coords.top,
                  left: coords.left,
                  right: coords.right,
                  maxHeight: coords.maxHeight,
                }}
                className="animate-scale-in z-[70] flex w-56 origin-top flex-col overflow-y-auto rounded-xl border border-border bg-popover p-1.5 text-popover-foreground shadow-[var(--shadow-lg)]"
              >
                <div className="px-2 pb-1.5 pt-1 text-xs font-semibold tracking-wide text-muted-foreground">
                  {label}
                </div>
                <ul className="flex flex-col gap-0.5">
                  {navigableChildren.map((child, index) => (
                    <li key={`${child.path}-${index}`}>
                      <NavLink
                        id={`button-sidebarSubnav-${name}-${index}`}
                        role="menuitem"
                        to={normalizeNavPath(child.path)}
                        onClick={() => setOpen(false)}
                        className={({ isActive }) =>
                          cn(
                            "block rounded-lg px-2.5 py-2 text-sm leading-snug transition-colors",
                            "text-foreground/85 hover:bg-muted hover:text-foreground",
                            "focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none",
                            isActive &&
                              "bg-gradient-to-br from-brand-500/15 to-brand-700/10 font-medium text-brand-700 dark:text-brand-300",
                          )
                        }
                      >
                        {child.label}
                      </NavLink>
                    </li>
                  ))}
                </ul>
              </div>,
              document.body,
            )
          : null}
      </div>
    );
  }

  return (
    <div id={`container-sidebarItem-${name}`} className="px-2 pb-1">
      <NavLink
        id={`button-sidebarNav-${name}`}
        to={to}
        end={Boolean(activeExact)}
        className={cn(itemBaseClass, active && itemActiveClass)}
        aria-current={active ? "page" : undefined}
      >
        <Icon aria-hidden className={iconClass} />
        <span id={`text-sidebarLabel-${name}`} className="leading-tight">
          {label}
        </span>
      </NavLink>
    </div>
  );
};
