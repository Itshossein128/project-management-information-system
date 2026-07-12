import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Plus } from "lucide-react";
import { Fragment, useState } from "react";
import {
  CATEGORY_META,
  createBarrier,
  deleteBarrier,
  fetchBarriers,
  STATUS_META,
  updateBarrier,
  type BarrierLog,
} from "@/app/lib/api/barriers";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { JalaliDateRangePicker } from "@/components/form/JalaliDateRangePicker";
import { LoadingSkeleton } from "@/components/layout/page-header";
import { Drawer } from "@/components/ui/drawer";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

export function BarriersGrid({ projectId }: { projectId: string }) {
  const toast = useToast();
  const qc = useQueryClient();
  const [page, setPage] = useState(1);
  const [dateRange, setDateRange] = useState({ from: "", to: "" });
  const [status, setStatus] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [edit, setEdit] = useState<BarrierLog | null>(null);
  const [resolveId, setResolveId] = useState<string | null>(null);
  const [form, setForm] = useState<{
    log_date: string;
    description: string;
    category: import("@/app/lib/api/barriers").BarrierCategory;
    impact_on_schedule: boolean;
    impact_on_cost: boolean;
    status: import("@/app/lib/api/barriers").BarrierStatus;
  }>({
    log_date: "",
    description: "",
    category: "other" as const,
    impact_on_schedule: false,
    impact_on_cost: false,
    status: "open",
  });
  const [resolveForm, setResolveForm] = useState({ resolved_date: "", corrective_action: "" });

  const { data, isLoading } = useQuery({
    queryKey: ["barriers", projectId, page, dateRange, status],
    queryFn: () =>
      fetchBarriers(projectId, {
        page,
        date_from: dateRange.from,
        date_to: dateRange.to,
        status: status || undefined,
      }),
  });

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (edit) return updateBarrier(projectId, edit.id, form);
      return createBarrier(projectId, form);
    },
    onSuccess: () => {
      toast.success(edit ? "مانع به‌روزرسانی شد" : "مانع ثبت شد");
      setDrawerOpen(false);
      setEdit(null);
      void qc.invalidateQueries({ queryKey: ["barriers", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const resolveMutation = useMutation({
    mutationFn: (id: string) =>
      updateBarrier(projectId, id, {
        status: "resolved",
        resolved_date: resolveForm.resolved_date,
        corrective_action: resolveForm.corrective_action,
      }),
    onSuccess: () => {
      toast.success("مشکل رفع شد");
      setResolveId(null);
      void qc.invalidateQueries({ queryKey: ["barriers", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const rows = data?.results ?? [];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end gap-3">
        <div className="min-w-[240px] flex-1">
          <JalaliDateRangePicker
            name="barrier_range"
            label="بازه تاریخ"
            value={dateRange}
            onChange={setDateRange}
          />
        </div>
        <select
          className="rounded-md border border-input bg-background px-3 py-2 text-sm"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          <option value="">همه وضعیت‌ها</option>
          {Object.entries(STATUS_META).map(([k, v]) => (
            <option key={k} value={k}>
              {v.label}
            </option>
          ))}
        </select>
        <Button
          variant="primary"
          size="sm"
          onClick={() => {
            setEdit(null);
            setForm({
              log_date: "",
              description: "",
              category: "other",
              impact_on_schedule: false,
              impact_on_cost: false,
              status: "open",
            });
            setDrawerOpen(true);
          }}
        >
          <Plus className="size-4" />
          افزودن
        </Button>
      </div>

      {isLoading ? (
        <LoadingSkeleton rows={8} />
      ) : rows.length === 0 ? (
        <p className="rounded-lg border border-dashed py-12 text-center text-muted-foreground">
          موانعی ثبت نشده است
        </p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full min-w-[900px] text-sm">
            <thead className="bg-muted/50">
              <tr>
                {["تاریخ", "دسته‌بندی", "شرح", "تأثیر زمانی", "تأثیر هزینه", "وضعیت", "عملیات"].map((h) => (
                  <th key={h} className="px-3 py-2 text-start font-medium">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const cat = row.category ? CATEGORY_META[row.category] : null;
                const st = STATUS_META[row.status];
                return (
                  <Fragment key={row.id}>
                    <tr className="border-t border-border">
                      <td className="px-3 py-2">{row.log_date}</td>
                      <td className="px-3 py-2">
                        {cat ? (
                          <span className={`rounded-full px-2 py-0.5 text-xs ${cat.className}`}>
                            {cat.label}
                          </span>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td className="px-3 py-2 max-w-xs truncate">{row.description}</td>
                      <td className="px-3 py-2">{row.impact_on_schedule ? <Check className="size-4 text-emerald-600" /> : "—"}</td>
                      <td className="px-3 py-2">{row.impact_on_cost ? <Check className="size-4 text-emerald-600" /> : "—"}</td>
                      <td className="px-3 py-2">
                        <Badge variant={st.variant} label={st.label} />
                      </td>
                      <td className="px-3 py-2">
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setEdit(row);
                              setForm({
                                log_date: row.log_date,
                                description: row.description,
                                category: (row.category || "other") as typeof form.category,
                                impact_on_schedule: row.impact_on_schedule,
                                impact_on_cost: row.impact_on_cost,
                                status: row.status,
                              });
                              setDrawerOpen(true);
                            }}
                          >
                            ویرایش
                          </Button>
                          {row.status === "open" ? (
                            <Button variant="ghost" size="sm" onClick={() => setResolveId(row.id)}>
                              رفع شد
                            </Button>
                          ) : null}
                        </div>
                      </td>
                    </tr>
                    {resolveId === row.id ? (
                      <tr key={`${row.id}-resolve`} className="bg-muted/30">
                        <td colSpan={7} className="px-3 py-3">
                          <div className="flex flex-wrap items-end gap-3">
                            <JalaliDatePicker
                              name="resolved_date"
                              label="تاریخ رفع"
                              value={resolveForm.resolved_date}
                              onChange={(v) => setResolveForm((f) => ({ ...f, resolved_date: v }))}
                            />
                            <label className="flex flex-1 flex-col gap-1 text-sm">
                              اقدام اصلاحی
                              <textarea
                                className="rounded-md border border-input px-2 py-1"
                                value={resolveForm.corrective_action}
                                onChange={(e) =>
                                  setResolveForm((f) => ({ ...f, corrective_action: e.target.value }))
                                }
                              />
                            </label>
                            <Button
                              size="sm"
                              onClick={() => resolveMutation.mutate(row.id)}
                              loading={resolveMutation.isPending}
                            >
                              ثبت رفع مشکل
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ) : null}
                  </Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <Drawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={edit ? "ویرایش مانع" : "ثبت مانع"}
        footer={
          <Button variant="primary" loading={saveMutation.isPending} onClick={() => saveMutation.mutate()}>
            ذخیره
          </Button>
        }
      >
        <div className="flex flex-col gap-3 p-4">
          <JalaliDatePicker
            name="log_date"
            label="تاریخ"
            value={form.log_date}
            onChange={(v) => setForm((f) => ({ ...f, log_date: v }))}
          />
          <label className="text-sm">
            دسته‌بندی
            <select
              className="mt-1 w-full rounded-md border border-input px-2 py-2"
              value={form.category}
              onChange={(e) => setForm((f) => ({ ...f, category: e.target.value as typeof form.category }))}
            >
              {Object.entries(CATEGORY_META).map(([k, v]) => (
                <option key={k} value={k}>
                  {v.label}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm">
            شرح
            <textarea
              className="mt-1 w-full rounded-md border border-input px-2 py-2"
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            />
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={form.impact_on_schedule}
              onChange={(e) => setForm((f) => ({ ...f, impact_on_schedule: e.target.checked }))}
            />
            تأثیر زمانی
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={form.impact_on_cost}
              onChange={(e) => setForm((f) => ({ ...f, impact_on_cost: e.target.checked }))}
            />
            تأثیر هزینه
          </label>
        </div>
      </Drawer>
    </div>
  );
}
