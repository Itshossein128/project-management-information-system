import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowUpRight,
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  CircleHelp,
  FolderKanban,
  RefreshCw,
  Search,
  X,
} from "lucide-react";
import { Link, useSearchParams } from "react-router";
import { useTranslation } from "react-i18next";
import {
  fetchPortfolioDashboard,
  figureTitleKey,
  type DashboardFigure,
} from "@/app/lib/api/dashboards";
import { PATHS } from "@/app/routeVars";
import { DashboardFigureGrid } from "@/components/dashboard/DashboardFigureGrid";
import { FigureDrillDrawer } from "@/components/dashboard/FigureDrillDrawer";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { EmptyState } from "@/components/layout/empty-state";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Input } from "@/components/form/Input";
import { Button, buttonVariants } from "@/components/ui/button";

const PAGE_SIZE = 6;

export default function ExecutiveDashboardPage() {
  const { t, i18n } = useTranslation();
  const [params, setParams] = useSearchParams();
  const search = params.get("search") ?? "";
  const requestedPage = Number(params.get("page") ?? 1);
  const [drill, setDrill] = useState<{
    projectId: string;
    figure: DashboardFigure;
  } | null>(null);
  const { data, isLoading, isFetching, isError, refetch } = useQuery({
    queryKey: ["portfolio-dashboard"],
    queryFn: () => fetchPortfolioDashboard(),
  });
  const filtered = useMemo(
    () =>
      data?.projects.filter((project) =>
        project.project_name
          .toLocaleLowerCase()
          .includes(search.trim().toLocaleLowerCase()),
      ) ?? [],
    [data, search],
  );
  const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const page =
    Number.isSafeInteger(requestedPage) && requestedPage > 0
      ? Math.min(requestedPage, pages)
      : 1;
  const projects = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const incompleteCount = useMemo(
    () =>
      data?.projects.filter(
        (project) =>
          !project.figures.length ||
          project.figures.some(
            (figure) => figure.status !== "ok" || figure.value == null,
          ),
      ).length ?? 0,
    [data],
  );
  const number = (value: number) => value.toLocaleString(i18n.language);
  const changeSearch = (value: string) => {
    const next = new URLSearchParams(params);
    next.delete("page");
    if (value) next.set("search", value);
    else next.delete("search");
    setParams(next, { replace: true });
  };
  const changePage = (value: number) => {
    const next = new URLSearchParams(params);
    if (value === 1) next.delete("page");
    else next.set("page", String(value));
    setParams(next);
  };
  const asOf = data?.as_of ? new Date(`${data.as_of}T00:00:00Z`) : null;
  const reportDate =
    asOf && !Number.isNaN(asOf.getTime())
      ? new Intl.DateTimeFormat(i18n.language, {
          dateStyle: "medium",
          timeZone: "UTC",
        }).format(asOf)
      : "—";
  const pagination = (position: string) => (
    <nav
      aria-label={t("dashboard.portfolio.pagination")}
      data-testid={`portfolio-pagination-${position}`}
      className="flex flex-wrap items-center justify-between gap-3"
    >
      <p className="text-sm text-muted-foreground" role="status">
        {t("dashboard.portfolio.showing", {
          from: number((page - 1) * PAGE_SIZE + 1),
          to: number(Math.min(page * PAGE_SIZE, filtered.length)),
          total: number(filtered.length),
        })}
      </p>
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          className="min-h-10"
          onClick={() => changePage(page - 1)}
          disabled={page === 1}
        >
          <ChevronLeft className="size-4 rtl:rotate-180" aria-hidden="true" />
          {t("dashboard.portfolio.previous")}
        </Button>
        <span dir="ltr" className="px-1 text-xs tabular-nums">
          {number(page)} / {number(pages)}
        </span>
        <Button
          variant="outline"
          className="min-h-10"
          onClick={() => changePage(page + 1)}
          disabled={page === pages}
        >
          {t("dashboard.portfolio.next")}
          <ChevronRight className="size-4 rtl:rotate-180" aria-hidden="true" />
        </Button>
      </div>
    </nav>
  );

  return (
    <main className="page-main page-shell mx-auto max-w-7xl px-4 py-8">
      <Breadcrumb
        items={[
          { label: t("nav.projects"), href: `/${PATHS.PROJECT}` },
          { label: t("dashboard.executiveTitle") },
        ]}
      />
      <PageHeader
        title={t("dashboard.executiveTitle")}
        subtitle={t("dashboard.portfolio.subtitle")}
        actions={
          <Button
            variant="outline"
            className="min-h-10"
            onClick={() => void refetch()}
            disabled={isFetching}
          >
            <RefreshCw
              className={`size-4 ${isFetching ? "motion-safe:animate-spin" : ""}`}
              aria-hidden="true"
            />
            {t("dashboard.portfolio.refresh")}
          </Button>
        }
      />

      {isError ? (
        <QueryErrorState onRetry={() => void refetch()} />
      ) : isLoading ? (
        <LoadingSkeleton rows={8} />
      ) : (
        <div className="space-y-6" data-testid="executive-portfolio-dashboard">
          <section aria-label={t("dashboard.portfolio.overview")}>
            <dl className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-xl border border-border/80 bg-card p-4 shadow-sm">
                <dt className="flex items-center gap-2 text-sm text-muted-foreground">
                  <FolderKanban
                    className="size-4 text-primary"
                    aria-hidden="true"
                  />
                  {t("dashboard.portfolio.projects")}
                </dt>
                <dd
                  className="mt-3 text-3xl font-semibold tabular-nums"
                  data-testid="portfolio-project-count"
                >
                  {number(data?.projects.length ?? 0)}
                </dd>
                <dd className="mt-2 text-xs text-muted-foreground">
                  {t("dashboard.portfolio.projectsHint")}
                </dd>
              </div>
              <div className="rounded-xl border border-border/80 bg-card p-4 shadow-sm">
                <dt className="flex items-center gap-2 text-sm text-muted-foreground">
                  <CircleHelp
                    className="size-4 text-primary"
                    aria-hidden="true"
                  />
                  {t("dashboard.portfolio.incomplete")}
                </dt>
                <dd
                  className="mt-3 text-3xl font-semibold tabular-nums"
                  data-testid="portfolio-incomplete-count"
                >
                  {number(incompleteCount)}
                </dd>
                <dd className="mt-2 text-xs text-muted-foreground">
                  {t("dashboard.portfolio.incompleteHint")}
                </dd>
              </div>
              <div className="rounded-xl border border-border/80 bg-card p-4 shadow-sm">
                <dt className="flex items-center gap-2 text-sm text-muted-foreground">
                  <CalendarDays
                    className="size-4 text-primary"
                    aria-hidden="true"
                  />
                  {t("dashboard.portfolio.reportDate")}
                </dt>
                <dd className="mt-3 text-xl font-semibold">
                  <time dateTime={data?.as_of}>{reportDate}</time>
                </dd>
                <dd className="mt-2 text-xs text-muted-foreground">
                  {t("dashboard.portfolio.reportDateHint")}
                </dd>
              </div>
            </dl>
          </section>

          {data?.projects.length ? (
            <>
              <section
                aria-label={t("dashboard.portfolio.searchLabel")}
                className="rounded-xl border border-border/80 bg-card p-4 shadow-sm"
              >
                <label
                  htmlFor="portfolio-search"
                  className="mb-2 block text-sm font-medium"
                >
                  {t("dashboard.portfolio.searchLabel")}
                </label>
                <div className="flex flex-wrap items-center gap-3">
                  <div className="relative min-w-0 flex-1">
                    <Search
                      className="pointer-events-none absolute start-3 top-3 size-4 text-muted-foreground"
                      aria-hidden="true"
                    />
                    <Input
                      id="portfolio-search"
                      type="search"
                      value={search}
                      onChange={(event) => changeSearch(event.target.value)}
                      placeholder={t("dashboard.portfolio.searchPlaceholder")}
                      aria-describedby="portfolio-search-hint"
                      className="h-10 ps-9"
                    />
                  </div>
                  {search ? (
                    <Button
                      variant="ghost"
                      className="min-h-10"
                      onClick={() => changeSearch("")}
                    >
                      <X className="size-4" aria-hidden="true" />
                      {t("dashboard.portfolio.clearSearch")}
                    </Button>
                  ) : null}
                </div>
                <p
                  id="portfolio-search-hint"
                  className="mt-2 text-xs text-muted-foreground"
                >
                  {t("dashboard.portfolio.searchHint")}
                </p>
              </section>
              {projects.length ? (
                <>
                  {pagination("top")}
                  <div
                    className="space-y-5"
                    data-testid="portfolio-project-results"
                  >
                    {projects.map((row) => (
                      <section
                        key={row.project_id}
                        aria-labelledby={`portfolio-project-${row.project_id}`}
                        className="overflow-hidden rounded-xl border border-border/80 bg-card shadow-sm"
                        data-testid="portfolio-project-card"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border/60 bg-muted/20 px-4 py-3">
                          <h2
                            id={`portfolio-project-${row.project_id}`}
                            className="min-w-0 break-words text-base font-semibold"
                          >
                            <bdi>{row.project_name}</bdi>
                          </h2>
                          <Link
                            className={buttonVariants({
                              variant: "outline",
                              size: "sm",
                              className: "min-h-10",
                            })}
                            aria-label={t("dashboard.portfolio.openProject", {
                              name: row.project_name,
                            })}
                            to={`/${PATHS.PROJECT}/${row.project_id}/${PATHS.PROJECT_DASHBOARD}`}
                          >
                            {t("dashboard.openProjectDashboard")}
                            <ArrowUpRight
                              className="size-4 rtl:-scale-x-100"
                              aria-hidden="true"
                            />
                          </Link>
                        </div>
                        <div className="p-4">
                          <DashboardFigureGrid
                            figures={row.figures}
                            onFigureClick={(figure) =>
                              setDrill({ projectId: row.project_id, figure })
                            }
                          />
                        </div>
                      </section>
                    ))}
                  </div>
                  {pages > 1 ? pagination("bottom") : null}
                </>
              ) : (
                <EmptyState
                  icon={<Search />}
                  title={t("dashboard.portfolio.noMatches")}
                  description={t("dashboard.portfolio.noMatchesHint")}
                  action={
                    <Button variant="outline" onClick={() => changeSearch("")}>
                      {t("dashboard.portfolio.clearSearch")}
                    </Button>
                  }
                />
              )}
            </>
          ) : (
            <EmptyState
              icon={<FolderKanban />}
              title={t("dashboard.portfolioEmpty")}
              description={t("dashboard.portfolio.emptyHint")}
              action={
                <Link
                  to={`/${PATHS.PROJECT}`}
                  className={buttonVariants({ variant: "outline" })}
                >
                  {t("nav.projects")}
                </Link>
              }
            />
          )}
        </div>
      )}

      <FigureDrillDrawer
        projectId={drill?.projectId ?? ""}
        figureKey={drill?.figure.figure_key ?? null}
        figureLabel={
          drill
            ? t(
                figureTitleKey(drill.figure.figure_key),
                drill.figure.figure_key,
              )
            : undefined
        }
        asOf={data?.as_of}
        isOpen={Boolean(drill)}
        onClose={() => setDrill(null)}
      />
    </main>
  );
}
