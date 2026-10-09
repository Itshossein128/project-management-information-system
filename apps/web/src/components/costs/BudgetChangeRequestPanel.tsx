import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  approveBudgetChangeRequest,
  createBudgetChangeRequest,
  fetchBudgetChangeRequests,
  rejectBudgetChangeRequest,
  submitBudgetChangeRequest,
  type BudgetChangeRequest,
} from "@/app/lib/api/costs";
import { Input } from "@/components/form";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

interface Props {
  projectId: string;
  canEdit: boolean;
  canApprove: boolean;
  /** Optional line to bump via CR update op */
  controlLineId?: string | null;
}

export function BudgetChangeRequestPanel({
  projectId,
  canEdit,
  canApprove,
  controlLineId,
}: Props) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const [reason, setReason] = useState("");
  const [impact, setImpact] = useState("");
  const [newAmount, setNewAmount] = useState("");

  const { data: requests = [], isLoading } = useQuery({
    queryKey: ["budget-change-requests", projectId],
    queryFn: () => fetchBudgetChangeRequests(projectId),
  });

  const open = requests.find((r) => r.status === "draft" || r.status === "submitted");

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["budget-change-requests", projectId] });
    void qc.invalidateQueries({ queryKey: ["budget-versions", projectId] });
    void qc.invalidateQueries({ queryKey: ["budgets", projectId] });
    void qc.invalidateQueries({ queryKey: ["cost-summary", projectId] });
    void qc.invalidateQueries({ queryKey: ["budget-remaining", projectId] });
  };

  const createMutation = useMutation({
    mutationFn: () => {
      const affected_lines: Record<string, unknown>[] = [];
      if (controlLineId && newAmount.trim()) {
        affected_lines.push({
          op: "update",
          line_id: controlLineId,
          budget_amount: newAmount.trim(),
        });
      }
      return createBudgetChangeRequest(projectId, {
        reason: reason.trim(),
        project_impact: impact.trim(),
        amount_delta: newAmount.trim() || "0",
        affected_lines,
      });
    },
    onSuccess: () => {
      toast.success(t("pages.costs.budgetCrCreated", "درخواست تغییر بودجه ایجاد شد"));
      setReason("");
      setImpact("");
      setNewAmount("");
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const actionMutation = useMutation({
    mutationFn: async ({
      cr,
      action,
    }: {
      cr: BudgetChangeRequest;
      action: "submit" | "approve" | "reject";
    }) => {
      if (action === "submit") return submitBudgetChangeRequest(projectId, cr.id);
      if (action === "approve") return approveBudgetChangeRequest(projectId, cr.id);
      return rejectBudgetChangeRequest(projectId, cr.id);
    },
    onSuccess: () => {
      toast.success(t("common.saved", "ذخیره شد"));
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <section className="space-y-3 border-t pt-6" data-testid="budget-change-request-panel">
      <h3 className="text-sm font-semibold">
        {t("pages.costs.budgetChangeRequests", "درخواست تغییر بودجه")}
      </h3>
      <p className="text-sm text-muted-foreground">
        {t(
          "pages.costs.budgetChangeHint",
          "تغییر بودجه مصوب فقط از مسیر درخواست با علت، مبلغ، تأثیر پروژه و تصویب مجاز است.",
        )}
      </p>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
      ) : (
        <ul className="space-y-2 text-sm">
          {requests.slice(0, 5).map((r) => (
            <li
              key={r.id}
              className="flex flex-wrap items-center justify-between gap-2 rounded border px-3 py-2"
            >
              <div>
                <span className="font-medium">{r.status}</span>
                <span className="ms-2 text-muted-foreground">{r.reason.slice(0, 80)}</span>
              </div>
              <div className="flex gap-1">
                {canEdit && r.status === "draft" ? (
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => actionMutation.mutate({ cr: r, action: "submit" })}
                  >
                    ارسال
                  </Button>
                ) : null}
                {canApprove && r.status === "submitted" ? (
                  <>
                    <Button
                      size="sm"
                      variant="primary"
                      onClick={() => actionMutation.mutate({ cr: r, action: "approve" })}
                    >
                      تصویب
                    </Button>
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => actionMutation.mutate({ cr: r, action: "reject" })}
                    >
                      رد
                    </Button>
                  </>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
      )}

      {canEdit && !open ? (
        <div className="space-y-2 rounded border p-3">
          <label className="block space-y-1 text-xs">
            <span>{t("pages.costs.crReason", "علت (حداقل ۱۰ کاراکتر)")}</span>
            <Input value={reason} onChange={(e) => setReason(e.target.value)} />
          </label>
          <label className="block space-y-1 text-xs">
            <span>{t("pages.costs.crImpact", "تأثیر بر نتیجه پروژه")}</span>
            <Input value={impact} onChange={(e) => setImpact(e.target.value)} />
          </label>
          {controlLineId ? (
            <label className="block space-y-1 text-xs">
              <span>{t("pages.costs.crNewAmount", "مبلغ پیشنهادی ردیف کنترل")}</span>
              <Input value={newAmount} onChange={(e) => setNewAmount(e.target.value)} />
            </label>
          ) : (
            <p className="text-xs text-muted-foreground">
              برای ایجاد درخواست تغییر مبلغ، یک ردیف از نسخه کنترل لازم است.
            </p>
          )}
          <Button
            size="sm"
            variant="primary"
            disabled={
              reason.trim().length < 10 ||
              impact.trim().length < 3 ||
              !controlLineId ||
              !newAmount.trim()
            }
            loading={createMutation.isPending}
            onClick={() => createMutation.mutate()}
          >
            ایجاد درخواست
          </Button>
        </div>
      ) : null}
    </section>
  );
}
