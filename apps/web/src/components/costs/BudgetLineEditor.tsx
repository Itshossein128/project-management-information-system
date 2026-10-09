import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { fetchCBS } from "@/app/lib/api/central-data";
import { fetchContracts } from "@/app/lib/api/contracts";
import {
  COST_CATEGORIES,
  createBudgetVersionLine,
  type BudgetLineLevel,
  type CostCategory,
} from "@/app/lib/api/costs";
import { fetchWBSFlat } from "@/app/lib/api/wbs";
import { Input } from "@/components/form";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

const LEVELS: { value: BudgetLineLevel; label: string }[] = [
  { value: "project", label: "پروژه" },
  { value: "phase", label: "فاز (WBS)" },
  { value: "contract", label: "قرارداد" },
  { value: "wbs", label: "بسته WBS" },
  { value: "cbs", label: "CBS" },
];

interface Props {
  projectId: string;
  versionId: string;
  enabled: boolean;
}

export function BudgetLineEditor({ projectId, versionId, enabled }: Props) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const [level, setLevel] = useState<BudgetLineLevel>("wbs");
  const [category, setCategory] = useState<CostCategory>("labor");
  const [amount, setAmount] = useState("");
  const [wbsId, setWbsId] = useState("");
  const [cbsId, setCbsId] = useState("");
  const [contractId, setContractId] = useState("");
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");

  const { data: wbsFlat = [] } = useQuery({
    queryKey: ["wbs-flat", projectId],
    queryFn: () => fetchWBSFlat(projectId),
    enabled,
  });
  const { data: cbsNodes = [] } = useQuery({
    queryKey: ["cbs", projectId],
    queryFn: () => fetchCBS(projectId),
    enabled: enabled && (level === "cbs" || level === "wbs" || level === "phase"),
  });
  const { data: contractsData } = useQuery({
    queryKey: ["contracts", projectId, "budget-line"],
    queryFn: () => fetchContracts(projectId),
    enabled: enabled && level === "contract",
  });

  const mutation = useMutation({
    mutationFn: () =>
      createBudgetVersionLine(projectId, versionId, {
        level,
        cost_category: category,
        budget_amount: amount.trim(),
        wbs: wbsId || null,
        cbs: cbsId || null,
        contract: contractId || null,
        period_start: periodStart || null,
        period_end: periodEnd || null,
      }),
    onSuccess: () => {
      toast.success(t("pages.costs.lineCreated", "ردیف بودجه اضافه شد"));
      setAmount("");
      void qc.invalidateQueries({ queryKey: ["budgets", projectId] });
      void qc.invalidateQueries({ queryKey: ["budget-versions", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (!enabled) return null;

  const needsWbs = level === "phase" || level === "wbs";
  const needsCbs = level === "cbs";
  const needsContract = level === "contract";

  return (
    <section className="space-y-3 rounded border p-3" data-testid="budget-line-editor">
      <h4 className="text-sm font-semibold">
        {t("pages.costs.addMultiLevelLine", "افزودن ردیف چندسطحی")}
      </h4>
      <div className="grid gap-2 md:grid-cols-2">
        <label className="block space-y-1 text-xs">
          <span>سطح</span>
          <select
            className="w-full rounded border px-2 py-1 text-sm"
            value={level}
            onChange={(e) => setLevel(e.target.value as BudgetLineLevel)}
          >
            {LEVELS.map((l) => (
              <option key={l.value} value={l.value}>
                {l.label}
              </option>
            ))}
          </select>
        </label>
        <label className="block space-y-1 text-xs">
          <span>سرفصل</span>
          <select
            className="w-full rounded border px-2 py-1 text-sm"
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
        {needsWbs ? (
          <label className="block space-y-1 text-xs">
            <span>WBS</span>
            <select
              className="w-full rounded border px-2 py-1 text-sm"
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
        ) : null}
        {needsCbs ? (
          <label className="block space-y-1 text-xs">
            <span>CBS</span>
            <select
              className="w-full rounded border px-2 py-1 text-sm"
              value={cbsId}
              onChange={(e) => setCbsId(e.target.value)}
            >
              <option value="">—</option>
              {cbsNodes.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.cbs_code} — {n.cbs_name}
                </option>
              ))}
            </select>
          </label>
        ) : null}
        {needsContract ? (
          <label className="block space-y-1 text-xs">
            <span>قرارداد</span>
            <select
              className="w-full rounded border px-2 py-1 text-sm"
              value={contractId}
              onChange={(e) => setContractId(e.target.value)}
            >
              <option value="">—</option>
              {(contractsData?.results ?? []).map((c) => (
                <option key={c.id} value={c.id}>
                  {c.contract_number}
                </option>
              ))}
            </select>
          </label>
        ) : null}
        <label className="block space-y-1 text-xs">
          <span>{t("pages.costs.transferAmount", "مبلغ")}</span>
          <Input value={amount} onChange={(e) => setAmount(e.target.value)} />
        </label>
        <label className="block space-y-1 text-xs">
          <span>شروع دوره (اختیاری)</span>
          <Input value={periodStart} onChange={(e) => setPeriodStart(e.target.value)} placeholder="YYYY-MM-DD" />
        </label>
        <label className="block space-y-1 text-xs">
          <span>پایان دوره (اختیاری)</span>
          <Input value={periodEnd} onChange={(e) => setPeriodEnd(e.target.value)} placeholder="YYYY-MM-DD" />
        </label>
      </div>
      <Button
        size="sm"
        variant="primary"
        disabled={
          !amount.trim() ||
          (needsWbs && !wbsId) ||
          (needsCbs && !cbsId) ||
          (needsContract && !contractId)
        }
        loading={mutation.isPending}
        onClick={() => mutation.mutate()}
      >
        افزودن ردیف
      </Button>
    </section>
  );
}
