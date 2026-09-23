import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { useState } from "react";
import {
  COST_CATEGORIES,
  costCategoryLabel,
  createCostPool,
  fetchCostPools,
  formatFaAmount,
  type CostCategory,
} from "@/app/lib/api/costs";
import { fetchWBSFlat } from "@/app/lib/api/wbs";
import { formatWithCommas, parseFormattedNumber, toRawNumericString } from "@/app/lib/utils";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Button } from "@/components/ui/sprint-button";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/toast";
import { AllocationWizard } from "./AllocationWizard";
import { EmptyState } from "@/components/layout/empty-state";

function LoadingSkeleton({ rows = 6 }: { rows?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-8 w-full" />
      ))}
    </div>
  );
}

export function CostPoolTab({
  projectId,
  canEdit,
}: {
  projectId: string;
  canEdit: boolean;
}) {
  const toast = useToast();
  const qc = useQueryClient();
  const [showNewForm, setShowNewForm] = useState(false);
  const [poolName, setPoolName] = useState("");
  const [category, setCategory] = useState<CostCategory>("site_overhead");
  const [totalAmount, setTotalAmount] = useState("");
  const [selectedPoolId, setSelectedPoolId] = useState<string | null>(null);

  const { data: pools = [], isLoading, isError, refetch } = useQuery({
    queryKey: ["cost-pools", projectId],
    queryFn: () => fetchCostPools(projectId),
  });

  const { data: wbsFlat = [] } = useQuery({
    queryKey: ["wbs-flat", projectId],
    queryFn: () => fetchWBSFlat(projectId),
  });

  const createPoolMutation = useMutation({
    mutationFn: () =>
      createCostPool(projectId, {
        pool_name: poolName,
        cost_category: category,
        total_amount: parseFormattedNumber(totalAmount),
      }),
    onSuccess: () => {
      toast.success("استخر هزینه ساخته شد");
      setPoolName("");
      setTotalAmount("");
      setShowNewForm(false);
      void qc.invalidateQueries({ queryKey: ["cost-pools", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const activePool = pools.find((p) => p.id === selectedPoolId);

  return (
    <div className="space-y-4" data-testid="cost-pool-tab">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm text-muted-foreground">
          مدیریت استخرهای هزینه و تخصیص به فعالیت‌ها/WBS
        </p>
        {canEdit && !showNewForm ? (
          <Button
            variant="primary"
            size="sm"
            data-testid="cost-pool-new-btn"
            onClick={() => setShowNewForm(true)}
          >
            <Plus className="size-4" />
            استخر جدید
          </Button>
        ) : null}
      </div>

      {showNewForm ? (
        <div
          className="rounded-lg border bg-card p-4 space-y-3"
          data-testid="cost-pool-create-form"
        >
          <h3 className="font-semibold text-sm">ساخت استخر هزینه جدید</h3>
          <div className="grid gap-3 sm:grid-cols-3">
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
              <span>دسته هزینه</span>
              <select
                className="rounded-md border px-2 py-1 bg-background"
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
                type="text"
                className="rounded-md border px-2 py-1"
                data-testid="cost-pool-amount-input"
                value={formatWithCommas(totalAmount)}
                onChange={(e) => setTotalAmount(toRawNumericString(e.target.value))}
              />
            </label>
          </div>
          <div className="flex gap-2">
            <Button
              variant="primary"
              size="sm"
              data-testid="cost-pool-create-btn"
              disabled={!poolName || !totalAmount || createPoolMutation.isPending}
              loading={createPoolMutation.isPending}
              onClick={() => createPoolMutation.mutate()}
            >
              ایجاد
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setShowNewForm(false)}
            >
              انصراف
            </Button>
          </div>
        </div>
      ) : null}

      {selectedPoolId && activePool ? (
        <AllocationWizard
          projectId={projectId}
          poolId={selectedPoolId}
          pool={activePool}
          onClose={() => setSelectedPoolId(null)}
          onDone={() => {
            void qc.invalidateQueries({ queryKey: ["cost-pools", projectId] });
          }}
        />
      ) : null}

      {isLoading ? (
        <LoadingSkeleton rows={6} />
      ) : isError ? (
        <QueryErrorState onRetry={() => void refetch()} />
      ) : pools.length === 0 ? (
        <EmptyState
          title="استخر هزینه‌ای وجود ندارد"
          description="با تعریف استخر جدید می‌توانید هزینه‌های غیرمستقیم یا بالاسری را بین فعالیت‌ها یا ساختار شکست توزیع کنید."
          action={
            canEdit ? (
              <Button
                variant="primary"
                size="sm"
                data-testid="cost-pool-new-btn"
                onClick={() => setShowNewForm(true)}
              >
                <Plus className="size-4" />
                استخر جدید
              </Button>
            ) : null
          }
        />
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                {["نام استخر", "دسته", "مبلغ کل", "تخصیص‌یافته", "باقیمانده", "وضعیت", "عملیات"].map(
                  (h) => (
                    <th key={h} className="px-3 py-2 text-start">
                      {h}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody>
              {pools.map((p) => {
                const statusLabel =
                  p.status === "fully_allocated"
                    ? "تخصیص کامل"
                    : p.status === "partially_allocated"
                    ? "تخصیص جزئی"
                    : "تخصیص نشده";
                return (
                  <tr key={p.id} className="border-t border-border">
                    <td className="px-3 py-2 font-medium">{p.pool_name}</td>
                    <td className="px-3 py-2">{costCategoryLabel(p.cost_category)}</td>
                    <td className="px-3 py-2 font-medium">
                      {p.total_amount != null ? formatFaAmount(p.total_amount) : "—"}
                    </td>
                    <td className="px-3 py-2">{formatFaAmount(p.allocated_amount)}</td>
                    <td className="px-3 py-2">{formatFaAmount(p.remaining)}</td>
                    <td className="px-3 py-2">
                      <span className="rounded-full bg-muted px-2 py-0.5 text-xs">
                        {statusLabel}
                      </span>
                    </td>
                    <td className="px-3 py-2">
                      {canEdit ? (
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => setSelectedPoolId(p.id)}
                        >
                          تخصیص
                        </Button>
                      ) : (
                        "—"
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
