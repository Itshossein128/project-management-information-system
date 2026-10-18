import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";
import {
  ChevronLeft,
  ChevronRight,
  FileBarChart,
  Search,
  X,
} from "lucide-react";
import type { UseQueryResult } from "@tanstack/react-query";
import type { PortfolioReport } from "@/app/lib/api/cashflow";
import { PATHS } from "@/app/routeVars";
import { Input } from "@/components/form/Input";
import { Button } from "@/components/ui/sprint-button";
import { DataTable } from "@/components/ui/data-table";
import { EmptyState } from "@/components/layout/empty-state";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { LoadingSkeleton } from "@/components/layout/page-header";

const PAGE_SIZE = 10;
type ReportRow = PortfolioReport["projects"][number];
export function PortfolioCashReport({
  report,
  period,
}: {
  report: UseQueryResult<PortfolioReport, Error>;
  period: string;
}) {
  const { t, i18n } = useTranslation();
  const [search, setSearch] = useState("");
  const [requestedPage, setPage] = useState(1);
  const filtered =
    report.data?.projects.filter((row) =>
      row.project_name
        .toLocaleLowerCase()
        .includes(search.trim().toLocaleLowerCase()),
    ) ?? [];
  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const page = Math.min(requestedPage, totalPages);
  const rows = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const number = (value: number) => value.toLocaleString(i18n.language);
  const amount = (value: number) => (
    <bdi className="tabular-nums">{number(value)}</bdi>
  );
  const columns = [
    {
      key: "project_name",
      label: t("pages.portfolioLiquidity.project"),
      render: (row: ReportRow) => (
        <Link
          className="rounded-sm font-medium text-foreground underline decoration-primary/40 underline-offset-4 hover:decoration-primary focus-visible:outline-2 focus-visible:outline-ring"
          to={`/${PATHS.PROJECT}/${row.project_id}/${PATHS.PROJECT_CASH_FLOW}`}
        >
          <bdi>{row.project_name}</bdi>
        </Link>
      ),
    },
    {
      key: "projected_inflow",
      label: t("pages.cashFlow.projectedInflow"),
      render: (row: ReportRow) =>
        row.inflow_status === "unregistered" ? (
          <span className="text-xs text-muted-foreground">
            {t("pages.cashFlow.noScheduledReceipts")}
          </span>
        ) : (
          amount(row.projected_inflow)
        ),
    },
    {
      key: "projected_outflow",
      label: t("pages.cashFlow.projectedOutflow"),
      render: (row: ReportRow) => amount(row.projected_outflow),
    },
    {
      key: "suggested_net_need",
      label: t("pages.cashFlow.suggestedNetNeed"),
      render: (row: ReportRow) => amount(row.suggested_net_need),
    },
    {
      key: "composite",
      label: t("pages.portfolioLiquidity.composite"),
      render: (row: ReportRow) =>
        row.composite == null ? "—" : amount(row.composite),
    },
  ];
  return (
    <section
      className="space-y-4 rounded-xl border border-border/80 bg-card p-4 shadow-sm sm:p-5"
      aria-labelledby="liquidity-report-title"
    >
      <div>
        <h2
          id="liquidity-report-title"
          className="flex items-center gap-2 text-lg font-semibold"
        >
          <FileBarChart className="size-5 text-primary" aria-hidden="true" />
          {t("pages.portfolioLiquidity.reportTitle")}
        </h2>
        <p className="mt-1 text-sm text-muted-foreground">{period}</p>
      </div>
      {report.isError ? (
        <QueryErrorState onRetry={() => void report.refetch()} />
      ) : report.isLoading ? (
        <LoadingSkeleton rows={4} />
      ) : !report.data?.projects.length ? (
        <EmptyState
          icon={<FileBarChart />}
          title={t("pages.portfolioLiquidity.ui.reportEmpty")}
          description={t("pages.portfolioLiquidity.ui.reportEmptyHint")}
        />
      ) : (
        <>
          <div className="flex flex-wrap items-end gap-3">
            <div className="min-w-0 flex-1">
              <label
                htmlFor="liquidity-report-search"
                className="mb-1.5 block text-sm font-medium"
              >
                {t("pages.portfolioLiquidity.ui.searchReport")}
              </label>
              <div className="relative">
                <Search
                  className="pointer-events-none absolute start-3 top-3 size-4 text-muted-foreground"
                  aria-hidden="true"
                />
                <Input
                  id="liquidity-report-search"
                  type="search"
                  className="h-10 ps-9"
                  value={search}
                  onChange={(event) => {
                    setSearch(event.target.value);
                    setPage(1);
                  }}
                  placeholder={t(
                    "pages.portfolioLiquidity.ui.searchPlaceholder",
                  )}
                />
              </div>
            </div>
            {search ? (
              <Button
                variant="ghost"
                className="min-h-10"
                onClick={() => {
                  setSearch("");
                  setPage(1);
                }}
              >
                <X className="size-4" aria-hidden="true" />
                {t("pages.portfolioLiquidity.ui.clearSearch")}
              </Button>
            ) : null}
          </div>
          {rows.length ? (
            <>
              <nav
                aria-label={t("pages.portfolioLiquidity.ui.reportPages")}
                className="flex flex-wrap items-center justify-between gap-3"
              >
                <p className="text-sm text-muted-foreground" role="status">
                  {t("pages.portfolioLiquidity.ui.showing", {
                    from: number((page - 1) * PAGE_SIZE + 1),
                    to: number(Math.min(page * PAGE_SIZE, filtered.length)),
                    total: number(filtered.length),
                  })}
                </p>
                <div className="flex items-center gap-2">
                  <Button
                    variant="secondary"
                    className="min-h-10"
                    disabled={page === 1}
                    onClick={() => setPage(page - 1)}
                  >
                    <ChevronLeft
                      className="size-4 rtl:rotate-180"
                      aria-hidden="true"
                    />
                    {t("pages.portfolioLiquidity.ui.previous")}
                  </Button>
                  <span className="text-xs tabular-nums" dir="ltr">
                    {number(page)} / {number(totalPages)}
                  </span>
                  <Button
                    variant="secondary"
                    className="min-h-10"
                    disabled={page === totalPages}
                    onClick={() => setPage(page + 1)}
                  >
                    {t("pages.portfolioLiquidity.ui.next")}
                    <ChevronRight
                      className="size-4 rtl:rotate-180"
                      aria-hidden="true"
                    />
                  </Button>
                </div>
              </nav>
              <div data-testid="portfolio-cash-report">
                <DataTable
                  columns={columns}
                  data={rows}
                  rowKey={(row) => row.project_id}
                />
              </div>
            </>
          ) : (
            <EmptyState
              icon={<Search />}
              title={t("pages.portfolioLiquidity.ui.noMatches")}
              action={
                <Button variant="secondary" onClick={() => setSearch("")}>
                  {t("pages.portfolioLiquidity.ui.clearSearch")}
                </Button>
              }
            />
          )}
        </>
      )}
    </section>
  );
}
