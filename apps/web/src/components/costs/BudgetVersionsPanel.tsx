import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  approveBudgetVersion,
  compareBudgetVersions,
  createBudgetVersion,
  fetchBudgetVersions,
  formatFaAmount,
  rejectBudgetVersion,
  submitBudgetVersion,
  type BudgetCompareResponse,
  type BudgetVersion,
  type BudgetVersionKind,
} from "@/app/lib/api/costs";
import { Input } from "@/components/form";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

interface Props {
  projectId: string;
  canEdit: boolean;
  canApprove: boolean;
  selectedVersionId: string | null;
  onSelectVersion: (id: string | null) => void;
}

const KIND_LABEL: Record<string, string> = {
  initial: "اولیه",
  approved: "مصوب",
  revised: "اصلاحی",
  final_forecast: "پیش‌بینی نهایی",
};

const STATUS_LABEL: Record<string, string> = {
  draft: "پیش‌نویس",
  submitted: "ارسال‌شده",
  approved: "مصوب",
  rejected: "رد شده",
};

export function BudgetVersionsPanel({
  projectId,
  canEdit,
  canApprove,
  selectedVersionId,
  onSelectVersion,
}: Props) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const [createKind, setCreateKind] = useState<"initial" | "final_forecast">("initial");
  const [compareLeft, setCompareLeft] = useState("");
  const [compareRight, setCompareRight] = useState("");
  const [fxRate, setFxRate] = useState("");
  const [compareResult, setCompareResult] = useState<BudgetCompareResponse | null>(null);

  const { data: versions = [], isLoading } = useQuery({
    queryKey: ["budget-versions", projectId],
    queryFn: () => fetchBudgetVersions(projectId),
  });

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["budget-versions", projectId] });
    void qc.invalidateQueries({ queryKey: ["budgets", projectId] });
    void qc.invalidateQueries({ queryKey: ["cost-summary", projectId] });
    void qc.invalidateQueries({ queryKey: ["budget-remaining", projectId] });
  };

  const createMutation = useMutation({
    mutationFn: () =>
      createBudgetVersion(projectId, {
        kind: createKind,
        name: createKind === "final_forecast" ? "Final forecast" : "Initial",
      }),
    onSuccess: (v) => {
      toast.success(t("pages.costs.budgetVersionCreated", "نسخه بودجه ایجاد شد"));
      onSelectVersion(v.id);
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const actionMutation = useMutation({
    mutationFn: async ({
      version,
      action,
      promote,
    }: {
      version: BudgetVersion;
      action: "submit" | "approve" | "reject";
      promote?: boolean;
    }) => {
      if (action === "submit") return submitBudgetVersion(projectId, version.id);
      if (action === "approve") {
        return approveBudgetVersion(projectId, version.id, Boolean(promote));
      }
      return rejectBudgetVersion(projectId, version.id);
    },
    onSuccess: () => {
      toast.success(t("common.saved", "ذخیره شد"));
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const compareMutation = useMutation({
    mutationFn: () => compareBudgetVersions(projectId, compareLeft, compareRight, fxRate || undefined),
    onSuccess: (data) => {
      setCompareResult(data);
      toast.success(t("pages.costs.compareDone", "مقایسه انجام شد"));
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <section className="space-y-3" data-testid="budget-versions-panel">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-sm font-semibold">
          {t("pages.costs.budgetVersions", "نسخه‌های بودجه")}
        </h3>
        {canEdit ? (
          <div className="flex flex-wrap items-center gap-2">
            <select
              className="rounded border px-2 py-1 text-sm"
              value={createKind}
              onChange={(e) => setCreateKind(e.target.value as "initial" | "final_forecast")}
              data-testid="budget-version-kind"
            >
              <option value="initial">اولیه</option>
              <option value="final_forecast">پیش‌بینی نهایی</option>
            </select>
            <Button
              size="sm"
              variant="secondary"
              data-testid="budget-version-create"
              loading={createMutation.isPending}
              onClick={() => createMutation.mutate()}
            >
              {t("pages.costs.newVersion", "نسخه جدید")}
            </Button>
          </div>
        ) : null}
      </div>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
      ) : versions.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          {t("pages.costs.noBudgetVersions", "هنوز نسخه‌ای ثبت نشده است.")}
        </p>
      ) : (
        <ul className="divide-y rounded-md border border-border">
          {versions.map((v) => {
            const selected = selectedVersionId === v.id;
            const kind = v.kind as BudgetVersionKind;
            return (
              <li
                key={v.id}
                className={`flex flex-wrap items-center justify-between gap-2 px-3 py-2 ${
                  selected ? "bg-muted/40" : ""
                }`}
              >
                <button
                  type="button"
                  className="text-start text-sm"
                  data-testid={`budget-version-${v.version_number}`}
                  onClick={() => onSelectVersion(v.id)}
                >
                  <span className="font-medium">
                    v{v.version_number} · {KIND_LABEL[kind] ?? kind}
                  </span>
                  <span className="ms-2 text-muted-foreground">
                    {STATUS_LABEL[v.status] ?? v.status}
                    {v.is_control ? " · کنترل" : ""}
                  </span>
                  <span className="ms-2 text-xs text-muted-foreground">
                    {formatFaAmount(v.total_amount)} · {v.line_count} ردیف
                  </span>
                </button>
                <div className="flex flex-wrap gap-1">
                  {canEdit && v.status === "draft" ? (
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => actionMutation.mutate({ version: v, action: "submit" })}
                    >
                      ارسال برای تصویب
                    </Button>
                  ) : null}
                  {canApprove && v.status === "submitted" ? (
                    <>
                      <Button
                        size="sm"
                        variant="primary"
                        onClick={() =>
                          actionMutation.mutate({
                            version: v,
                            action: "approve",
                            promote: kind === "final_forecast",
                          })
                        }
                      >
                        {kind === "final_forecast" ? "تصویب و کنترل" : "تصویب"}
                      </Button>
                      {kind === "final_forecast" ? (
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() =>
                            actionMutation.mutate({
                              version: v,
                              action: "approve",
                              promote: false,
                            })
                          }
                        >
                          تصویب بدون کنترل
                        </Button>
                      ) : null}
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => actionMutation.mutate({ version: v, action: "reject" })}
                      >
                        رد
                      </Button>
                    </>
                  ) : null}
                </div>
              </li>
            );
          })}
        </ul>
      )}

      {versions.length >= 2 ? (
        <div className="space-y-2 rounded border p-3" data-testid="budget-version-compare">
          <p className="text-sm font-medium">{t("pages.costs.compareTitle", "مقایسه نسخه‌ها")}</p>
          <div className="grid gap-2 md:grid-cols-3">
            <label className="block space-y-1 text-xs">
              <span>نسخه چپ</span>
              <select
                className="w-full rounded border px-2 py-1 text-sm"
                value={compareLeft}
                onChange={(e) => setCompareLeft(e.target.value)}
              >
                <option value="">—</option>
                {versions.map((v) => (
                  <option key={v.id} value={v.id}>
                    v{v.version_number} ({v.currency})
                  </option>
                ))}
              </select>
            </label>
            <label className="block space-y-1 text-xs">
              <span>نسخه راست</span>
              <select
                className="w-full rounded border px-2 py-1 text-sm"
                value={compareRight}
                onChange={(e) => setCompareRight(e.target.value)}
              >
                <option value="">—</option>
                {versions.map((v) => (
                  <option key={v.id} value={v.id}>
                    v{v.version_number} ({v.currency})
                  </option>
                ))}
              </select>
            </label>
            <label className="block space-y-1 text-xs">
              <span>نرخ تبدیل (در صورت ارز متفاوت)</span>
              <Input value={fxRate} onChange={(e) => setFxRate(e.target.value)} />
            </label>
          </div>
          <Button
            size="sm"
            variant="secondary"
            disabled={!compareLeft || !compareRight || compareLeft === compareRight}
            loading={compareMutation.isPending}
            onClick={() => compareMutation.mutate()}
          >
            مقایسه
          </Button>
          {compareResult ? (
            <div className="max-h-48 overflow-auto text-xs">
              <p className="mb-1 text-muted-foreground">
                FX={compareResult.fx_rate} · {compareResult.diffs.length} سرفصل
              </p>
              <ul className="space-y-1">
                {compareResult.diffs.slice(0, 20).map((d) => (
                  <li key={d.key}>
                    {d.key}: {formatFaAmount(d.left_amount)} → {formatFaAmount(d.right_amount)} (Δ{" "}
                    {formatFaAmount(d.delta)})
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
