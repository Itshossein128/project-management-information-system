import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import {
  COST_CATEGORIES,
  costCategoryLabel,
  createCostPool,
  fetchCostPools,
  formatFaAmount,
  type CostCategory,
} from "@/app/lib/api/costs";
import { AllocationWizard } from "@/components/costs/AllocationWizard";
import { EmptyState } from "@/components/layout/empty-state";
import { LoadingSkeleton } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

const STATUS_LABELS: Record<string, string> = {
  unallocated: "تخصیص‌نیافته",
  partially_allocated: "تخصیص جزئی",
  fully_allocated: "کامل",
};

export function CostPoolTab({
  projectId,
  canEdit,
}: {
  projectId: string;
  canEdit: boolean;
}) {
  const toast = useToast();
  const qc = useQueryClient();
  const [wizardPoolId, setWizardPoolId] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [poolName, setPoolName] = useState("");
  const [category, setCategory] = useState<CostCategory>("site_overhead");
  const [totalAmount, setTotalAmount] = useState("");

  const { data: pools = [], isLoading, isError, refetch } = useQuery({
    queryKey: ["cost-pools", projectId],
    queryFn: () => fetchCostPools(projectId),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createCostPool(projectId, {
        pool_name: poolName,
        cost_category: category,
        total_amount: totalAmount ? Number(totalAmount) : undefined,
      }),
    onSuccess: () => {
      toast.success("استخر هزینه ایجاد شد");
      setShowCreate(false);
      setPoolName("");
      setTotalAmount("");
      void qc.invalidateQueries({ queryKey: ["cost-pools", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (isLoading) {
    return <LoadingSkeleton rows={6} />;
  }
  if (isError) {
    return <QueryErrorState onRetry={() => void refetch()} />;
  }

  return (
    <div className="space-y-4" data-testid="cost-pool-tab">
      {canEdit && (pools.length > 0 || showCreate) ? (
        <div className="flex flex-wrap items-end gap-3">
          {!showCreate ? (
            <Button
              variant="secondary"
              size="sm"
              data-testid="cost-pool-new-btn"
              onClick={() => setShowCreate(true)}
            >
              استخر جدید
            </Button>
          ) : (
            <div
              className="flex flex-wrap items-end gap-2 rounded-lg border border-border p-3"
              data-testid="cost-pool-create-form"
            >
              <label className="flex flex-col gap-1 text-sm">
                <span>نام استخر</span>
                <input
                  className="rounded-md border px-2 py-1"
                  data-testid="cost-pool-name-input"
                  value={poolName}
                  onChange={(e) => setPoolName(e.target.value)}
                />
              </label>
              <label className="flex flex-col gap-1 text-sm">
                <span>دسته</span>
                <select
                  className="rounded-md border px-2 py-1"
                  data-testid="cost-pool-category"
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
                <span>مبلغ کل</span>
                <input
                  type="number"
                  className="rounded-md border px-2 py-1"
                  data-testid="cost-pool-amount-input"
                  value={totalAmount}
                  onChange={(e) => setTotalAmount(e.target.value)}
                />
              </label>
              <Button
                variant="primary"
                size="sm"
                data-testid="cost-pool-create-btn"
                loading={createMutation.isPending}
                disabled={!poolName}
                onClick={() => createMutation.mutate()}
              >
                ایجاد
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setShowCreate(false)}>
                انصراف
              </Button>
            </div>
          )}
        </div>
      ) : null}

      {pools.length === 0 ? (
        showCreate ? null : (
          <EmptyState
            title="استخری ثبت نشده"
            description="استخر هزینه برای تخصیص هزینه‌های سربار ایجاد کنید."
            action={
              canEdit ? (
                <Button
                  variant="primary"
                  size="sm"
                  data-testid="cost-pool-new-btn"
                  onClick={() => setShowCreate(true)}
                >
                  استخر جدید
                </Button>
              ) : null
            }
          />
        )
      ) : (
      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-sm" data-testid="cost-pool-table">
          <thead className="bg-muted/50">
            <tr>
              {["نام", "دسته", "کل", "تخصیص‌یافته", "باقیمانده", "وضعیت", ""].map((h) => (
                <th key={h} className="px-3 py-2 text-start">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
              {pools.map((p) => (
                <tr
                  key={p.id}
                  className="border-t border-border"
                  data-testid={`cost-pool-row-${p.id}`}
                >
                  <td className="px-3 py-2 font-medium">{p.pool_name || "—"}</td>
                  <td className="px-3 py-2">{costCategoryLabel(p.cost_category)}</td>
                  <td className="px-3 py-2">
                    {p.total_amount != null ? formatFaAmount(p.total_amount) : "—"}
                  </td>
                  <td className="px-3 py-2">{formatFaAmount(p.allocated_amount)}</td>
                  <td className="px-3 py-2">{formatFaAmount(p.remaining)}</td>
                  <td className="px-3 py-2">{STATUS_LABELS[p.status] ?? p.status}</td>
                  <td className="px-3 py-2">
                    {canEdit && p.remaining > 0 ? (
                      <Button
                        variant="secondary"
                        size="sm"
                        data-testid={`cost-pool-allocate-btn-${p.id}`}
                        onClick={() => setWizardPoolId(p.id)}
                      >
                        تخصیص
                      </Button>
                    ) : null}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
      )}

      {wizardPoolId ? (
        <AllocationWizard
          projectId={projectId}
          poolId={wizardPoolId}
          pool={pools.find((p) => p.id === wizardPoolId)}
          onClose={() => setWizardPoolId(null)}
          onDone={() => {
            setWizardPoolId(null);
            void qc.invalidateQueries({ queryKey: ["cost-pools", projectId] });
            void qc.invalidateQueries({ queryKey: ["actual-costs", projectId] });
          }}
        />
      ) : null}
    </div>
  );
}
