import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import {
  CalendarRange,
  Check,
  CircleHelp,
  ListOrdered,
  Plus,
  Wallet,
} from "lucide-react";
import {
  compareAllocationSimulation,
  createAllocationDecision,
  createLiquidityCycle,
  fetchPortfolioCashReport,
  listLiquidityCycles,
  proposeAllocation,
  saveAllocationSimulation,
  type ProposalResponse,
} from "@/app/lib/api/cashflow";
import { ApiRequestError } from "@/app/lib/api-client";
import { Input } from "@/components/form/Input";
import { Select } from "@/components/form/Select";
import { Field } from "@/components/form/Field";
import { Checkbox } from "@/components/form/Checkbox";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/sprint-button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { DataTable } from "@/components/ui/data-table";
import { EmptyState } from "@/components/layout/empty-state";
import { LoadingSkeleton } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { PortfolioCashReport } from "./PortfolioCashReport";
import {
  allocationDecisionBlocker,
  normalizeLiquidityAmount,
} from "./allocation-form";

const START = "2026-10-01",
  END = "2026-12-31",
  DECISION_END = "2026-10-31";
function StepCard({
  step,
  title,
  description,
  children,
}: {
  step: number;
  title: string;
  description: string;
  children: ReactNode;
}) {
  const { i18n } = useTranslation();
  return (
    <section
      id={`allocation-step-${step}`}
      aria-labelledby={`allocation-title-${step}`}
      className="scroll-mt-4 space-y-4 rounded-xl border border-border/80 bg-card p-4 shadow-sm sm:p-5"
    >
      <div className="flex items-start gap-3">
        <span
          className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary"
          aria-hidden="true"
        >
          {step.toLocaleString(i18n.language)}
        </span>
        <div>
          <h2 id={`allocation-title-${step}`} className="text-lg font-semibold">
            {title}
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">{description}</p>
        </div>
      </div>
      {children}
    </section>
  );
}

export function AllocationWorkbench() {
  const { t, i18n } = useTranslation();
  const ui = (key: string) => t(`pages.portfolioLiquidity.ui.${key}`);
  const qc = useQueryClient();
  const [cycleId, setCycleId] = useState("");
  const [name, setName] = useState("2026-Q4");
  const [liquidity, setLiquidity] = useState("5000000");
  const [createAttempted, setCreateAttempted] = useState(false);
  const [rationale, setRationale] = useState("");
  const [ownerId, setOwnerId] = useState("");
  const [acknowledge, setAcknowledge] = useState(false);
  const [proposalResult, setProposalResult] = useState<{
    cycleId: string;
    data: ProposalResponse;
  } | null>(null);
  const [simulationResult, setSimulationResult] = useState<{
    cycleId: string;
    diffs: Array<{
      project_id: string;
      diff: number;
      simulation_amount: number;
      proposal_amount: number;
    }>;
  } | null>(null);
  const proposal =
    proposalResult?.cycleId === cycleId ? proposalResult.data : null;
  const simDiffs =
    simulationResult?.cycleId === cycleId ? simulationResult.diffs : [];
  const normalizedLiquidity = normalizeLiquidityAmount(liquidity);
  const number = (value: number) => value.toLocaleString(i18n.language);
  const date = (value: string) =>
    new Intl.DateTimeFormat(i18n.language, {
      dateStyle: "medium",
      timeZone: "UTC",
    }).format(new Date(`${value}T00:00:00Z`));
  const period = `${date(START)} – ${date(END)}`;
  const cycles = useQuery({
    queryKey: ["liquidity-cycles"],
    queryFn: listLiquidityCycles,
  });
  const report = useQuery({
    queryKey: ["portfolio-cash-report", cycleId],
    queryFn: () =>
      fetchPortfolioCashReport("2026-10", "2026-12", cycleId || undefined),
  });
  const selectedCycle = cycles.data?.results.find(
    (cycle) => cycle.id === cycleId,
  );
  const projectName = (id: string) =>
    report.data?.projects.find((project) => project.project_id === id)
      ?.project_name ?? id;

  const changeCycle = (id: string) => {
    setCycleId(id);
    setProposalResult(null);
    setSimulationResult(null);
    setAcknowledge(false);
    setOwnerId("");
    setRationale("");
    runPropose.reset();
    saveDecision.reset();
    runSim.reset();
  };
  const createCycle = useMutation({
    mutationFn: () =>
      createLiquidityCycle({
        name: name.trim(),
        period_start: START,
        period_end: END,
        available_liquidity: normalizedLiquidity!,
        currency: "IRR",
      }),
    onSuccess: (cycle) => {
      changeCycle(cycle.id);
      void qc.invalidateQueries({ queryKey: ["liquidity-cycles"] });
    },
  });
  const runPropose = useMutation({
    mutationFn: (id: string) => proposeAllocation(id),
    onSuccess: (data, id) => {
      setProposalResult({ cycleId: id, data });
      setSimulationResult(null);
      setAcknowledge(false);
      saveDecision.reset();
      runSim.reset();
    },
  });
  const saveDecision = useMutation({
    mutationFn: (payload: {
      cycleId: string;
      ownerId: string;
      rationale: string;
      acknowledge: boolean;
      proposal: ProposalResponse;
    }) =>
      createAllocationDecision(payload.cycleId, {
        owner_id: payload.ownerId.trim(),
        rationale: payload.rationale.trim(),
        acknowledge_overlap: payload.acknowledge,
        lines: payload.proposal.lines.map((line) => ({
          project_id: line.project_id,
          amount: line.suggested_amount,
          period_start: START,
          period_end: DECISION_END,
        })),
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["portfolio-cash-report"] });
    },
  });
  const runSim = useMutation({
    mutationFn: async (payload: {
      cycleId: string;
      proposal: ProposalResponse;
    }) => {
      const simulation = await saveAllocationSimulation(payload.cycleId, {
        name: "alt",
        lines: payload.proposal.lines.map((line) => ({
          project_id: line.project_id,
          amount: Math.max(0, line.suggested_amount * 0.8),
        })),
      });
      return compareAllocationSimulation(payload.cycleId, simulation.id);
    },
    onSuccess: (data, payload) =>
      setSimulationResult({ cycleId: payload.cycleId, diffs: data.diffs }),
  });
  const busy =
    createCycle.isPending ||
    runPropose.isPending ||
    saveDecision.isPending ||
    runSim.isPending;
  const overlapRequired =
    (saveDecision.error instanceof ApiRequestError &&
      saveDecision.error.code === "overlapping_allocation") ||
    Boolean(saveDecision.error?.message.includes("overlapping_allocation"));
  const blocker = allocationDecisionBlocker({
    cycleId,
    proposalCycleId: proposalResult?.cycleId ?? "",
    lineCount: proposal?.lines.length ?? 0,
    ownerId,
    rationale,
    overlapRequired,
    acknowledged: acknowledge,
  });
  const currentStep = !cycleId ? 1 : !proposal?.lines.length ? 2 : 3;
  const mutationError = (error: Error | null) =>
    error ? (
      <Alert variant="destructive">
        <AlertDescription>
          {error.message || ui("actionFailed")}
        </AlertDescription>
      </Alert>
    ) : null;
  const amount = (value: number) => (
    <bdi className="tabular-nums">{number(value)}</bdi>
  );
  const proposalColumns = [
    {
      key: "rank",
      label: t("pages.portfolioLiquidity.rank"),
      render: (line: ProposalResponse["lines"][number]) => number(line.rank),
    },
    {
      key: "project",
      label: t("pages.portfolioLiquidity.project"),
      render: (line: ProposalResponse["lines"][number]) => (
        <bdi className="break-all font-medium">
          {projectName(line.project_id)}
        </bdi>
      ),
    },
    {
      key: "suggested_amount",
      label: t("pages.portfolioLiquidity.amount"),
      render: (line: ProposalResponse["lines"][number]) =>
        amount(line.suggested_amount),
    },
  ];

  return (
    <div className="space-y-5" data-testid="allocation-workbench">
      <nav aria-label={ui("workflow")}>
        <ol className="grid grid-cols-3 gap-2">
          {["cycleTitle", "proposalTitle", "decisionTitle"].map(
            (key, index) => (
              <li key={key}>
                <a
                  href={`#allocation-step-${index + 1}`}
                  aria-current={currentStep === index + 1 ? "step" : undefined}
                  className={`flex h-full min-w-0 flex-col items-center gap-2 rounded-xl border p-3 text-center text-sm font-medium sm:flex-row sm:text-start focus-visible:outline-2 focus-visible:outline-ring ${currentStep === index + 1 ? "border-primary/30 bg-primary/10 text-foreground" : "border-border/70 bg-card text-muted-foreground"}`}
                >
                  <span
                    className="flex size-6 shrink-0 items-center justify-center rounded-full bg-background text-xs"
                    aria-hidden="true"
                  >
                    {currentStep > index + 1 ||
                    (index === 2 && saveDecision.isSuccess) ? (
                      <Check className="size-3.5" />
                    ) : (
                      number(index + 1)
                    )}
                  </span>
                  {t(`pages.portfolioLiquidity.${key}`)}
                </a>
              </li>
            ),
          )}
        </ol>
      </nav>
      <p className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
        <CalendarRange className="size-4 shrink-0" aria-hidden="true" />
        {ui("reportPeriod")}: <span>{period}</span>
      </p>

      <StepCard
        step={1}
        title={t("pages.portfolioLiquidity.cycleTitle")}
        description={ui("cycleHint")}
      >
        {cycles.isLoading ? (
          <LoadingSkeleton rows={2} />
        ) : cycles.isError ? (
          <QueryErrorState onRetry={() => void cycles.refetch()} />
        ) : cycles.data?.results.length ? (
          <Select
            name="liquidity-cycle"
            label={t("pages.portfolioLiquidity.selectCycle")}
            value={cycleId || "none"}
            disabled={busy}
            onChange={(event) =>
              changeCycle(
                event.target.value === "none" ? "" : event.target.value,
              )
            }
            options={[
              {
                value: "none",
                label: t("pages.portfolioLiquidity.selectCycle"),
              },
              ...(cycles.data?.results ?? []).map((cycle) => ({
                value: cycle.id,
                label: cycle.name,
              })),
            ]}
            className="min-h-10"
          />
        ) : (
          <p className="rounded-lg bg-muted/50 p-3 text-sm text-muted-foreground">
            {ui("noCycles")}
          </p>
        )}
        {selectedCycle ? (
          <div
            className="flex flex-wrap items-center justify-between gap-2 rounded-lg bg-muted/40 p-3 text-sm"
            role="status"
          >
            <span className="font-medium">{selectedCycle.name}</span>
            <span>
              {date(selectedCycle.period_start)} –{" "}
              {date(selectedCycle.period_end)}
            </span>
            <span className="inline-flex items-center gap-2">
              <Wallet className="size-4" aria-hidden="true" />
              {amount(Number(selectedCycle.available_liquidity))}
              <span className="text-muted-foreground">
                {selectedCycle.currency}
              </span>
            </span>
          </div>
        ) : null}
        <form
          noValidate
          onSubmit={(event) => {
            event.preventDefault();
            setCreateAttempted(true);
            if (!name.trim() || normalizedLiquidity == null) {
              event.currentTarget
                .querySelector<HTMLInputElement>(
                  name.trim()
                    ? "#liquidity-cycle-amount"
                    : "#liquidity-cycle-name",
                )
                ?.focus();
            } else if (!busy) {
              createCycle.mutate();
            }
          }}
          className="space-y-3 border-t border-border/60 pt-4"
        >
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <Plus className="size-4" aria-hidden="true" />
            {t("pages.portfolioLiquidity.createCycle")}
          </h3>
          <div className="grid items-start gap-4 sm:grid-cols-2">
            <Field
              name="cycle-name"
              label={t("pages.portfolioLiquidity.cycleName")}
              htmlFor="liquidity-cycle-name"
              error={
                createAttempted && !name.trim() ? ui("nameRequired") : undefined
              }
            >
              {() => (
                <Input
                  id="liquidity-cycle-name"
                  value={name}
                  onChange={(event) => {
                    setName(event.target.value);
                    createCycle.reset();
                  }}
                  aria-invalid={(createAttempted && !name.trim()) || undefined}
                  aria-describedby={
                    createAttempted && !name.trim()
                      ? "text-cycle-nameInputError"
                      : undefined
                  }
                  className="h-10"
                  disabled={busy}
                  required
                />
              )}
            </Field>
            <Field
              name="cycle-amount"
              label={`${t("pages.portfolioLiquidity.availableLiquidity")} (IRR)`}
              htmlFor="liquidity-cycle-amount"
              helpText={ui("amountHint")}
              error={
                createAttempted && normalizedLiquidity == null
                  ? ui("amountInvalid")
                  : undefined
              }
            >
              {() => (
                <Input
                  id="liquidity-cycle-amount"
                  inputMode="decimal"
                  value={liquidity}
                  onChange={(event) => {
                    setLiquidity(event.target.value);
                    createCycle.reset();
                  }}
                  aria-invalid={
                    (createAttempted && normalizedLiquidity == null) ||
                    undefined
                  }
                  aria-describedby={`text-cycle-amountInputHelper${createAttempted && normalizedLiquidity == null ? " text-cycle-amountInputError" : ""}`}
                  className="h-10"
                  disabled={busy}
                  required
                />
              )}
            </Field>
          </div>
          <p className="text-xs text-muted-foreground">
            {ui("newCyclePeriod")}: {period}
          </p>
          {mutationError(createCycle.error)}
          {createCycle.isSuccess ? (
            <p
              role="status"
              className="text-sm text-success-800 dark:text-success-300"
            >
              {ui("cycleCreated")}
            </p>
          ) : null}
          <Button
            type="submit"
            className="min-h-10"
            loading={createCycle.isPending}
            disabled={busy}
          >
            <Plus className="size-4" aria-hidden="true" />
            {t("pages.portfolioLiquidity.createCycle")}
          </Button>
        </form>
      </StepCard>

      <StepCard
        step={2}
        title={t("pages.portfolioLiquidity.proposalTitle")}
        description={ui("proposalHint")}
      >
        {!cycleId ? (
          <p className="flex items-start gap-2 rounded-lg bg-muted/50 p-3 text-sm text-muted-foreground">
            <CircleHelp className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
            {ui("cycleRequired")}
          </p>
        ) : null}
        <Button
          type="button"
          className="min-h-10"
          loading={runPropose.isPending}
          disabled={!cycleId || busy}
          onClick={() => runPropose.mutate(cycleId)}
        >
          <ListOrdered className="size-4" aria-hidden="true" />
          {t("pages.portfolioLiquidity.generateProposal")}
        </Button>
        {mutationError(runPropose.error)}
        {proposal ? (
          <>
            {proposal.lines.length ? (
              <>
                <p className="text-xs text-muted-foreground">
                  {ui("proposalCurrency")}: {selectedCycle?.currency ?? "IRR"}
                </p>
                <DataTable
                  columns={proposalColumns}
                  data={proposal.lines}
                  rowKey={(line) => line.project_id}
                />
              </>
            ) : (
              <EmptyState
                title={
                  proposal.message === "no_available_liquidity"
                    ? t("pages.portfolioLiquidity.noLiquidity")
                    : ui("proposalEmpty")
                }
                description={ui("proposalEmptyHint")}
              />
            )}
            {proposal.warnings?.incomplete_score_projects?.length ? (
              <p
                role="status"
                className="text-sm text-warning-800 dark:text-warning-300"
              >
                {t("pages.portfolioLiquidity.ui.incompleteScores", {
                  count: proposal.warnings.incomplete_score_projects.length,
                })}
              </p>
            ) : null}
          </>
        ) : null}
      </StepCard>

      <StepCard
        step={3}
        title={t("pages.portfolioLiquidity.decisionTitle")}
        description={ui("decisionHint")}
      >
        <form
          className="space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            if (!blocker && proposal && !busy && !saveDecision.isSuccess)
              saveDecision.mutate({
                cycleId,
                ownerId,
                rationale,
                acknowledge,
                proposal,
              });
          }}
        >
          <p className="text-xs text-muted-foreground">
            {ui("decisionPeriod")}: {date(START)} – {date(DECISION_END)}
          </p>
          <Field
            name="decision-owner"
            label={t("pages.portfolioLiquidity.ownerId")}
            htmlFor="liquidity-owner"
            helpText={ui("ownerHint")}
          >
            {() => (
              <Input
                id="liquidity-owner"
                value={ownerId}
                onChange={(event) => {
                  setOwnerId(event.target.value);
                  setAcknowledge(false);
                  saveDecision.reset();
                }}
                disabled={busy || !proposal?.lines.length}
                aria-describedby="text-decision-ownerInputHelper"
                className="h-10"
                required
              />
            )}
          </Field>
          <Field
            name="decision-rationale"
            label={t("pages.portfolioLiquidity.rationale")}
            htmlFor="liquidity-rationale"
          >
            {() => (
              <Textarea
                id="liquidity-rationale"
                value={rationale}
                onChange={(event) => {
                  setRationale(event.target.value);
                  setAcknowledge(false);
                  saveDecision.reset();
                }}
                rows={3}
                required
                disabled={busy || !proposal?.lines.length}
              />
            )}
          </Field>
          {overlapRequired ? (
            <Alert>
              <AlertDescription className="space-y-3">
                <p>{t("pages.portfolioLiquidity.overlapWarning")}</p>
                <Checkbox
                  name="allocation-overlap"
                  label={t("pages.portfolioLiquidity.acknowledgeOverlap")}
                  checked={acknowledge}
                  onChange={(event) => setAcknowledge(event.target.checked)}
                  disabled={busy}
                />
              </AlertDescription>
            </Alert>
          ) : (
            mutationError(saveDecision.error)
          )}
          {saveDecision.isSuccess ? (
            <p
              role="status"
              className="text-sm text-success-800 dark:text-success-300"
            >
              {ui("decisionSaved")}
            </p>
          ) : blocker ? (
            <p
              id="allocation-decision-hint"
              className="text-sm text-muted-foreground"
              role="status"
            >
              {ui(blocker)}
            </p>
          ) : null}
          <div className="flex flex-wrap gap-2">
            <Button
              type="submit"
              className="min-h-10"
              loading={saveDecision.isPending}
              disabled={Boolean(blocker) || busy || saveDecision.isSuccess}
              aria-describedby={
                blocker ? "allocation-decision-hint" : undefined
              }
            >
              {t("pages.portfolioLiquidity.saveDecision")}
            </Button>
            <Button
              type="button"
              variant="secondary"
              className="min-h-10"
              loading={runSim.isPending}
              disabled={!proposal?.lines.length || busy}
              onClick={() => proposal && runSim.mutate({ cycleId, proposal })}
            >
              {t("pages.portfolioLiquidity.simulate")}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">
            {ui("simulationHint")}
          </p>
          {mutationError(runSim.error)}
          {simDiffs.length ? (
            <DataTable
              columns={[
                {
                  key: "project_id",
                  label: t("pages.portfolioLiquidity.project"),
                  render: (row) => (
                    <bdi className="break-all">
                      {projectName(row.project_id)}
                    </bdi>
                  ),
                },
                {
                  key: "simulation_amount",
                  label: ui("simulationAmount"),
                  render: (row) => amount(row.simulation_amount),
                },
                {
                  key: "diff",
                  label: ui("difference"),
                  render: (row) => amount(row.diff),
                },
              ]}
              data={simDiffs}
              rowKey={(row) => row.project_id}
            />
          ) : null}
        </form>
      </StepCard>
      <PortfolioCashReport
        key={cycleId}
        report={report}
        period={`${ui("reportPeriod")}: ${period}`}
      />
    </div>
  );
}
