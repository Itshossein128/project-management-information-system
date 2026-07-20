import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { fetchActivities } from "@/app/lib/api/activities";
import {
  allocateCostPool,
  AUTO_ALLOCATE_METHODS,
  autoAllocateCostPool,
  formatFaAmount,
  type AutoAllocateMethod,
  type CostPool,
} from "@/app/lib/api/costs";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

interface AllocationLine {
  activity_id: string;
  amount: string;
}

export function AllocationWizard({
  projectId,
  poolId,
  pool,
  onClose,
  onDone,
}: {
  projectId: string;
  poolId: string;
  pool?: CostPool;
  onClose: () => void;
  onDone: () => void;
}) {
  const toast = useToast();
  const [lines, setLines] = useState<AllocationLine[]>([{ activity_id: "", amount: "" }]);
  const [autoMethod, setAutoMethod] = useState<AutoAllocateMethod>("by_budget_weight");

  const { data: activitiesData } = useQuery({
    queryKey: ["activities", projectId, "allocation"],
    queryFn: () => fetchActivities(projectId, { per_page: 300 }),
  });

  const activities = activitiesData?.results ?? [];
  const remaining = pool?.remaining ?? 0;

  const totalAllocated = lines.reduce((s, l) => s + (Number(l.amount) || 0), 0);

  const save = useMutation({
    mutationFn: () =>
      allocateCostPool(
        projectId,
        poolId,
        lines
          .filter((l) => l.activity_id && l.amount)
          .map((l) => ({
            activity_id: l.activity_id,
            amount: Number(l.amount),
          })),
      ),
    onSuccess: () => {
      toast.success("تخصیص انجام شد");
      onDone();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const autoAllocate = useMutation({
    mutationFn: () => autoAllocateCostPool(projectId, poolId, { method: autoMethod }),
    onSuccess: (res) => {
      if (!res.allocations.length) {
        toast.error("تخصیص خودکاری انجام نشد — داده وزنی یافت نشد");
        return;
      }
      toast.success(`${res.allocations.length} تخصیص خودکار انجام شد`);
      onDone();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const updateLine = (idx: number, patch: Partial<AllocationLine>) => {
    setLines((prev) => prev.map((l, i) => (i === idx ? { ...l, ...patch } : l)));
  };

  const busy = save.isPending || autoAllocate.isPending;

  return (
    <Drawer
      isOpen
      onClose={onClose}
      title={`تخصیص استخر${pool?.pool_name ? `: ${pool.pool_name}` : ""}`}
      footer={
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground">
            باقیمانده: {formatFaAmount(remaining)} — جمع تخصیص: {formatFaAmount(totalAllocated)}
          </p>
          <Button
            variant="primary"
            data-testid="cost-pool-allocate-confirm"
            disabled={
              busy ||
              lines.every((l) => !l.activity_id || !l.amount) ||
              totalAllocated > remaining
            }
            loading={save.isPending}
            onClick={() => save.mutate()}
          >
            تأیید تخصیص
          </Button>
        </div>
      }
    >
      <div className="space-y-4" data-testid="cost-pool-allocation-wizard">
        <div className="rounded-lg border border-border bg-muted/30 p-3 space-y-3">
          <p className="text-sm font-medium">تخصیص خودکار</p>
          <label className="flex flex-col gap-1 text-sm">
            <span>روش</span>
            <select
              className="rounded-md border border-input bg-background px-3 py-2"
              value={autoMethod}
              data-testid="cost-pool-auto-method"
              onChange={(e) => setAutoMethod(e.target.value as AutoAllocateMethod)}
            >
              {AUTO_ALLOCATE_METHODS.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
          </label>
          <Button
            variant="secondary"
            size="sm"
            data-testid="cost-pool-auto-allocate"
            disabled={busy || remaining <= 0}
            loading={autoAllocate.isPending}
            onClick={() => autoAllocate.mutate()}
          >
            تخصیص خودکار
          </Button>
        </div>

        <p className="text-sm font-medium">تخصیص دستی</p>
        {lines.map((line, idx) => (
          <div key={idx} className="flex flex-col gap-2 rounded-lg border border-border p-3">
            <label className="flex flex-col gap-1 text-sm">
              <span>فعالیت</span>
              <select
                className="rounded-md border border-input bg-background px-3 py-2"
                value={line.activity_id}
                data-testid={idx === 0 ? "cost-pool-allocate-activity" : undefined}
                onChange={(e) => updateLine(idx, { activity_id: e.target.value })}
              >
                <option value="">انتخاب…</option>
                {activities.map((a) => (
                  <option key={a.activity_id} value={a.activity_id}>
                    {a.activity_code} — {a.activity_name}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span>مبلغ</span>
              <input
                type="number"
                className="rounded-md border px-3 py-2"
                value={line.amount}
                data-testid={idx === 0 ? "cost-pool-allocate-amount" : undefined}
                onChange={(e) => updateLine(idx, { amount: e.target.value })}
              />
            </label>
            {lines.length > 1 ? (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setLines((prev) => prev.filter((_, i) => i !== idx))}
              >
                حذف ردیف
              </Button>
            ) : null}
          </div>
        ))}
        <Button
          variant="secondary"
          size="sm"
          onClick={() => setLines((prev) => [...prev, { activity_id: "", amount: "" }])}
        >
          ردیف دیگر
        </Button>
      </div>
    </Drawer>
  );
}
