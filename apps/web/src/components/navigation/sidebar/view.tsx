import { Link } from "react-router";
import { X } from "lucide-react";
import { useAuth } from "@/app/contexts/auth-context";
import { cn } from "@/app/lib/utils";
import { useTranslation } from "react-i18next";
import { useNavigation } from "../hooks/useNavigation";
import { SidebarItem } from "./components/sidebarItem";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

export interface SidebarProps {
  className?: string;
  onClose?: () => void;
}

export const Sidebar = ({ className, onClose }: SidebarProps) => {
  const { user } = useAuth();
  const { t } = useTranslation();
  const items = useNavigation(user?.roles);
  const sections = ["workspace", "administration"] as const;

  return (
    <aside
      id="container-mainSidebar"
      className={cn("flex h-dvh flex-col border-e border-sidebar-border bg-sidebar text-sidebar-foreground", className)}
    >
      <div id="container-sidebarBrand" className="flex shrink-0 items-center gap-3 border-b border-sidebar-border px-5 py-3">
        <Link to="/projects" className="flex min-w-0 flex-1 items-center gap-3 rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sidebar-ring" aria-label={t("nav.sidebarProjects")}>
          <span id="text-sidebarBrandMark" className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-brand-600 to-safety-700 font-semibold text-white shadow-sm" aria-hidden="true">V</span>
          <span className="min-w-0">
            <span id="text-sidebarBrandTitle" className="block text-lg font-bold">{t("common.brandName", { defaultValue: "Velora" })}</span>
            <span className="block text-xs text-muted-foreground">{t("nav.workspaceSubtitle")}</span>
          </span>
        </Link>
        {onClose ? (
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                type="button"
                onClick={onClose}
                aria-label={t("nav.closeMenu")}
                className="flex size-11 shrink-0 items-center justify-center rounded-lg hover:bg-sidebar-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sidebar-ring"
              >
                <X className="size-5" aria-hidden="true" />
              </button>
            </TooltipTrigger>
            <TooltipContent>{t("nav.closeMenu")}</TooltipContent>
          </Tooltip>
        ) : null}
      </div>
      <nav id="nav-mainSidebar" className="flex min-h-0 flex-1 flex-col gap-5 overflow-y-auto px-3 py-5 [scrollbar-gutter:stable]" aria-label={t("nav.main")}>
        {sections.map((section) => {
          const sectionItems = items.filter((item) => (item.section ?? "workspace") === section);
          if (!sectionItems.length) return null;
          return (
            <section key={section} aria-labelledby={`text-navSection-${section}`} className={cn(section === "administration" && "border-t border-sidebar-border pt-4")}>
              <h2 id={`text-navSection-${section}`} className="mb-2 px-3 text-xs font-semibold text-muted-foreground">{t(`nav.section.${section}`)}</h2>
              <ul id={`list-sidebarNav-${section}`} className="flex flex-col gap-1">
                {sectionItems.map((item) => (
                  <li key={item.path}>
                    <SidebarItem {...item} name={`${section}-${item.path.replace(/[^a-z0-9-]/gi, "-")}`} label={item.labelI18nKey ? t(item.labelI18nKey, { defaultValue: item.label }) : item.label} />
                  </li>
                ))}
              </ul>
            </section>
          );
        })}
      </nav>
    </aside>
  );
};
