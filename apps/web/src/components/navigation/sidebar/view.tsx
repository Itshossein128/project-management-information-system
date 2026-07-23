import { useAuth } from "@/app/contexts/auth-context";
import { cn } from "@/app/lib/utils";
import { isRTL } from "@/app/lib/i18n";
import { useTranslation } from "react-i18next";
import { useNavigation } from "../hooks/useNavigation";
import { SidebarItem } from "./components/sidebarItem";

export interface SidebarProps {
  className?: string;
}

export const Sidebar = ({ className }: SidebarProps) => {
  const { user } = useAuth();
  const { t } = useTranslation();
  const items = useNavigation(user?.roles).map((item) => ({
    ...item,
    label: item.labelI18nKey
      ? t(item.labelI18nKey, { defaultValue: item.label })
      : item.label,
  }));

  return (
    <aside
      id="container-mainSidebar"
      className={cn(
        "flex h-dvh min-h-dvh flex-col border-sidebar-border bg-sidebar text-sidebar-foreground lg:shadow-[var(--shadow-sm)]",
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
          className="flex size-11 items-center justify-center rounded-xl bg-gradient-to-br from-brand-600 to-safety-700 font-semibold text-white shadow-sm ring-1 ring-sidebar-ring/30"
          aria-hidden
        >
          {t("common.brandShort", { defaultValue: "BM" })}
        </div>
        <span
          id="text-sidebarBrandTitle"
          className="text-[10px] text-sidebar-foreground/55"
        >
          {t("common.brandName", { defaultValue: "Building" })}
        </span>
      </div>

      <nav
        id="nav-mainSidebar"
        className="flex min-h-0 flex-1 flex-col overflow-y-auto overflow-x-hidden py-3"
        aria-label={t("nav.main")}
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
