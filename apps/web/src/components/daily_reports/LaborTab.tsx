import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Plus, Save } from "lucide-react";
import { useToast } from "@/components/ui/toast";
import {
  batchSaveLabor,
  fetchJobTitles,
  type LaborCategory,
  type LaborRow,
} from "@/app/lib/api/daily-reports";
import { isNetworkError, queueLaborBatch, type LaborBatchMeta } from "@/app/lib/offlineWrite";
import { getCachedManpowerTitles } from "@/app/lib/offlineDB";
import type { DailyTabProps } from "./ActivityTab";

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
  category: LaborCategory,
  titles: string[],
  existing: LaborRow[],
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
  // Any remaining existing rows are custom titles.
  const custom: Draft[] = Array.from(byTitle.values()).map((row) => ({
    id: row.id,
    job_title: row.job_title,
    custom_title: row.custom_title,
    isCustom: true,
    shift_1_count: row.shift_1_count,
    shift_2_count: row.shift_2_count,
    shift_3_count: row.shift_3_count,
    work_hours: row.work_hours ?? "",
    overtime_hours: row.overtime_hours ?? "",
  }));
  return [...fixed, ...custom];
}

function CategoryPanel({
  projectId,
  reportId,
  category,
  existing,
  reportMeta,
  readOnly,
  onChanged,
}: {
  projectId: string;
  reportId: string;
  category: LaborCategory;
  existing: LaborRow[];
  reportMeta: LaborBatchMeta;
  readOnly?: boolean;
  onChanged: () => void;
}) {
  const toast = useToast();
  const { data: titles = [] } = useQuery({
    queryKey: ["job-titles", projectId, category],
    queryFn: async () => {
      if (isNetworkError()) {
        const cached = await getCachedManpowerTitles(category);
        return cached.map((t) => ({
          id: String(t.id),
          category: t.category as LaborCategory,
          title: String(t.title ?? ""),
        }));
      }
      return fetchJobTitles(projectId, category);
    },
  });
  const titleNames = useMemo(() => titles.map((t) => t.title), [titles]);
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [saving, setSaving] = useState(false);
  const [isDirty, setIsDirty] = useState(false);

  useEffect(() => {
    setDrafts(rowsForCategory(category, titleNames, existing));
    setIsDirty(false);
  }, [category, titleNames, existing]);

  const setCount = (idx: number, field: keyof Draft, value: number) => {
    setIsDirty(true);
    setDrafts((prev) => prev.map((d, i) => (i === idx ? { ...d, [field]: value } : d)));
  };
  const setCustomName = (idx: number, name: string) => {
    setIsDirty(true);
    setDrafts((prev) =>
      prev.map((d, i) => (i === idx ? { ...d, job_title: name, custom_title: name } : d)),
    );
  };
  const addCustom = () => {
    setIsDirty(true);
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

  const save = async (silent = false) => {
    const payload = drafts
      .filter((d) => d.job_title.trim() && (d.id || d.shift_1_count || d.shift_2_count || d.shift_3_count))
      .map((d) => ({
        labor_category: category,
        job_title: d.job_title.trim(),
        custom_title: d.isCustom ? d.custom_title.trim() : "",
        shift_1_count: d.shift_1_count,
        shift_2_count: d.shift_2_count,
        shift_3_count: d.shift_3_count,
        work_hours: d.work_hours === "" ? null : d.work_hours,
        overtime_hours: d.overtime_hours === "" ? null : d.overtime_hours,
      }));
    if (payload.length === 0) {
      if (!silent) {
        toast.warning("موردی برای ذخیره وجود ندارد");
      }
      return;
    }
    setSaving(true);
    try {
      if (isNetworkError()) {
        await queueLaborBatch(projectId, reportId, payload, reportMeta);
        if (!silent) toast.success("نیروی انسانی در صف آفلاین ذخیره شد");
      } else {
        await batchSaveLabor(projectId, reportId, payload);
        if (!silent) toast.success("نیروی انسانی ذخیره شد");
      }
      setIsDirty(false);
      onChanged();
    } catch (e) {
      if (!silent) {
        toast.error((e as Error).message);
      }
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    if (readOnly || !isDirty || saving) return;
    const timer = window.setTimeout(() => {
      void save(true);
    }, 900);
    return () => window.clearTimeout(timer);
  }, [isDirty, readOnly, saving, drafts]);

  return (
    <div className="space-y-3">
      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full min-w-[520px] text-sm">
          <thead>
            <tr className="bg-muted/50 text-muted-foreground">
              <th className="px-2 py-2 text-right font-medium">عنوان شغلی</th>
              <th className="px-2 py-2 text-center font-medium">شیفت ۱</th>
              <th className="px-2 py-2 text-center font-medium">شیفت ۲</th>
              <th className="px-2 py-2 text-center font-medium">شیفت ۳</th>
              <th className="px-2 py-2 text-center font-medium">ساعات کار</th>
              <th className="px-2 py-2 text-center font-medium">اضافه‌کار</th>
              <th className="px-2 py-2 text-center font-medium">جمع</th>
            </tr>
          </thead>
          <tbody>
            {drafts.map((d, idx) => {
              const rowTotal = d.shift_1_count + d.shift_2_count + d.shift_3_count;
              return (
                <tr key={d.id ?? `${d.job_title}-${idx}`} className="border-t border-border">
                  <td className="px-2 py-1">
                    {d.isCustom ? (
                      <input
                        className="h-8 w-full rounded border border-input bg-transparent px-2 text-sm"
                        value={d.job_title}
                        placeholder="عنوان سفارشی"
                        disabled={readOnly}
                        onChange={(e) => setCustomName(idx, e.target.value)}
                      />
                    ) : (
                      d.job_title
                    )}
                  </td>
                  {(["shift_1_count", "shift_2_count", "shift_3_count"] as const).map((f) => (
                    <td key={f} className="px-2 py-1 text-center">
                      <input
                        type="number"
                        min={0}
                        className={numInput}
                        value={d[f]}
                        disabled={readOnly}
                        onChange={(e) => setCount(idx, f, Number(e.target.value) || 0)}
                      />
                    </td>
                  ))}
                  {(["work_hours", "overtime_hours"] as const).map((f) => (
                    <td key={f} className="px-2 py-1 text-center">
                      <input
                        type="number"
                        min={0}
                        step={0.5}
                        className={numInput}
                        value={d[f]}
                        disabled={readOnly}
                        onChange={(e) => {
                          setIsDirty(true);
                          const val = e.target.value === "" ? "" : Number(e.target.value);
                          setDrafts((prev) =>
                            prev.map((row, i) => (i === idx ? { ...row, [f]: val } : row)),
                          );
                        }}
                      />
                    </td>
                  ))}
                  <td className="px-2 py-1 text-center font-medium">{rowTotal}</td>
                </tr>
              );
            })}
          </tbody>
          <tfoot>
            <tr className="border-t border-border bg-muted/30 font-semibold">
              <td className="px-2 py-2 text-right">جمع کل</td>
              <td colSpan={5} />
              <td className="px-2 py-2 text-center">{total}</td>
            </tr>
          </tfoot>
        </table>
      </div>
      {!readOnly ? (
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={addCustom}
            className="inline-flex items-center gap-1 rounded-md border border-dashed border-border px-3 py-1.5 text-sm text-muted-foreground hover:bg-muted/40"
          >
            <Plus className="size-4" />
            عنوان سفارشی
          </button>
          <button
            type="button"
            onClick={() => {
              void save();
            }}
            disabled={saving}
            className="inline-flex items-center gap-1 rounded-md bg-primary px-4 py-1.5 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            <Save className="size-4" />
            ذخیره نیروی انسانی
          </button>
        </div>
      ) : null}
    </div>
  );
}

export function LaborTab({ projectId, reportId, report, readOnly, onChanged }: DailyTabProps) {
  const [active, setActive] = useState<LaborCategory>("indirect");

  if (!reportId) {
    return (
      <p className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
        برای افزودن نیروی انسانی، ابتدا هدر گزارش را ذخیره کنید.
      </p>
    );
  }

  const existing = report?.labor ?? [];
  const reportMeta: LaborBatchMeta = {
    report_date: report?.report_date,
    shift: report?.shift,
    weather_condition: report?.weather_condition,
    site_status: report?.site_status,
    general_notes: report?.general_notes,
    temp_min: report?.temp_min,
    temp_max: report?.temp_max,
    existing_labor: existing,
  };

  return (
    <div className="space-y-4">
      <div className="inline-flex rounded-lg border border-border p-1">
        {(["indirect", "direct"] as const).map((cat) => (
          <button
            key={cat}
            type="button"
            onClick={() => setActive(cat)}
            className={
              active === cat
                ? "rounded-md bg-primary px-4 py-1.5 text-sm text-primary-foreground"
                : "rounded-md px-4 py-1.5 text-sm text-muted-foreground hover:bg-muted/40"
            }
          >
            {cat === "indirect" ? "پرسنل ستادی" : "پرسنل اجرایی"}
          </button>
        ))}
      </div>
      <CategoryPanel
        key={active}
        projectId={projectId}
        reportId={reportId}
        category={active}
        existing={existing}
        reportMeta={reportMeta}
        readOnly={readOnly}
        onChanged={onChanged}
      />
    </div>
  );
}
