import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router";
import {
  ProjectProvider,
  usePermission,
  useProject,
} from "@/app/contexts/project-context";
import { fetchLaborProductivity } from "@/app/lib/api/labor-productivity";
import { PATHS } from "@/app/routeVars";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { Button } from "@/components/ui/sprint-button";

type GroupBy = "activity" | "discipline" | "job_title";

function Content() {
  const { t } = useTranslation();

  const { projectId } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_reports");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [groupBy, setGroupBy] = useState<GroupBy>("activity");

  const { data, isLoading } = useQuery({
    queryKey: ["labor-productivity", projectId, dateFrom, dateTo, groupBy],
    queryFn: () =>
      fetchLaborProductivity(projectId, {
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
        group_by: groupBy,
      }),
    enabled: canView,
  });

  if (!canView) {
    return (
      <p className='rounded-lg border border-border p-8 text-center text-muted-foreground'>
        دسترسی به این بخش ندارید.
      </p>
    );
  }

  if (isLoading) return <LoadingSkeleton rows={8} />;

  const rows = data?.rows ?? [];

  return (
    <div className='space-y-6'>
      <div className='flex flex-wrap items-end gap-3'>
        <JalaliDatePicker
          name='from'
          label='از تاریخ'
          value={dateFrom}
          onChange={setDateFrom}
        />
        <JalaliDatePicker
          name='to'
          label='تا تاریخ'
          value={dateTo}
          onChange={setDateTo}
        />
        <div className='flex gap-2'>
          {(
            [
              ["activity", "فعالیت"],
              ["discipline", "رشته"],
              ["job_title", "عنوان شغلی"],
            ] as const
          ).map(([id, label]) => (
            <Button
              key={id}
              size='sm'
              variant={groupBy === id ? "primary" : "secondary"}
              onClick={() => setGroupBy(id)}
            >
              {label}
            </Button>
          ))}
        </div>
      </div>

      {data ? (
        <div className='grid gap-3 sm:grid-cols-3'>
          <div className='rounded-lg border border-border p-4'>
            <p className='text-xs text-muted-foreground'>مجموع ساعات کار</p>
            <p className='text-xl font-semibold'>{data.total_labor_hours}</p>
          </div>
          {data.total_executed_qty != null ? (
            <div className='rounded-lg border border-border p-4'>
              <p className='text-xs text-muted-foreground'>مجموع اجرا</p>
              <p className='text-xl font-semibold'>{data.total_executed_qty}</p>
            </div>
          ) : null}
          {data.project_productivity_index != null ? (
            <div className='rounded-lg border border-border p-4'>
              <p className='text-xs text-muted-foreground'>
                شاخص بهره‌وری پروژه
              </p>
              <p className='text-xl font-semibold'>
                {data.project_productivity_index}
              </p>
            </div>
          ) : null}
        </div>
      ) : null}

      <div className='overflow-x-auto rounded-lg border border-border'>
        <table className='w-full text-sm'>
          <thead className='bg-muted/50'>
            <tr>
              {groupBy === "activity"
                ? [
                    "کد",
                    "فعالیت",
                    "اجرا",
                    "ساعات",
                    "بهره‌وری",
                    "بودجه نیرو",
                  ].map((h) => (
                    <th key={h} className='px-3 py-2 text-start'>
                      {h}
                    </th>
                  ))
                : groupBy === "job_title"
                  ? ["عنوان", "ساعات", "نفر-روز"].map((h) => (
                      <th key={h} className='px-3 py-2 text-start'>
                        {h}
                      </th>
                    ))
                  : ["رشته", "ساعات", "نفر-روز"].map((h) => (
                      <th key={h} className='px-3 py-2 text-start'>
                        {h}
                      </th>
                    ))}
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td
                  colSpan={6}
                  className='px-3 py-8 text-center text-muted-foreground'
                >
                  داده‌ای یافت نشد
                </td>
              </tr>
            ) : groupBy === "activity" ? (
              rows.map((r) => (
                <tr key={r.activity_id} className='border-t border-border'>
                  <td className='px-3 py-2 font-mono text-xs'>
                    {r.activity_code}
                  </td>
                  <td className='px-3 py-2'>{r.activity_name}</td>
                  <td className='px-3 py-2'>{r.executed_qty ?? "—"}</td>
                  <td className='px-3 py-2'>{r.labor_hours ?? "—"}</td>
                  <td className='px-3 py-2'>{r.productivity_index ?? "—"}</td>
                  <td className='px-3 py-2'>{r.planned_budget_labor ?? "—"}</td>
                </tr>
              ))
            ) : groupBy === "job_title" ? (
              rows.map((r) => (
                <tr key={r.job_title} className='border-t border-border'>
                  <td className='px-3 py-2'>{r.job_title}</td>
                  <td className='px-3 py-2'>{r.labor_hours}</td>
                  <td className='px-3 py-2'>{r.headcount_days}</td>
                </tr>
              ))
            ) : (
              rows.map((r) => (
                <tr key={r.discipline} className='border-t border-border'>
                  <td className='px-3 py-2'>{r.discipline}</td>
                  <td className='px-3 py-2'>{r.labor_hours}</td>
                  <td className='px-3 py-2'>{r.headcount_days}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function ProjectLaborProductivityPage() {
  const { t, i18n } = useTranslation();
  const { projectId = "" } = useParams();
  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "بهره‌وری نیروی انسانی" },
          ]}
        />
        <PageHeader title={t("pages.laborProductivity.title")} />
        <p className='text-sm text-muted-foreground'>
          <Link
            className='text-primary hover:underline'
            to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PERSONNEL_SUMMARY}`}
          >
            گزارش نفرات
          </Link>
        </p>
        <Content />
      </ProjectProvider>
    </main>
  );
}
