import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router";
import { ChevronDown, Loader2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { fetchProject } from "@/app/lib/api/projects";
import { isRTL } from "@/app/lib/i18n";
import { cn } from "@/app/lib/utils";
import { ICONS } from "@/components/icons";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { useProjectNavigation } from "./hooks/useNavigation";

const toPath = (path: string) => `/${path}`.replace(/\/+/g, "/");

/** Local navigation has its own landmark; the global sidebar never changes. */
export function ProjectNavigation() {
  const { t } = useTranslation();
  const { pathname } = useLocation();
  const { projectId, items, capabilities } = useProjectNavigation();
  const [openSection, setOpenSection] = useState<string | null>(null);
  const { data: project } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => fetchProject(projectId!),
    enabled: Boolean(projectId),
    staleTime: 30_000,
  });

  useEffect(() => { setOpenSection(null); }, [pathname]);
  if (!projectId) return null;

  return (
    <nav id="nav-projectNavigation" aria-label={t("nav.projectNavigation")} className="sticky top-0 z-10 border-b border-border bg-card px-4 py-3 sm:px-6">
      <div className="mb-2 flex min-w-0 items-center gap-2 text-xs">
        <span className="shrink-0 font-semibold text-muted-foreground">{t("nav.section.project")}</span>
        <span aria-hidden="true" className="text-muted-foreground">/</span>
        <span className="truncate font-medium" title={project?.project_name}>{project?.project_name ?? t("nav.projectWorkspace")}</span>
      </div>
      <ul className="flex items-center gap-1 overflow-x-auto pb-1">
        {items.map((item) => {
          const label = item.labelI18nKey ? t(item.labelI18nKey, { defaultValue: item.label }) : item.label;
          const Icon = ICONS[item.icon];
          const children = item.children?.filter((child) => !child.path.includes(":")) ?? [];
          const currentChild = children.filter((child) => pathname === toPath(child.path) || (!child.activeExact && pathname.startsWith(`${toPath(child.path)}/`))).sort((a, b) => b.path.length - a.path.length)[0];
          return (
            <li key={item.labelI18nKey ?? item.path} className="shrink-0">
              <Popover open={openSection === item.path} onOpenChange={(open) => setOpenSection(open ? item.path : null)}>
                <PopoverTrigger asChild>
                  <button type="button" aria-current={currentChild ? "location" : undefined} className={cn("flex min-h-11 items-center gap-2 rounded-lg px-3 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring motion-reduce:transition-none", currentChild && "bg-accent text-accent-foreground")}>
                    <Icon aria-hidden="true" className="size-4" />
                    {label}
                    <ChevronDown aria-hidden="true" className="size-3.5" />
                  </button>
                </PopoverTrigger>
                <PopoverContent aria-label={label} dir={isRTL() ? "rtl" : "ltr"} align={isRTL() ? "end" : "start"} className="max-h-[min(70dvh,var(--radix-popover-content-available-height))] w-64 overflow-y-auto p-1.5 motion-reduce:animate-none">
                  {capabilities.isPending ? (
                    <p role="status" className="flex min-h-11 items-center gap-2 px-3 text-sm text-muted-foreground"><Loader2 className="size-4 animate-spin" aria-hidden="true" />{t("common.loading")}</p>
                  ) : capabilities.isError ? (
                    <div className="space-y-2 p-3 text-sm">
                      <p role="status">{t("nav.projectNavigationError")}</p>
                      <button type="button" onClick={() => void capabilities.refetch()} className="min-h-11 rounded-md px-3 underline focus-visible:ring-2 focus-visible:ring-ring">{t("common.retry")}</button>
                    </div>
                  ) : (
                    <ul aria-label={label} className="space-y-0.5">
                      {children.map((child) => (
                        <li key={child.path}>
                          <Link to={toPath(child.path)} onClick={() => setOpenSection(null)} aria-current={currentChild === child ? "page" : undefined} className={cn("flex min-h-11 items-center rounded-md px-3 py-2 text-sm hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring", currentChild === child && "bg-primary font-medium text-primary-foreground hover:bg-primary")}>
                            {child.labelI18nKey ? t(child.labelI18nKey, { defaultValue: child.label }) : child.label}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  )}
                </PopoverContent>
              </Popover>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
