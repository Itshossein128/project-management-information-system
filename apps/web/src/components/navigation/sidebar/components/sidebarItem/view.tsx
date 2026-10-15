import { useEffect, useMemo, useState } from "react";
import { Link, useLocation } from "react-router";
import { ChevronDown } from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "@/app/lib/utils";
import { ICONS, type IconName } from "@/components/icons";
import type { NavigationChildItem } from "@/types/navigation";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";

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

function normalizePath(path: string): string {
  return `/${path}`.replace(/\/+/g, "/").replace(/\/$/, "") || "/";
}

function matchesPath(pathname: string, path: string): boolean {
  const target = normalizePath(path);
  return pathname === target || pathname.startsWith(`${target}/`);
}

const itemClass = "flex min-h-11 w-full items-center gap-3 rounded-lg px-3 py-2.5 text-start text-sm font-medium text-sidebar-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sidebar-ring motion-reduce:transition-none";
const activeClass = "bg-sidebar-primary text-sidebar-primary-foreground hover:bg-sidebar-primary hover:text-sidebar-primary-foreground";

export const SidebarItem = ({
  name, label, icon, path, activePathPrefix, activePathExclude, activeExact, children,
}: SidebarItemProps) => {
  const { t } = useTranslation();
  const { pathname } = useLocation();
  const Icon = ICONS[icon];
  const navigableChildren = useMemo(
    () => children?.filter((child) => !child.path.includes(":")) ?? [],
    [children],
  );
  // A parent route such as /settings must not compete with /settings/members.
  const currentChild = navigableChildren
    .filter((child) => matchesPath(pathname, child.path))
    .sort((a, b) => b.path.length - a.path.length)[0];
  const active = activePathPrefix
    ? matchesPath(pathname, activePathPrefix) && !(activePathExclude && new RegExp(activePathExclude).test(pathname))
    : activeExact ? normalizePath(pathname) === normalizePath(path) : matchesPath(pathname, path);
  const sectionActive = Boolean(currentChild);
  const [open, setOpen] = useState(sectionActive);

  useEffect(() => {
    setOpen(sectionActive);
  }, [pathname, sectionActive]);

  if (navigableChildren.length) {
    return (
      <Collapsible id={`container-sidebarItem-${name}`} open={open} onOpenChange={setOpen}>
        <CollapsibleTrigger
          id={`button-sidebarExpand-${name}`}
          className={cn(itemClass, sectionActive && "bg-sidebar-accent font-semibold text-sidebar-accent-foreground")}
          onKeyDown={(event) => {
            if (event.key === "Escape" && open) {
              event.stopPropagation();
              setOpen(false);
            }
          }}
        >
          <Icon aria-hidden="true" className="size-5 shrink-0" />
          <span id={`text-sidebarLabel-${name}`} className="min-w-0 flex-1">{label}</span>
          <ChevronDown aria-hidden="true" className={cn("size-4 shrink-0 transition-transform motion-reduce:transition-none", open && "rotate-180")} />
        </CollapsibleTrigger>
        <CollapsibleContent id={`list-sidebarSubnav-${name}`}>
          <ul aria-label={label} className="ms-5 mt-1 flex flex-col gap-0.5 border-s border-sidebar-border ps-3">
            {navigableChildren.map((child, index) => (
              <li key={child.path}>
                <Link
                  id={`button-sidebarSubnav-${name}-${index}`}
                  to={normalizePath(child.path)}
                  aria-current={currentChild === child ? "page" : undefined}
                  className={cn(itemClass, "text-[13px] font-normal", currentChild === child && activeClass)}
                >
                  {child.labelI18nKey ? t(child.labelI18nKey, { defaultValue: child.label }) : child.label}
                </Link>
              </li>
            ))}
          </ul>
        </CollapsibleContent>
      </Collapsible>
    );
  }

  return (
    <div id={`container-sidebarItem-${name}`}>
      <Link
        id={`button-sidebarNav-${name}`}
        to={normalizePath(path)}
        className={cn(itemClass, active && activeClass)}
        aria-current={active ? normalizePath(pathname) === normalizePath(path) ? "page" : "location" : undefined}
      >
        <Icon aria-hidden="true" className="size-5 shrink-0" />
        <span id={`text-sidebarLabel-${name}`}>{label}</span>
      </Link>
    </div>
  );
};
