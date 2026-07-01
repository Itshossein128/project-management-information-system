import { useMemo, useState } from "react";
import { NavLink, useLocation } from "react-router";
import { ChevronDown } from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "@/app/lib/utils";
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
  const base = `/${path}`.replace(/\/+$/, "") || "/";

  if (options.activePathPrefix) {
    const prefix = `/${options.activePathPrefix}`;
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
  const [expanded, setExpanded] = useState(false);

  const to = `/${path}`.replace(/\/+/g, "/");

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

  const itemActiveClass =
    "bg-sidebar-primary text-sidebar-primary-foreground shadow-[var(--shadow-sm)] ring-1 ring-sidebar-ring/30";

  if (hasChildren && navigableChildren.length > 0) {
    return (
      <div id={`container-sidebarItem-${name}`} className="px-2 pb-1">
        <div className="flex flex-col gap-0.5">
          <div className="flex items-stretch gap-0.5">
            <NavLink
              id={`button-sidebarNav-${name}`}
              to={to}
              end={Boolean(activeExact)}
              className={cn(
                "flex min-h-[72px] flex-1 flex-col items-center justify-center gap-1 rounded-xl px-1.5 py-2 text-center text-xs font-medium text-sidebar-foreground transition-colors",
                "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                "focus-visible:ring-2 focus-visible:ring-sidebar-ring focus-visible:outline-none",
                active && itemActiveClass,
              )}
            >
              <Icon aria-hidden className="size-7 shrink-0 opacity-90" />
              <span id={`text-sidebarLabel-${name}`} className="leading-tight">
                {label}
              </span>
            </NavLink>
            <button
              id={`button-sidebarExpand-${name}`}
              type="button"
              aria-expanded={expanded}
              aria-label={
                expanded ? t("nav.closeSubmenu") : t("nav.openSubmenu")
              }
              className={cn(
                "flex w-7 shrink-0 items-center justify-center rounded-lg border border-transparent text-sidebar-foreground/80 transition-colors",
                "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                "focus-visible:ring-2 focus-visible:ring-sidebar-ring focus-visible:outline-none",
              )}
              onClick={() => setExpanded((e) => !e)}
            >
              <ChevronDown
                className={cn(
                  "size-4 transition-transform",
                  expanded && "rotate-180",
                )}
              />
            </button>
          </div>
          {expanded && (
            <ul
              id={`list-sidebarSubnav-${name}`}
              className="border-sidebar-border ms-1 flex flex-col gap-0.5 border-s ps-2"
            >
              {navigableChildren.map((child, index) => (
                <li key={`${child.path}-${index}`}>
                  <NavLink
                    id={`button-sidebarSubnav-${name}-${index}`}
                    to={`/${child.path}`.replace(/\/+/g, "/")}
                    className={({ isActive }) =>
                      cn(
                        "block rounded-md px-2 py-1.5 text-[11px] leading-snug transition-colors",
                        "text-sidebar-foreground/90 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                        "focus-visible:ring-2 focus-visible:ring-sidebar-ring focus-visible:outline-none",
                        isActive &&
                          "bg-sidebar-accent font-medium text-sidebar-accent-foreground",
                      )
                    }
                  >
                    {child.label}
                  </NavLink>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    );
  }

  return (
    <div id={`container-sidebarItem-${name}`} className="px-2 pb-1">
      <NavLink
        id={`button-sidebarNav-${name}`}
        to={to}
        end={Boolean(activeExact)}
        className={cn(
          "flex min-h-[72px] flex-col items-center justify-center gap-1 rounded-xl px-1.5 py-2 text-center text-xs font-medium text-sidebar-foreground transition-colors",
          "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
          "focus-visible:ring-2 focus-visible:ring-sidebar-ring focus-visible:outline-none",
          active && itemActiveClass,
        )}
        aria-current={active ? "page" : undefined}
      >
        <Icon aria-hidden className="size-7 shrink-0 opacity-90" />
        <span id={`text-sidebarLabel-${name}`} className="leading-tight">
          {label}
        </span>
      </NavLink>
    </div>
  );
};
