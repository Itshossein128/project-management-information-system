import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { fetchWBSFlat } from "@/app/lib/api/wbs";
import { formatWithCommas, parseFormattedNumber, toRawNumericString } from "@/app/lib/utils";
import { fetchActivities } from "@/app/lib/api/activities";
import {
  COST_CATEGORIES,
  costCategoryLabel,
  createActualCost,
  fetchActualCosts,
  fetchSuppliers,
  formatFaAmount,
  type CostCategory,
  type Supplier,
} from "@/app/lib/api/costs";
import { listFiscalLocks } from "@/app/lib/api/project-core";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { EmptyState } from "@/components/layout/empty-state";
import { LoadingSkeleton } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

function asArray<T>(value: T[] | { results?: T[] } | null | undefined): T[] {
  if (Array.isArray(value)) return value;
  if (value && Array.isArray(value.results)) return value.results;
  return [];
}

function SourceBadge({ isAuto }: { isAuto: boolean }) {
  return (
    <span
      className={
        isAuto
          ? "inline-flex rounded-full bg-info-100 px-2 py-0.5 text-xs text-info-800 dark:bg-info-950 dark:text-info-200"
          : "inline-flex rounded-full bg-success-100 px-2 py-0.5 text-xs text-success-800 dark:bg-success-950 dark:text-success-200"
      }
    >
      {isAuto ? "خودکار" : "دستی"}
    </span>
  );
}

function dateInActiveLock(
  isoDate: string,
  locks: { period_start: string; period_end: string; is_active?: boolean }[],
): boolean {
  if (!isoDate) return false;
  return locks.some((lock) => {
    if (lock.is_active === false) return false;
    return lock.period_start <= isoDate && isoDate <= lock.period_end;
  });
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
  const [corrective, setCorrective] = useState(false);
  const [correctionReason, setCorrectionReason] = useState("");

  const { data: wbsData } = useQuery({
    queryKey: ["wbs-flat", projectId],
    queryFn: () => fetchWBSFlat(projectId),
    enabled: open,
  });
  const wbsFlat = asArray(wbsData);

  const { data: activitiesData } = useQuery({
    queryKey: ["activities", projectId, "cost-drawer"],
    queryFn: () => fetchActivities(projectId, { per_page: 200 }),
    enabled: open,
  });
  const activities = asArray(activitiesData);

  const { data: suppliersData } = useQuery({
    queryKey: ["suppliers", projectId],
    queryFn: () => fetchSuppliers(projectId),
    enabled: open,
  });
  const suppliers = asArray<Supplier>(suppliersData);

  const { data: fiscalLocksData } = useQuery({
    queryKey: ["project-fiscal-locks", projectId],
    queryFn: () => listFiscalLocks(projectId),
    // Prefetch even while closed so corrective UI is ready on open.
    enabled: Boolean(projectId),
  });
  const fiscalLocks = asArray(fiscalLocksData);

  const activeLocks = useMemo(
    () => fiscalLocks.filter((lock) => lock.is_active !== false),
    [fiscalLocks],
  );
  // Show corrective path whenever an active lock exists (date may be unset yet).
  const showCorrectivePath = activeLocks.length > 0;
  const lockApplies =
    activeLocks.length > 0 &&
    (!costDate || dateInActiveLock(costDate, activeLocks));

  // When a lock forces the corrective path, pre-check and keep reason editable.
  useEffect(() => {
    if (lockApplies) setCorrective(true);
  }, [lockApplies]);

  const save = useMutation({
    mutationFn: () =>
      createActualCost(projectId, {
        cost_date: costDate,
        cost_category: category,
        amount: parseFormattedNumber(amount),
        description,
        wbs: wbsId || null,
        activity: activityId || null,
        supplier: supplierId || null,
        ...(corrective
          ? { corrective: true, correction_reason: correctionReason.trim() }
          : {}),
      }),
    onSuccess: () => {
      toast.success("هزینه ثبت شد");
      onSaved();
      onClose();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const canSave =
    Boolean(costDate && amount) &&
    !save.isPending &&
    (!corrective || correctionReason.trim().length > 0) &&
    !(lockApplies && !corrective);

  return (
    <Drawer
      isOpen={open}
      onClose={onClose}
      title="ثبت هزینه جدید"
      footer={
        <Button
          variant="primary"
          data-testid="actual-cost-save-btn"
          disabled={!canSave}
          loading={save.isPending}
          onClick={() => save.mutate()}
        >
          ذخیره
        </Button>
      }
    >
      <div className="flex flex-col gap-4" data-testid="actual-cost-drawer">
        <JalaliDatePicker name="cost_date" label="تاریخ هزینه" value={costDate} onChange={setCostDate} />
        {showCorrectivePath ? (
          <div
            className="space-y-2 rounded-md border border-warning-200 bg-warning-50 p-3 dark:border-warning-800 dark:bg-warning-950/30"
            data-testid="actual-cost-corrective-section"
          >
            <p className="text-sm text-muted-foreground">
              یک قفل دوره مالی فعال است. برای ثبت در دوره قفل‌شده، مسیر اصلاحی را فعال کنید.
            </p>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                data-testid="actual-cost-corrective"
                checked={corrective}
                onChange={(e) => setCorrective(e.target.checked)}
              />
              <span>ثبت اصلاحی (دوره مالی قفل)</span>
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span>دلیل اصلاح</span>
              <input
                className="rounded-md border border-input bg-background px-3 py-2"
                data-testid="actual-cost-correction-reason"
                value={correctionReason}
                onChange={(e) => setCorrectionReason(e.target.value)}
                required={corrective || lockApplies}
              />
            </label>
          </div>
        ) : null}
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
            value={formatWithCommas(amount)}
            onChange={(e) => setAmount(toRawNumericString(e.target.value))}
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
            {activities.map((a) => (
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
