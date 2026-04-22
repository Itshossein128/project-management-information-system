import { useAuth } from "@/app/contexts/auth-context";
import { cn } from "@/app/lib/utils";
import { isRTL } from "@/app/lib/i18n";
import { useNavigation } from "../hooks/useNavigation";
import { SidebarItem } from "./components/sidebarItem";

export interface SidebarProps {
  className?: string;
}

export const Sidebar = ({ className }: SidebarProps) => {
  const { user } = useAuth();
  const items = useNavigation(user?.roles);

  return (
    <aside
      id="container-mainSidebar"
      className={cn(
        "flex h-full min-h-0 flex-col border-sidebar-border bg-sidebar text-sidebar-foreground shadow-[inset_-1px_0_0_0_var(--sidebar-border)]",
        isRTL() ? "border-l" : "border-r",
        className,
      )}
    >
      <div
        id="container-sidebarBrand"
        className="flex shrink-0 flex-col items-center gap-1 border-sidebar-border border-b px-2 py-4"
      >
        <div
          id="text-sidebarBrandMark"
          className="flex size-11 items-center justify-center rounded-xl bg-sidebar-primary font-semibold text-sidebar-primary-foreground shadow-sm ring-1 ring-sidebar-ring/30"
          aria-hidden
        >
          BM
        </div>
        <span
          id="text-sidebarBrandTitle"
          className="text-[10px] text-sidebar-foreground/55"
        >
          Building
        </span>
      </div>

      <nav
        id="nav-mainSidebar"
        className="flex min-h-0 flex-1 flex-col overflow-y-auto overflow-x-hidden py-3"
        aria-label="اصلی"
      >
        <ul id="list-sidebarNav" className="flex flex-col gap-1">
          {items.map((item, index) => (
            <li key={`${item.path}-${index}`} id={`item-sidebar-${index}`}>
              <SidebarItem
                name={`sidebar-${index}`}
                label={item.label}
                icon={item.icon}
                path={item.path}
                activePathPrefix={item.activePathPrefix}
                activePathExclude={item.activePathExclude}
                activeExact={item.activeExact}
                children={item.children}
              />
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};
