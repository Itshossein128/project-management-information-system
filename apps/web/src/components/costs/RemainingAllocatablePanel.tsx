import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  costCategoryLabel,
  fetchBudgetRemaining,
  fetchBudgets,
  formatFaAmount,
  postBudgetTransfer,
} from "@/app/lib/api/costs";
import { Input } from "@/components/form";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

interface Props {
  projectId: string;
  canEdit: boolean;
  versionId?: string | null;
}

export function RemainingAllocatablePanel({ projectId, canEdit, versionId }: Props) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const [fromId, setFromId] = useState("");
  const [toId, setToId] = useState("");
  const [amount, setAmount] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["budget-remaining", projectId, versionId ?? "control"],
    queryFn: () => fetchBudgetRemaining(projectId, versionId ?? undefined),
  });

  const { data: budgetData } = useQuery({
    queryKey: ["budgets", projectId, versionId ?? "default", "for-transfer"],
    queryFn: () => fetchBudgets(projectId, versionId ? { version_id: versionId } : {}),
    enabled: canEdit,
  });

  const lineOptions = useMemo(
    () =>
      (budgetData?.results ?? []).map((b) => ({
        id: b.id,
        label: `${b.wbs_code ?? b.activity_code ?? b.level ?? "—"} / ${costCategoryLabel(b.cost_category)} (${formatFaAmount(b.budget_amount)})`,
      })),
    [budgetData],
  );

  const transferMutation = useMutation({
    mutationFn: () =>
      postBudgetTransfer(projectId, {
        from_line_id: fromId,
        to_line_id: toId,
        amount: amount.trim(),
        note: "UI transfer",
      }),
    onSuccess: () => {
      toast.success(t("pages.costs.transferDone", "جابه‌جایی ثبت شد"));
      setAmount("");
      void qc.invalidateQueries({ queryKey: ["budget-remaining", projectId] });
      void qc.invalidateQueries({ queryKey: ["budgets", projectId] });
      void qc.invalidateQueries({ queryKey: ["budget-versions", projectId] });
      void qc.invalidateQueries({ queryKey: ["cost-summary", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <section className="space-y-3 border-t pt-6" data-testid="remaining-allocatable-panel">
      <h3 className="text-sm font-semibold">
        {t("pages.costs.remainingTitle", "مانده قابل تخصیص")}
      </h3>
      <p className="text-sm text-muted-foreground">
        {t(
          "pages.costs.remainingHint",
          "مانده = مصوب − تعهدشده − مصرف‌شده. جابه‌جایی درون بودجه با حفظ سقف پروژه.",
        )}
      </p>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
      ) : !data?.headings?.length ? (
        <p className="text-sm text-muted-foreground">
          {t("pages.costs.noRemaining", "بودجه مصوب کنترلی برای محاسبه مانده یافت نشد.")}
        </p>
      ) : (
        <>
          <p className="text-xs text-muted-foreground">
            سقف پروژه: {formatFaAmount(data.project_ceiling)}
          </p>
          <div className="overflow-x-auto rounded border">
            <table className="w-full min-w-[640px] text-sm">
              <thead className="bg-muted/40">
                <tr>
                  <th className="px-2 py-1 text-start">سرفصل</th>
                  <th className="px-2 py-1 text-center">مصوب</th>
                  <th className="px-2 py-1 text-center">تعهد</th>
                  <th className="px-2 py-1 text-center">مصرف</th>
                  <th className="px-2 py-1 text-center">مانده</th>
                </tr>
              </thead>
              <tbody>
                {data.headings.map((h) => (
                  <tr key={h.key} className="border-t">
                    <td className="px-2 py-1">
                      {costCategoryLabel(h.cost_category)}
                      {h.cbs_missing_warning ? (
                        <span className="ms-1 text-xs text-warning-700">بدون CBS</span>
                      ) : null}
                      {h.overrun ? (
                        <span className="ms-1 text-xs text-destructive">تجاوز</span>
                      ) : null}
                    </td>
                    <td className="px-2 py-1 text-center">{formatFaAmount(h.approved)}</td>
                    <td className="px-2 py-1 text-center">{formatFaAmount(h.committed)}</td>
                    <td className="px-2 py-1 text-center">{formatFaAmount(h.consumed)}</td>
                    <td className="px-2 py-1 text-center font-medium">
                      {formatFaAmount(h.remaining)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {canEdit && lineOptions.length >= 2 ? (
        <div className="space-y-2 rounded border p-3">
          <p className="text-sm font-medium">{t("pages.costs.transferTitle", "جابه‌جایی درون بودجه")}</p>
          <label className="block text-xs">
            از ردیف
            <select
              className="mt-1 w-full rounded border px-2 py-1 text-sm"
              value={fromId}
              onChange={(e) => setFromId(e.target.value)}
            >
              <option value="">—</option>
              {lineOptions.map((o) => (
                <option key={o.id} value={o.id}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-xs">
            به ردیف
            <select
              className="mt-1 w-full rounded border px-2 py-1 text-sm"
              value={toId}
              onChange={(e) => setToId(e.target.value)}
            >
              <option value="">—</option>
              {lineOptions.map((o) => (
                <option key={o.id} value={o.id}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>
          <label className="block space-y-1 text-xs">
            <span>{t("pages.costs.transferAmount", "مبلغ")}</span>
            <Input value={amount} onChange={(e) => setAmount(e.target.value)} />
          </label>
          <Button
            size="sm"
            variant="primary"
            disabled={!fromId || !toId || fromId === toId || !amount.trim()}
            loading={transferMutation.isPending}
            onClick={() => transferMutation.mutate()}
          >
            ثبت جابه‌جایی
          </Button>
        </div>
      ) : null}
    </section>
  );
}
