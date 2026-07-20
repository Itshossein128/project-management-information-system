import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { useMemo, useState } from "react";
import { fetchWBSFlat } from "@/app/lib/api/wbs";
import { fetchActivities } from "@/app/lib/api/activities";
import {
  COST_CATEGORIES,
  costCategoryLabel,
  createActualCost,
  fetchActualCosts,
  fetchSuppliers,
  formatFaAmount,
  type CostCategory,
} from "@/app/lib/api/costs";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { EmptyState } from "@/components/layout/empty-state";
import { LoadingSkeleton } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

function SourceBadge({ isAuto }: { isAuto: boolean }) {
  return (
    <span
      className={
        isAuto
          ? "inline-flex rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-800 dark:bg-blue-950 dark:text-blue-200"
          : "inline-flex rounded-full bg-emerald-100 px-2 py-0.5 text-xs text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200"
      }
    >
      {isAuto ? "خودکار" : "دستی"}
    </span>
  );
}

function AddCostDrawer({
  projectId,
  open,
  onClose,
  onSaved,
}: {
  projectId: string;
  open: boolean;
  onClose: () => void;
  onSaved: () => void;
}) {
  const toast = useToast();
  const [costDate, setCostDate] = useState("");
  const [category, setCategory] = useState<CostCategory>("material");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [wbsId, setWbsId] = useState("");
  const [activityId, setActivityId] = useState("");
  const [supplierId, setSupplierId] = useState("");

  const { data: wbsFlat = [] } = useQuery({
    queryKey: ["wbs-flat", projectId],
    queryFn: () => fetchWBSFlat(projectId),
    enabled: open,
  });

  const { data: activitiesData } = useQuery({
    queryKey: ["activities", projectId, "cost-drawer"],
    queryFn: () => fetchActivities(projectId, { per_page: 200 }),
    enabled: open,
  });

  const { data: suppliers = [] } = useQuery({
    queryKey: ["suppliers", projectId],
    queryFn: () => fetchSuppliers(projectId),
    enabled: open,
  });

  const save = useMutation({
    mutationFn: () =>
      createActualCost(projectId, {
        cost_date: costDate,
        cost_category: category,
        amount: Number(amount),
        description,
        wbs: wbsId || null,
        activity: activityId || null,
        supplier: supplierId || null,
      }),
    onSuccess: () => {
      toast.success("هزینه ثبت شد");
      onSaved();
      onClose();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <Drawer
      isOpen={open}
      onClose={onClose}
      title="ثبت هزینه جدید"
      footer={
        <Button
          variant="primary"
          data-testid="actual-cost-save-btn"
          disabled={!costDate || !amount || save.isPending}
          loading={save.isPending}
          onClick={() => save.mutate()}
        >
          ذخیره
        </Button>
      }
    >
      <div className="flex flex-col gap-4" data-testid="actual-cost-drawer">
        <JalaliDatePicker name="cost_date" label="تاریخ هزینه" value={costDate} onChange={setCostDate} />
        <label className="flex flex-col gap-1 text-sm">
          <span>دسته هزینه</span>
          <select
            className="rounded-md border border-input bg-background px-3 py-2"
            data-testid="actual-cost-category"
            value={category}
            onChange={(e) => setCategory(e.target.value as CostCategory)}
          >
            {COST_CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>مبلغ (ریال)</span>
          <input
            type="number"
            className="rounded-md border border-input px-3 py-2"
            data-testid="actual-cost-amount"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>WBS</span>
          <select
            className="rounded-md border border-input bg-background px-3 py-2"
            data-testid="actual-cost-wbs"
            value={wbsId}
            onChange={(e) => setWbsId(e.target.value)}
          >
            <option value="">—</option>
            {wbsFlat.map((w) => (
              <option key={w.wbs_id} value={w.wbs_id}>
                {w.wbs_code} — {w.wbs_name}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>فعالیت</span>
          <select
            className="rounded-md border border-input bg-background px-3 py-2"
            value={activityId}
            onChange={(e) => setActivityId(e.target.value)}
          >
            <option value="">—</option>
            {(activitiesData?.results ?? []).map((a) => (
              <option key={a.activity_id} value={a.activity_id}>
                {a.activity_code} — {a.activity_name}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>تأمین‌کننده</span>
          <select
            className="rounded-md border border-input bg-background px-3 py-2"
            value={supplierId}
            onChange={(e) => setSupplierId(e.target.value)}
          >
            <option value="">—</option>
            {suppliers.map((s) => (
              <option key={s.id} value={s.id}>
                {s.supplier_name}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>شرح</span>
          <textarea
            className="rounded-md border border-input px-3 py-2"
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </label>
      </div>
    </Drawer>
  );
}

export function ActualCostsTab({
  projectId,
  canEdit,
}: {
  projectId: string;
  canEdit: boolean;
}) {
  const [category, setCategory] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const qc = useQueryClient();

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["actual-costs", projectId, category, dateFrom, dateTo],
    queryFn: () =>
      fetchActualCosts(projectId, {
        cost_category: category || undefined,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      }),
  });

  const rows = data?.results ?? [];
  const meta = data?.meta;

  const totalDisplay = useMemo(
    () => (meta?.total_actual != null ? formatFaAmount(meta.total_actual) : "—"),
    [meta],
  );

  return (
    <div className="space-y-4" data-testid="actual-costs-tab">
      <div className="flex flex-wrap items-end gap-3">
        <label className="flex flex-col gap-1 text-sm">
          <span>دسته</span>
          <select
            className="rounded-md border border-input bg-background px-3 py-2"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">همه</option>
            {COST_CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
        </label>
        <JalaliDatePicker name="from" label="از تاریخ" value={dateFrom} onChange={setDateFrom} />
        <JalaliDatePicker name="to" label="تا تاریخ" value={dateTo} onChange={setDateTo} />
        <p className="text-sm text-muted-foreground">
          جمع: <span className="font-semibold text-foreground">{totalDisplay}</span>
        </p>
        {canEdit ? (
          <Button
            variant="secondary"
            size="sm"
            data-testid="actual-cost-add-btn"
            onClick={() => setDrawerOpen(true)}
          >
            <Plus className="size-4" />
            افزودن هزینه
          </Button>
        ) : null}
      </div>

      {isLoading ? (
        <LoadingSkeleton rows={6} />
      ) : isError ? (
        <QueryErrorState onRetry={() => void refetch()} />
      ) : rows.length === 0 ? (
        <EmptyState
          title="هزینه‌ای یافت نشد"
          description="هزینه جدیدی ثبت کنید یا فیلترها را تغییر دهید."
          action={
            canEdit ? (
              <Button
                variant="primary"
                size="sm"
                data-testid="actual-cost-add-btn"
                onClick={() => setDrawerOpen(true)}
              >
                <Plus className="size-4" />
                افزودن هزینه
              </Button>
            ) : null
          }
        />
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                {["تاریخ", "دسته", "مبلغ", "WBS", "فعالیت", "تأمین‌کننده", "منبع", "شرح"].map(
                  (h) => (
                    <th key={h} className="px-3 py-2 text-start">
                      {h}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="border-t border-border">
                  <td className="px-3 py-2 whitespace-nowrap">{r.cost_date}</td>
                  <td className="px-3 py-2">{costCategoryLabel(r.cost_category)}</td>
                  <td className="px-3 py-2 font-medium">
                    {r.amount_display || formatFaAmount(r.amount)}
                  </td>
                  <td className="px-3 py-2">{r.wbs_code ?? "—"}</td>
                  <td className="px-3 py-2">{r.activity_code ?? "—"}</td>
                  <td className="px-3 py-2">{r.supplier_name ?? "—"}</td>
                  <td className="px-3 py-2">
                    <SourceBadge isAuto={r.is_auto_created} />
                  </td>
                  <td className="px-3 py-2 max-w-[200px] truncate" title={r.description}>
                    {r.description || "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <AddCostDrawer
        projectId={projectId}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onSaved={() => {
          void qc.invalidateQueries({ queryKey: ["actual-costs", projectId] });
          void qc.invalidateQueries({ queryKey: ["cost-summary", projectId] });
          void qc.invalidateQueries({ queryKey: ["cost-variance", projectId] });
        }}
      />
    </div>
  );
}
