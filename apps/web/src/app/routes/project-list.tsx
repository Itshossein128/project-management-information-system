import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowUpRight,
  ChevronLeft,
  ChevronRight,
  FolderKanban,
  LayoutDashboard,
  Plus,
  ReceiptText,
  Search,
  Wallet,
  X,
} from "lucide-react";
import { Link, useSearchParams } from "react-router";
import { useTranslation } from "react-i18next";
import { fetchPortfolioSummary } from "@/app/lib/api/central-data";
import { fetchProjects, type ProjectListItem } from "@/app/lib/api/projects";
import { formatDisplayDate } from "@/app/lib/jalali-utils";
import { PATHS } from "@/app/routeVars";
import {
  Badge,
  projectStatusBadge,
  projectStatusI18nKey,
} from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/form/Input";
import { Select } from "@/components/form/Select";
import { DataTable } from "@/components/ui/data-table";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/layout/empty-state";
import { Breadcrumb, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";

const overview = (project: ProjectListItem) =>
  `/${PATHS.PROJECT}/${project.project_id}/${PATHS.PROJECT_OVERVIEW}`;

export default function ProjectListPage() {
  const { t, i18n } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();
  const search = searchParams.get("search")?.trim() ?? "";
  const status = searchParams.get("status") ?? "";
  const rawPage = Number(searchParams.get("page") ?? 1);
  const page = Number.isSafeInteger(rawPage) && rawPage > 0 ? rawPage : 1;
  const rawSize = Number(searchParams.get("page_size") ?? 20);
  const pageSize = [10, 20, 50].includes(rawSize) ? rawSize : 20;
  const [searchInput, setSearchInput] = useState(search);
  useEffect(() => setSearchInput(search), [search]);
  const number = (value: number) => value.toLocaleString(i18n.language);

  const updateParams = (changes: Record<string, string>) => {
    const next = new URLSearchParams(searchParams);
    next.delete("page");
    for (const [key, value] of Object.entries(changes)) {
      if (value) next.set(key, value);
      else next.delete(key);
    }
    setSearchParams(next);
  };
  const resetFilters = () => {
    setSearchInput("");
    updateParams({ search: "", status: "" });
  };
  const filtersActive = Boolean(search || status);
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["projects", { search, status, page, pageSize }],
    queryFn: () => fetchProjects({ search, status, page, page_size: pageSize }),
  });
  const {
    data: portfolio,
    isPending: portfolioPending,
    isError: portfolioError,
    refetch: refetchPortfolio,
  } = useQuery({
    queryKey: ["portfolio-summary"],
    queryFn: fetchPortfolioSummary,
  });
  const projects = data?.results ?? [];
  const count = data?.count ?? 0;
  const totalPages = Math.max(1, Math.ceil(count / pageSize));
  const rangeStart = projects.length ? (page - 1) * pageSize + 1 : 0;
  const rangeEnd = projects.length ? rangeStart + projects.length - 1 : 0;
  const columns = [
    {
      key: "project_code",
      label: t("project.code"),
      render: (row: ProjectListItem) => (
        <bdi className="font-mono text-xs text-muted-foreground">
          {row.project_code}
        </bdi>
      ),
    },
    {
      key: "project_name",
      label: t("project.name"),
      render: (row: ProjectListItem) => (
        <Link
          to={overview(row)}
          className="rounded-sm font-semibold text-foreground underline-offset-4 hover:text-primary hover:underline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-ring"
        >
          {row.project_name}
        </Link>
      ),
    },
    { key: "employer", label: t("project.employer") },
    {
      key: "status",
      label: t("project.status"),
      render: (row: ProjectListItem) => (
        <Badge
          className="whitespace-nowrap"
          variant={projectStatusBadge[row.status] ?? "neutral"}
          label={t(projectStatusI18nKey[row.status] ?? row.status)}
        />
      ),
    },
    {
      key: "start_date",
      label: t("project.startDate"),
      render: (row: ProjectListItem) => (
        <bdi className="whitespace-nowrap tabular-nums">
          {formatDisplayDate(row.start_date)}
        </bdi>
      ),
    },
    {
      key: "planned_finish_date",
      label: t("project.plannedFinish"),
      render: (row: ProjectListItem) => (
        <bdi className="whitespace-nowrap tabular-nums">
          {formatDisplayDate(row.planned_finish_date)}
        </bdi>
      ),
    },
    {
      key: "contract_amount",
      label: t("project.contractAmount"),
      render: (row: ProjectListItem) =>
        row.contract_amount == null ? (
          "—"
        ) : (
          <span className="inline-flex flex-wrap items-baseline gap-1 tabular-nums">
            <bdi>{number(Number(row.contract_amount))}</bdi>
            {row.currency ? (
              <span className="text-xs text-muted-foreground">
                {row.currency}
              </span>
            ) : null}
          </span>
        ),
    },
    {
      key: "actions",
      label: "",
      render: (row: ProjectListItem) => (
        <Link
          to={overview(row)}
          aria-label={t("project.list.openProject", { name: row.project_name })}
          className={buttonVariants({
            variant: "ghost",
            size: "sm",
            className: "min-h-10",
          })}
        >
          {t("project.view")}
          <ArrowUpRight
            className="size-4 rtl:-scale-x-100"
            aria-hidden="true"
          />
        </Link>
      ),
    },
  ];

  const pagination = (position: string) => (
    <nav
      aria-label={t("project.list.pagination")}
      className="flex flex-wrap items-center justify-between gap-3"
      data-testid={`project-pagination-${position}`}
    >
      <p
        className="text-sm text-muted-foreground"
        aria-live="polite"
        aria-atomic="true"
      >
        {t("project.list.showing", {
          from: number(rangeStart),
          to: number(rangeEnd),
          total: number(count),
        })}
      </p>
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          className="min-h-10"
          disabled={isLoading || !data?.previous}
          onClick={() => updateParams({ page: String(page - 1) })}
        >
          <ChevronLeft className="size-4 rtl:rotate-180" aria-hidden="true" />
          {t("project.list.previous")}
        </Button>
        <span dir="ltr" className="whitespace-nowrap px-1 text-xs tabular-nums">
          {t("project.list.page", {
            page: number(page),
            total: number(totalPages),
          })}
        </span>
        <Button
          variant="outline"
          className="min-h-10"
          disabled={isLoading || !data?.next}
          onClick={() => updateParams({ page: String(page + 1) })}
        >
          {t("project.list.next")}
          <ChevronRight className="size-4 rtl:rotate-180" aria-hidden="true" />
        </Button>
      </div>
    </nav>
  );

  return (
    <main className="page-main page-shell mx-auto px-4 py-8">
      <Breadcrumb items={[{ label: t("project.title") }]} />
      <PageHeader
        title={t("project.title")}
        subtitle={t("project.subtitle")}
        actions={
          <Link
            className={buttonVariants({ className: "min-h-10" })}
            to={`/${PATHS.PROJECT}/${PATHS.PROJECT_NEW}`}
          >
            <Plus className="size-4" aria-hidden="true" />
            {t("project.create")}
          </Link>
        }
      />

      <section
        className="mb-6 space-y-3"
        data-testid="portfolio-summary"
        aria-label={t("project.list.overview")}
        aria-busy={portfolioPending}
      >
        <dl className="grid gap-3 sm:grid-cols-3">
          <div className="rounded-xl border border-border/80 bg-card p-4 shadow-sm">
            <dt className="flex items-center gap-2 text-sm text-muted-foreground">
              <FolderKanban
                className="size-4 text-primary"
                aria-hidden="true"
              />
              {t("project.list.portfolioProjects")}
            </dt>
            <dd className="mt-3 flex min-h-9 items-center text-3xl font-semibold tabular-nums tracking-tight">
              {portfolioPending ? (
                <Skeleton
                  className="h-9 w-24 bg-muted motion-reduce:animate-none"
                  aria-hidden="true"
                />
              ) : portfolioError ? (
                <Button
                  variant="ghost"
                  className="h-9 px-0"
                  onClick={() => void refetchPortfolio()}
                  title={t("common.loadFailed")}
                >
                  {t("common.retry")}
                </Button>
              ) : (
                number(portfolio?.totals.project_count ?? 0)
              )}
            </dd>
          </div>
          {(
            [
              {
                key: "total_budget",
                label: "centralData.budget",
                icon: Wallet,
              },
              {
                key: "total_actual",
                label: "glossary.actualCost",
                icon: ReceiptText,
              },
            ] as const
          ).map(({ key, label, icon: Icon }) => (
            <div
              key={key}
              className="rounded-xl border border-border/80 bg-card p-4 shadow-sm"
            >
              <dt className="flex items-center gap-2 text-sm text-muted-foreground">
                <Icon className="size-4 text-primary" aria-hidden="true" />
                {t(label)}
                <span className="ms-auto rounded bg-muted px-2 py-0.5 text-xs font-medium">
                  IRR
                </span>
              </dt>
              <dd className="mt-3 break-words text-3xl font-semibold tabular-nums tracking-tight">
                {portfolioPending ? (
                  <Skeleton
                    className="h-9 w-32 max-w-full bg-muted motion-reduce:animate-none"
                    aria-hidden="true"
                  />
                ) : portfolioError ? (
                  "—"
                ) : (
                  <bdi>
                    {number(
                      Number(portfolio?.totals_by_currency.IRR?.[key] ?? 0),
                    )}
                  </bdi>
                )}
              </dd>
            </div>
          ))}
        </dl>
        <div className="flex flex-wrap gap-x-5 gap-y-2">
          <Link
            className="inline-flex min-h-10 items-center gap-2 rounded-md text-sm font-medium text-primary underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-ring"
            to={`/${PATHS.EXECUTIVE_DASHBOARD}`}
            data-testid="portfolio-dashboard-link"
          >
            <LayoutDashboard className="size-4" aria-hidden="true" />
            {t("dashboard.executiveTitle")}
            <ArrowUpRight
              className="size-3.5 rtl:-scale-x-100"
              aria-hidden="true"
            />
          </Link>
          <Link
            className="inline-flex min-h-10 items-center gap-2 rounded-md text-sm font-medium text-primary underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-ring"
            to={`/${PATHS.PORTFOLIO_LIQUIDITY}`}
            data-testid="portfolio-liquidity-link"
          >
            <Wallet className="size-4" aria-hidden="true" />
            {t("pages.portfolioLiquidity.title")}
            <ArrowUpRight
              className="size-3.5 rtl:-scale-x-100"
              aria-hidden="true"
            />
          </Link>
        </div>
      </section>

      <section aria-label={t("project.list.directory")} className="space-y-4">
        <div className="rounded-xl border border-border/80 bg-card p-4 shadow-sm">
          <form
            role="search"
            aria-label={t("project.list.searchLabel")}
            onSubmit={(event) => {
              event.preventDefault();
              updateParams({ search: searchInput.trim() });
            }}
            className="flex flex-col gap-3 lg:flex-row lg:items-end"
          >
            <div className="min-w-0 flex-1">
              <label
                htmlFor="project-search"
                className="mb-1.5 block text-sm font-medium"
              >
                {t("project.list.searchLabel")}
              </label>
              <div className="relative">
                <Search
                  className="pointer-events-none absolute start-3 top-3 size-4 text-muted-foreground"
                  aria-hidden="true"
                />
                <Input
                  id="project-search"
                  type="search"
                  name="search"
                  value={searchInput}
                  onChange={(event) => setSearchInput(event.target.value)}
                  placeholder={t("project.list.searchPlaceholder")}
                  className="h-10 ps-9"
                />
              </div>
            </div>
            <div className="w-full lg:w-44">
              <Select
                name="project-status"
                label={t("project.status")}
                value={status || "all"}
                onChange={(event) =>
                  updateParams({
                    status:
                      event.target.value === "all" ? "" : event.target.value,
                  })
                }
                className="min-h-10"
                options={[
                  { value: "all", label: t("project.list.allStatuses") },
                  ...Object.entries(projectStatusI18nKey).map(
                    ([value, key]) => ({ value, label: t(key) }),
                  ),
                ]}
              />
            </div>
            <Button type="submit" className="min-h-10">
              <Search className="size-4" aria-hidden="true" />
              {t("common.search")}
            </Button>
            {filtersActive ? (
              <Button
                type="button"
                variant="ghost"
                className="min-h-10"
                onClick={resetFilters}
              >
                <X className="size-4" aria-hidden="true" />
                {t("project.list.clearFilters")}
              </Button>
            ) : null}
          </form>
        </div>

        {isError ? (
          <QueryErrorState onRetry={() => void refetch()} />
        ) : !isLoading && count === 0 ? (
          <EmptyState
            icon={filtersActive ? <Search /> : <FolderKanban />}
            title={t(
              filtersActive ? "project.list.noMatches" : "project.empty",
            )}
            description={t(
              filtersActive
                ? "project.list.noMatchesHint"
                : "project.list.emptyHint",
            )}
            action={
              filtersActive ? (
                <Button variant="outline" onClick={resetFilters}>
                  {t("project.list.clearFilters")}
                </Button>
              ) : (
                <Link
                  className={buttonVariants()}
                  to={`/${PATHS.PROJECT}/${PATHS.PROJECT_NEW}`}
                >
                  {t("project.create")}
                </Link>
              )
            }
          />
        ) : (
          <>
            <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Select
                  name="project-page-size"
                  label={t("project.list.perPage")}
                  value={String(pageSize)}
                  onChange={(event) =>
                    updateParams({ page_size: event.target.value })
                  }
                  className="min-h-10 w-20"
                  fieldClassName="flex items-center gap-3 whitespace-nowrap"
                  options={[10, 20, 50].map((size) => ({
                    value: String(size),
                    label: number(size),
                  }))}
                />
              </div>
              {data ? pagination("top") : null}
            </div>
            <div aria-busy={isLoading} data-testid="project-results">
              <DataTable
                columns={columns}
                data={projects}
                loading={isLoading}
                rowKey={(row) => row.project_id}
              />
            </div>
            {data && count > pageSize ? pagination("bottom") : null}
          </>
        )}
      </section>
    </main>
  );
}
