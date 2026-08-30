import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router";
import { Plus, Save } from "lucide-react";
import {
  fetchJobTitles,
  fetchManpower,
  saveManpowerDay,
  type ManpowerRow,
} from "@/app/lib/api/manpower";
import { ProjectProvider, useProject } from "@/app/contexts/project-context";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

type Tab = "indirect" | "direct";

interface Draft {
  id?: string;
  job_title: string;
  custom_title: string;
  isCustom: boolean;
  shift_1_count: number;
  shift_2_count: number;
  shift_3_count: number;
  work_hours: number | "";
  overtime_hours: number | "";
}

const numInput =
  "h-8 w-16 rounded border border-input bg-transparent px-2 text-center text-sm outline-none focus-visible:ring-[2px] focus-visible:ring-ring/40 disabled:opacity-50";

function rowsForCategory(
  category: Tab,
  titles: string[],
  existing: ManpowerRow[],
): Draft[] {
  const byTitle = new Map(
    existing.filter((r) => r.labor_category === category).map((r) => [r.job_title, r]),
  );
  const fixed: Draft[] = titles.map((title) => {
    const row = byTitle.get(title);
    byTitle.delete(title);
    return {
      id: row?.id,
      job_title: title,
      custom_title: "",
      isCustom: false,
      shift_1_count: row?.shift_1_count ?? 0,
      shift_2_count: row?.shift_2_count ?? 0,
      shift_3_count: row?.shift_3_count ?? 0,
      work_hours: row?.work_hours ?? "",
      overtime_hours: row?.overtime_hours ?? "",
    };
  });
  const custom: Draft[] = Array.from(byTitle.values()).map((row) => ({
    id: row.id,
    job_title: row.job_title,
    custom_title: row.custom_title ?? row.job_title,
    isCustom: true,
    shift_1_count: row.shift_1_count ?? 0,
    shift_2_count: row.shift_2_count ?? 0,
    shift_3_count: row.shift_3_count ?? 0,
    work_hours: row.work_hours ?? "",
    overtime_hours: row.overtime_hours ?? "",
  }));
  return [...fixed, ...custom];
}

function Content() {
  const { t } = useTranslation();

  const { projectId } = useProject();
  const toast = useToast();
  const qc = useQueryClient();
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [tab, setTab] = useState<Tab>("indirect");
  const [drafts, setDrafts] = useState<Draft[]>([]);

  const { data: titles, isLoading: titlesLoading } = useQuery({
    queryKey: ["job-titles", projectId],
    queryFn: () => fetchJobTitles(projectId),
  });

  const { data: saved = [], isLoading } = useQuery({
    queryKey: ["manpower", projectId, date],
    queryFn: () => fetchManpower(projectId, date),
  });

  const jobTitles = useMemo(() => {
    const list = tab === "indirect" ? (titles?.indirect ?? []) : (titles?.direct ?? []);
    return list.map((t) => t.title);
  }, [tab, titles]);

  useEffect(() => {
    setDrafts(rowsForCategory(tab, jobTitles, saved));
  }, [tab, jobTitles, saved, date]);

  const handleDateChange = (newDate: string) => {
    setDate(newDate);
    // Reset unsaved local state immediately when date changes
    setDrafts(rowsForCategory(tab, jobTitles, []));
  };

  const addCustom = () => {
    setDrafts((prev) => [
      ...prev,
      {
        job_title: "",
        custom_title: "",
        isCustom: true,
        shift_1_count: 0,
        shift_2_count: 0,
        shift_3_count: 0,
        work_hours: "",
        overtime_hours: "",
      },
    ]);
  };

  const total = drafts.reduce(
    (sum, d) => sum + d.shift_1_count + d.shift_2_count + d.shift_3_count,
    0,
  );

  const save = useMutation({
    mutationFn: () => {
      const payload = drafts
        .filter(
          (d) =>
            d.job_title.trim() &&
            (d.id ||
              d.shift_1_count ||
              d.shift_2_count ||
              d.shift_3_count ||
              d.work_hours !== "" ||
              d.overtime_hours !== ""),
        )
        .map((d) => ({
          report_date: date,
          labor_category: tab,
          job_title: d.job_title.trim(),
          custom_title: d.isCustom ? d.custom_title.trim() : "",
          shift_1_count: d.shift_1_count,
          shift_2_count: d.shift_2_count,
          shift_3_count: d.shift_3_count,
          work_hours: d.work_hours === "" ? null : Number(d.work_hours),
          overtime_hours: d.overtime_hours === "" ? null : Number(d.overtime_hours),
        }));

      if (payload.length === 0) {
        throw new Error("موردی برای ذخیره وجود ندارد");
      }
      return saveManpowerDay(projectId, payload);
    },
    onSuccess: (res) => {
      const n = (res as { count?: number }).count ?? drafts.length;
      toast.success(`${n} ردیف ذخیره شد`);
      void qc.invalidateQueries({ queryKey: ["manpower", projectId, date] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (titlesLoading || isLoading) return <LoadingSkeleton rows={8} />;

  return (
    <div className='space-y-4'>
      <JalaliDatePicker
        name='manpower_date'
        label='تاریخ'
        value={date}
        onChange={handleDateChange}
      />
      <div className='flex gap-2'>
        <Button
          variant={tab === "indirect" ? "primary" : "secondary"}
          size='sm'
          onClick={() => setTab("indirect")}
        >
          نیروی غیرمستقیم
        </Button>
        <Button
          variant={tab === "direct" ? "primary" : "secondary"}
          size='sm'
          onClick={() => setTab("direct")}
        >
          نیروی مستقیم
        </Button>
      </div>

      <div className='overflow-x-auto rounded-lg border border-border'>
        <table className='w-full min-w-[520px] text-sm'>
          <thead>
            <tr className='bg-muted/50 text-muted-foreground'>
              <th className='px-2 py-2 text-right font-medium'>عنوان شغلی</th>
              <th className='px-2 py-2 text-center font-medium'>شیفت ۱</th>
              <th className='px-2 py-2 text-center font-medium'>شیفت ۲</th>
              <th className='px-2 py-2 text-center font-medium'>شیفت ۳</th>
              <th className='px-2 py-2 text-center font-medium'>ساعات کار</th>
              <th className='px-2 py-2 text-center font-medium'>اضافه‌کار</th>
              <th className='px-2 py-2 text-center font-medium'>جمع</th>
            </tr>
          </thead>
          <tbody>
            {drafts.map((d, idx) => {
              const rowTotal = d.shift_1_count + d.shift_2_count + d.shift_3_count;
              return (
                <tr key={d.id ?? `${d.job_title}-${idx}`} className='border-t border-border'>
                  <td className='px-2 py-1'>
                    {d.isCustom ? (
                      <input
                        className='h-8 w-full rounded border border-input bg-transparent px-2 text-sm'
                        value={d.job_title}
                        placeholder='عنوان سفارشی'
                        onChange={(e) => {
                          const val = e.target.value;
                          setDrafts((prev) =>
                            prev.map((row, i) =>
                              i === idx ? { ...row, job_title: val, custom_title: val } : row,
                            ),
                          );
                        }}
                      />
                    ) : (
                      d.job_title
                    )}
                  </td>
                  {(["shift_1_count", "shift_2_count", "shift_3_count"] as const).map((f) => (
                    <td key={f} className='px-2 py-1 text-center'>
                      <input
                        type='number'
                        min={0}
                        className={numInput}
                        value={d[f]}
                        onChange={(e) => {
                          const val = Number(e.target.value) || 0;
                          setDrafts((prev) =>
                            prev.map((row, i) => (i === idx ? { ...row, [f]: val } : row)),
                          );
                        }}
                      />
                    </td>
                  ))}
                  {(["work_hours", "overtime_hours"] as const).map((f) => (
                    <td key={f} className='px-2 py-1 text-center'>
                      <input
                        type='number'
                        min={0}
                        step={0.5}
                        className={numInput}
                        value={d[f]}
                        onChange={(e) => {
                          const val = e.target.value === "" ? "" : Number(e.target.value);
                          setDrafts((prev) =>
                            prev.map((row, i) => (i === idx ? { ...row, [f]: val } : row)),
                          );
                        }}
                      />
                    </td>
                  ))}
                  <td className='px-2 py-1 text-center font-medium'>{rowTotal}</td>
                </tr>
              );
            })}
          </tbody>
          <tfoot>
            <tr className='border-t border-border bg-muted/30 font-semibold'>
              <td className='px-2 py-2 text-right'>جمع کل</td>
              <td colSpan={5} />
              <td className='px-2 py-2 text-center'>{total}</td>
            </tr>
          </tfoot>
        </table>
      </div>

      <div className='flex items-center gap-2'>
        <Button
          type='button'
          variant='secondary'
          size='sm'
          onClick={addCustom}
          className='inline-flex items-center gap-1'
        >
          <Plus className='size-4' />
          عنوان سفارشی
        </Button>
        <Button
          type='button'
          variant='primary'
          onClick={() => save.mutate()}
          loading={save.isPending}
          className='inline-flex items-center gap-1'
        >
          <Save className='size-4' />
          ذخیره نیروی انسانی
        </Button>
      </div>
    </div>
  );
}

export default function ProjectManpowerPage() {
  const { t } = useTranslation();
  const { projectId = "" } = useParams();
  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <Breadcrumb items={[{ label: "نیروی انسانی" }]} />
        <PageHeader title={t("pages.manpower.title")} />
        <Content />
      </ProjectProvider>
    </main>
  );
}
