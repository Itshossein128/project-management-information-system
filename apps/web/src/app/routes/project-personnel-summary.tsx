import { useQuery } from "@tanstack/react-query";
import { Download } from "lucide-react";
import { useMemo, useState } from "react";
import { useParams } from "react-router";
import {
  ProjectProvider,
  usePermission,
  useProject,
} from "@/app/contexts/project-context";
import { downloadExcel } from "@/app/lib/excel/excel-write";
import { fetchPersonnelSummary } from "@/app/lib/api/reports";
import { PATHS } from "@/app/routeVars";
import { JalaliDateRangePicker } from "@/components/form/JalaliDateRangePicker";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { Button } from "@/components/ui/sprint-button";

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function monthStartIso() {
  const d = new Date();
  return new Date(d.getFullYear(), d.getMonth(), 1).toISOString().slice(0, 10);
}

function heatColor(value: number, max: number): string {
  if (value <= 0 || max <= 0) return "";
  const ratio = value / max;
  if (ratio > 0.75) return "bg-success-200 dark:bg-success-900/50";
  if (ratio > 0.5) return "bg-success-100 dark:bg-success-950/40";
  if (ratio > 0.25) return "bg-success-50 dark:bg-success-950/20";
  return "bg-muted/30";
}

function PersonnelSummaryContent() {
  const { projectId, project, isLoading: projectLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_reports");

  const [dateRange, setDateRange] = useState({
    from: monthStartIso(),
    to: todayIso(),
  });
  const [category, setCategory] = useState<"all" | "indirect" | "direct">(
    "all",
  );
  const [groupBy, setGroupBy] = useState<"daily" | "monthly">("daily");

  const { data, isLoading } = useQuery({
    queryKey: ["personnel-summary", projectId, dateRange, category, groupBy],
    queryFn: () =>
      fetchPersonnelSummary(projectId, {
        date_from: dateRange.from,
        date_to: dateRange.to,
        category,
        group_by: groupBy,
      }),
    enabled: canView && Boolean(projectId),
  });

  const maxCell = useMemo(() => {
    if (!data) return 0;
    let max = 0;
    for (const title of data.job_titles) {
      for (const d of data.dates) {
        const v = data.data[title]?.[d] ?? 0;
        if (v > max) max = v;
      }
    }
    return max;
  }, [data]);

  const exportXlsx = () => {
    if (!data) return;
    const headers = ["عنوان شغلی", ...data.dates, "میانگین"];
    const rows = data.job_titles.map((title) => {
      const row: Record<string, unknown> = { "عنوان شغلی": title };
      for (const d of data.dates) {
        row[d] = data.data[title]?.[d] ?? 0;
      }
      row["میانگین"] = data.totals_by_title[title] ?? 0;
      return row;
    });
    const totalRow: Record<string, unknown> = { "عنوان شغلی": "جمع" };
    for (const d of data.dates) {
      totalRow[d] = data.totals_by_date[d] ?? 0;
    }
    totalRow["میانگین"] = "";
    rows.push(totalRow);
    downloadExcel({
      filename: `personnel-summary-${projectId}.xlsx`,
      sheetName: "نفرات",
      headers,
      rows,
    });
  };

  if (projectLoading) return <LoadingSkeleton rows={10} />;
  if (!project) return <p>پروژه یافت نشد</p>;

  if (!canView) {
    return (
      <p className='rounded-lg border border-border bg-card p-8 text-center text-muted-foreground'>
        دسترسی به این بخش ندارید — نقش شما مجوز مشاهده گزارش‌ها را ندارد.
      </p>
    );
  }

  return (
    <div className='space-y-6'>
      <div className='flex flex-wrap items-end justify-between gap-3'>
        <PageHeader title='گزارش نفرات' subtitle={project.project_name} />
        <Button
          variant='secondary'
          size='sm'
          disabled={!data}
          onClick={exportXlsx}
        >
          <Download className='size-4' />
          خروجی Excel
        </Button>
      </div>

      <div className='flex flex-wrap items-end gap-3'>
        <div className='min-w-[260px] flex-1'>
          <JalaliDateRangePicker
            name='personnel_range'
            label='بازه تاریخ'
            value={dateRange}
            onChange={setDateRange}
          />
        </div>
        <div className='flex gap-2'>
          {(
            [
              { value: "all", label: "همه" },
              { value: "indirect", label: "غیرمستقیم" },
              { value: "direct", label: "مستقیم" },
            ] as const
          ).map((c) => (
            <Button
              key={c.value}
              size='sm'
              variant={category === c.value ? "primary" : "secondary"}
              onClick={() => setCategory(c.value)}
            >
              {c.label}
            </Button>
          ))}
        </div>
        <div className='flex gap-2'>
          <Button
            size='sm'
            variant={groupBy === "daily" ? "primary" : "secondary"}
            onClick={() => setGroupBy("daily")}
          >
            روزانه
          </Button>
          <Button
            size='sm'
            variant={groupBy === "monthly" ? "primary" : "secondary"}
            onClick={() => setGroupBy("monthly")}
          >
            ماهانه
          </Button>
        </div>
      </div>

      {isLoading ? (
        <LoadingSkeleton rows={8} />
      ) : data && data.job_titles.length > 0 ? (
        <div className='overflow-x-auto rounded-lg border border-border'>
          <table className='w-full min-w-[600px] text-xs'>
            <thead className='bg-muted/50'>
              <tr>
                <th className='sticky start-0 z-10 bg-muted/50 px-2 py-2 text-start'>
                  عنوان
                </th>
                {data.dates.map((d) => (
                  <th
                    key={d}
                    className='px-2 py-2 text-center whitespace-nowrap'
                  >
                    {d}
                  </th>
                ))}
                <th className='px-2 py-2 text-center'>میانگین</th>
              </tr>
            </thead>
            <tbody>
              {data.job_titles.map((title) => (
                <tr key={title} className='border-t border-border'>
                  <td className='sticky start-0 z-10 bg-card px-2 py-1 font-medium whitespace-nowrap'>
                    {title}
                  </td>
                  {data.dates.map((d) => {
                    const v = data.data[title]?.[d] ?? 0;
                    return (
                      <td
                        key={d}
                        className={`px-2 py-1 text-center ${heatColor(v, maxCell)}`}
                        title={String(v)}
                      >
                        {v > 0 ? v : "—"}
                      </td>
                    );
                  })}
                  <td className='px-2 py-1 text-center font-medium'>
                    {data.totals_by_title[title]?.toFixed(1) ?? "—"}
                  </td>
                </tr>
              ))}
              <tr className='border-t-2 border-border bg-muted/30 font-semibold'>
                <td className='sticky start-0 z-10 bg-muted/30 px-2 py-2'>
                  جمع
                </td>
                {data.dates.map((d) => (
                  <td key={d} className='px-2 py-2 text-center'>
                    {data.totals_by_date[d] ?? 0}
                  </td>
                ))}
                <td />
              </tr>
            </tbody>
          </table>
        </div>
      ) : (
        <p className='text-center text-muted-foreground'>
          داده‌ای در این بازه یافت نشد
        </p>
      )}
    </div>
  );
}

export default function ProjectPersonnelSummaryPage() {
  const { projectId = "" } = useParams();

  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "گزارش نفرات" },
          ]}
        />
        <PersonnelSummaryContent />
      </ProjectProvider>
    </main>
  );
}
