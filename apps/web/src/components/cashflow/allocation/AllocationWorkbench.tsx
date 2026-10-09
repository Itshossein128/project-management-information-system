import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";
import {
  compareAllocationSimulation,
  createAllocationDecision,
  createLiquidityCycle,
  fetchPortfolioCashReport,
  formatFaAmount,
  listLiquidityCycles,
  proposeAllocation,
  saveAllocationSimulation,
} from "@/app/lib/api/cashflow";
import { PATHS } from "@/app/routeVars";
import { Button } from "@/components/ui/sprint-button";
import { LoadingSkeleton } from "@/components/layout/page-header";

export function AllocationWorkbench() {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const [cycleId, setCycleId] = useState<string>("");
  const [name, setName] = useState("2026-Q4");
  const [liquidity, setLiquidity] = useState("5000000");
  const [rationale, setRationale] = useState("");
  const [ownerId, setOwnerId] = useState("");
  const [acknowledge, setAcknowledge] = useState(false);
  const [decisionError, setDecisionError] = useState<string | null>(null);
  const [proposal, setProposal] = useState<Awaited<
    ReturnType<typeof proposeAllocation>
  > | null>(null);
  const [simDiffs, setSimDiffs] = useState<
    Array<{ project_id: string; diff: number; simulation_amount: number; proposal_amount: number }>
  >([]);

  const cycles = useQuery({
    queryKey: ["liquidity-cycles"],
    queryFn: listLiquidityCycles,
  });
  const report = useQuery({
    queryKey: ["portfolio-cash-report", cycleId],
    queryFn: () => fetchPortfolioCashReport("2026-10", "2026-12", cycleId || undefined),
  });

  const createCycle = useMutation({
    mutationFn: () =>
      createLiquidityCycle({
        name,
        period_start: "2026-10-01",
        period_end: "2026-12-31",
        available_liquidity: liquidity,
      }),
    onSuccess: (c) => {
      setCycleId(c.id);
      void qc.invalidateQueries({ queryKey: ["liquidity-cycles"] });
    },
  });

  const runPropose = useMutation({
    mutationFn: () => proposeAllocation(cycleId),
    onSuccess: (p) => setProposal(p),
  });

  const saveDecision = useMutation({
    mutationFn: () =>
      createAllocationDecision(cycleId, {
        owner_id: ownerId,
        rationale,
        acknowledge_overlap: acknowledge,
        lines: (proposal?.lines ?? []).map((l) => ({
          project_id: l.project_id,
          amount: l.suggested_amount,
          period_start: "2026-10-01",
          period_end: "2026-10-31",
        })),
      }),
    onSuccess: () => {
      setDecisionError(null);
      void qc.invalidateQueries({ queryKey: ["portfolio-cash-report"] });
    },
    onError: (err: unknown) => {
      const msg = err instanceof Error ? err.message : String(err);
      setDecisionError(msg);
      if (msg.includes("overlapping_allocation")) {
        setAcknowledge(true);
      }
    },
  });

  const runSim = useMutation({
    mutationFn: async () => {
      const sim = await saveAllocationSimulation(cycleId, {
        name: "alt",
        lines: (proposal?.lines ?? []).map((l) => ({
          project_id: l.project_id,
          amount: Math.max(0, l.suggested_amount * 0.8),
        })),
      });
      return compareAllocationSimulation(cycleId, sim.id);
    },
    onSuccess: (c) => setSimDiffs(c.diffs),
  });

  return (
    <div className="space-y-8" data-testid="allocation-workbench">
      <section className="space-y-3">
        <h2 className="text-lg font-medium">{t("pages.portfolioLiquidity.cycleTitle")}</h2>
        <div className="flex flex-wrap gap-2">
          <input
            className="rounded border px-2 py-1"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={t("pages.portfolioLiquidity.cycleName")}
          />
          <input
            className="rounded border px-2 py-1"
            value={liquidity}
            onChange={(e) => setLiquidity(e.target.value)}
            placeholder={t("pages.portfolioLiquidity.availableLiquidity")}
          />
          <Button type="button" onClick={() => createCycle.mutate()}>
            {t("pages.portfolioLiquidity.createCycle")}
          </Button>
        </div>
        {(cycles.data?.results ?? []).length > 0 && (
          <select
            className="rounded border px-2 py-1"
            value={cycleId}
            onChange={(e) => setCycleId(e.target.value)}
          >
            <option value="">{t("pages.portfolioLiquidity.selectCycle")}</option>
            {cycles.data?.results.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name} ({c.status})
              </option>
            ))}
          </select>
        )}
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">{t("pages.portfolioLiquidity.proposalTitle")}</h2>
        <Button type="button" disabled={!cycleId} onClick={() => runPropose.mutate()}>
          {t("pages.portfolioLiquidity.generateProposal")}
        </Button>
        {proposal?.message === "no_available_liquidity" && (
          <p className="text-sm text-warning-800">{t("pages.portfolioLiquidity.noLiquidity")}</p>
        )}
        {proposal && proposal.lines.length > 0 && (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-start">
                <th className="p-2">{t("pages.portfolioLiquidity.rank")}</th>
                <th className="p-2">{t("pages.portfolioLiquidity.project")}</th>
                <th className="p-2">{t("pages.portfolioLiquidity.amount")}</th>
              </tr>
            </thead>
            <tbody>
              {proposal.lines.map((l) => (
                <tr key={l.project_id} className="border-b">
                  <td className="p-2">{l.rank}</td>
                  <td className="p-2">{l.project_id.slice(0, 8)}…</td>
                  <td className="p-2">{formatFaAmount(l.suggested_amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">{t("pages.portfolioLiquidity.decisionTitle")}</h2>
        <input
          className="w-full max-w-md rounded border px-2 py-1"
          value={ownerId}
          onChange={(e) => setOwnerId(e.target.value)}
          placeholder={t("pages.portfolioLiquidity.ownerId")}
        />
        <textarea
          className="w-full max-w-md rounded border px-2 py-1"
          value={rationale}
          onChange={(e) => setRationale(e.target.value)}
          placeholder={t("pages.portfolioLiquidity.rationale")}
          rows={3}
        />
        {acknowledge && (
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={acknowledge}
              onChange={(e) => setAcknowledge(e.target.checked)}
            />
            {t("pages.portfolioLiquidity.acknowledgeOverlap")}
          </label>
        )}
        {decisionError && (
          <p className="text-sm text-danger-700" data-testid="decision-error">
            {decisionError.includes("overlapping_allocation")
              ? t("pages.portfolioLiquidity.overlapWarning")
              : decisionError}
          </p>
        )}
        <Button
          type="button"
          disabled={!cycleId || !ownerId || !rationale}
          onClick={() => saveDecision.mutate()}
        >
          {t("pages.portfolioLiquidity.saveDecision")}
        </Button>
        <Button type="button" variant="secondary" disabled={!cycleId || !proposal} onClick={() => runSim.mutate()}>
          {t("pages.portfolioLiquidity.simulate")}
        </Button>
        {simDiffs.length > 0 && (
          <ul className="text-sm">
            {simDiffs.map((d) => (
              <li key={d.project_id}>
                {d.project_id.slice(0, 8)}… Δ {formatFaAmount(d.diff)}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">{t("pages.portfolioLiquidity.reportTitle")}</h2>
        {report.isLoading ? (
          <LoadingSkeleton rows={4} />
        ) : (
          <table className="w-full text-sm" data-testid="portfolio-cash-report">
            <thead>
              <tr className="border-b text-start">
                <th className="p-2">{t("pages.portfolioLiquidity.project")}</th>
                <th className="p-2">{t("pages.cashFlow.projectedInflow")}</th>
                <th className="p-2">{t("pages.cashFlow.projectedOutflow")}</th>
                <th className="p-2">{t("pages.cashFlow.suggestedNetNeed")}</th>
                <th className="p-2">{t("pages.portfolioLiquidity.composite")}</th>
              </tr>
            </thead>
            <tbody>
              {(report.data?.projects ?? []).map((p) => (
                <tr key={p.project_id} className="border-b">
                  <td className="p-2">
                    <Link
                      className="underline"
                      to={`/${PATHS.PROJECT}/${p.project_id}/${PATHS.PROJECT_CASH_FLOW}`}
                    >
                      {p.project_name}
                    </Link>
                  </td>
                  <td className="p-2">
                    {p.inflow_status === "unregistered"
                      ? t("pages.cashFlow.noScheduledReceipts")
                      : formatFaAmount(p.projected_inflow)}
                  </td>
                  <td className="p-2">{formatFaAmount(p.projected_outflow)}</td>
                  <td className="p-2">{formatFaAmount(p.suggested_net_need)}</td>
                  <td className="p-2">{p.composite ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
