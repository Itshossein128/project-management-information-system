import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useMemo, useState } from "react";
import { fetchActivities } from "@/app/lib/api/activities";
import {
  COST_CATEGORIES,
  fetchBudgets,
  formatFaAmount,
  parseFaAmount,
  postBudgetsBulk,
  type CostCategory,
} from "@/app/lib/api/costs";
import { fetchWBSFlat } from "@/app/lib/api/wbs";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

type GridMode = "wbs" | "activity";

interface RowDef {
  id: string;
  code: string;
  name: string;
  wbsId?: string;
}

function cellKey(rowId: string, cat: CostCategory) {
  return `${rowId}:${cat}`;
}

export function BudgetGrid({
  projectId,
  canEdit,
}: {
  projectId: string;
  canEdit: boolean;
}) {
  const toast = useToast();
  const qc = useQueryClient();
  const [mode, setMode] = useState<GridMode>("wbs");
  const [edits, setEdits] = useState<Record<string, number>>({});
  const [editingCell, setEditingCell] = useState<string | null>(null);

  const { data: budgetData, isLoading: budgetsLoading } = useQuery({
    queryKey: ["budgets", projectId],
    queryFn: () => fetchBudgets(projectId),
  });

  const { data: wbsFlat = [], isLoading: wbsLoading } = useQuery({
    queryKey: ["wbs-flat", projectId],
    queryFn: () => fetchWBSFlat(projectId),
    enabled: mode === "wbs",
  });

  const { data: activitiesData, isLoading: actLoading } = useQuery({
    queryKey: ["activities", projectId, "budget-grid"],
    queryFn: () => fetchActivities(projectId, { per_page: 500 }),
    enabled: mode === "activity",
  });

  const rows: RowDef[] = useMemo(() => {
    if (mode === "wbs") {
      return wbsFlat.map((w) => ({
        id: w.wbs_id,
        code: w.wbs_code,
        name: w.wbs_name,
      }));
    }
    return (activitiesData?.results ?? []).map((a) => ({
      id: a.activity_id,
      code: a.activity_code,
      name: a.activity_name,
      wbsId: a.wbs_id,
    }));
  }, [mode, wbsFlat, activitiesData]);

  const baseAmounts = useMemo(() => {
    const map: Record<string, number> = {};
    for (const b of budgetData?.results ?? []) {
      const rowId = mode === "wbs" ? b.wbs : b.activity;
      if (!rowId) continue;
      if (mode === "wbs" && b.activity) continue;
      if (mode === "activity" && !b.activity) continue;
      map[cellKey(rowId, b.cost_category)] = b.budget_amount;
    }
    return map;
  }, [budgetData, mode]);

  const getAmount = useCallback(
    (rowId: string, cat: CostCategory) => {
      const k = cellKey(rowId, cat);
      if (k in edits) return edits[k];
      return baseAmounts[k] ?? 0;
    },
    [edits, baseAmounts],
  );

  const colTotals = useMemo(() => {
    const totals: Record<CostCategory, number> = Object.fromEntries(
      COST_CATEGORIES.map((c) => [c.value, 0]),
    ) as Record<CostCategory, number>;
    for (const row of rows) {
      for (const cat of COST_CATEGORIES) {
        totals[cat.value] += getAmount(row.id, cat.value);
      }
    }
    return totals;
  }, [rows, getAmount]);

  const rowTotals = useMemo(() => {
    const totals: Record<string, number> = {};
    for (const row of rows) {
      totals[row.id] = COST_CATEGORIES.reduce(
        (sum, cat) => sum + getAmount(row.id, cat.value),
        0,
      );
    }
    return totals;
  }, [rows, getAmount]);

  const grandTotal = useMemo(
    () => Object.values(colTotals).reduce((s, v) => s + v, 0),
    [colTotals],
  );

  const saveMutation = useMutation({
    mutationFn: () => {
      const items: Parameters<typeof postBudgetsBulk>[1] = [];
      for (const row of rows) {
        for (const cat of COST_CATEGORIES) {
          const k = cellKey(row.id, cat.value);
          if (!(k in edits)) continue;
          const amount = edits[k];
          if (mode === "wbs") {
            items.push({ wbs: row.id, cost_category: cat.value, budget_amount: amount });
          } else {
            items.push({
              wbs: row.wbsId ?? null,
              activity: row.id,
              cost_category: cat.value,
              budget_amount: amount,
            });
          }
        }
      }
      return postBudgetsBulk(projectId, items);
    },
    onSuccess: (res) => {
      toast.success(`${res.saved} بودجه ذخیره شد`);
      if (res.warning) toast.error(res.warning);
      setEdits({});
      void qc.invalidateQueries({ queryKey: ["budgets", projectId] });
      void qc.invalidateQueries({ queryKey: ["cost-summary", projectId] });
      void qc.invalidateQueries({ queryKey: ["cost-variance", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const isLoading = budgetsLoading || (mode === "wbs" ? wbsLoading : actLoading);
  const hasEdits = Object.keys(edits).length > 0;

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">در حال بارگذاری ماتریس بودجه…</p>;
  }

  return (
    <div className="space-y-4">
      {budgetData?.warning ? (
        <p className="rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-900 dark:bg-amber-950/40 dark:text-amber-100">
          {budgetData.warning}
        </p>
      ) : null}

      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex gap-2">
          <Button
            size="sm"
            variant={mode === "wbs" ? "primary" : "secondary"}
            onClick={() => {
              setMode("wbs");
              setEdits({});
            }}
          >
            WBS
          </Button>
          <Button
            size="sm"
            variant={mode === "activity" ? "primary" : "secondary"}
            onClick={() => {
              setMode("activity");
              setEdits({});
            }}
          >
            فعالیت
          </Button>
        </div>
        {canEdit && hasEdits ? (
          <Button
            variant="primary"
            size="sm"
            loading={saveMutation.isPending}
            onClick={() => saveMutation.mutate()}
          >
            ذخیره تغییرات
          </Button>
        ) : null}
      </div>

      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full min-w-[900px] text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="sticky start-0 z-10 bg-muted/50 px-3 py-2 text-start">کد</th>
              <th className="px-3 py-2 text-start">عنوان</th>
              {COST_CATEGORIES.map((c) => (
                <th key={c.value} className="px-2 py-2 text-center whitespace-nowrap">
                  {c.label}
                </th>
              ))}
              <th className="px-3 py-2 text-center font-semibold">جمع</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className="border-t border-border">
                <td className="sticky start-0 z-10 bg-card px-3 py-1 font-mono text-xs">
                  {row.code}
                </td>
                <td className="px-3 py-1 max-w-[200px] truncate" title={row.name}>
                  {row.name}
                </td>
                {COST_CATEGORIES.map((cat) => {
                  const k = cellKey(row.id, cat.value);
                  const amount = getAmount(row.id, cat.value);
                  const isEditing = editingCell === k;
                  return (
                    <td key={cat.value} className="px-1 py-1 text-center">
                      {canEdit && isEditing ? (
                        <input
                          autoFocus
                          className="w-24 rounded border px-1 py-0.5 text-center text-xs"
                          defaultValue={amount ? String(amount) : ""}
                          onBlur={(e) => {
                            const val = parseFaAmount(e.target.value);
                            setEdits((prev) => ({ ...prev, [k]: val }));
                            setEditingCell(null);
                          }}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") (e.target as HTMLInputElement).blur();
                          }}
                        />
                      ) : (
                        <button
                          type="button"
                          className="w-full rounded px-1 py-0.5 hover:bg-muted/60 disabled:cursor-default"
                          disabled={!canEdit}
                          onClick={() => canEdit && setEditingCell(k)}
                        >
                          {amount ? formatFaAmount(amount) : "—"}
                        </button>
                      )}
                    </td>
                  );
                })}
                <td className="px-3 py-1 text-center font-medium">
                  {rowTotals[row.id] ? formatFaAmount(rowTotals[row.id]) : "—"}
                </td>
              </tr>
            ))}
            <tr className="border-t-2 border-border bg-muted/30 font-semibold">
              <td colSpan={2} className="px-3 py-2">
                جمع ستون‌ها
              </td>
              {COST_CATEGORIES.map((cat) => (
                <td key={cat.value} className="px-2 py-2 text-center">
                  {colTotals[cat.value] ? formatFaAmount(colTotals[cat.value]) : "—"}
                </td>
              ))}
              <td className="px-3 py-2 text-center">{formatFaAmount(grandTotal)}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
