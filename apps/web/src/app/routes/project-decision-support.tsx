import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, useRef, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router";
import { ProjectProvider, useProject, usePermission } from "@/app/contexts/project-context";
import {
  DECISION_METHODS,
  type DecisionCase,
  type CriterionType,
  type DecisionMethod,
  DecisionSupportRequestError,
  isSavedCase,
  createDecisionCase,
  getDecisionCase,
  getDecisionRun,
  listDecisionCases,
  listDecisionRuns,
  patchDecisionCase,
  type DecisionRun,
  type SawRankingRow,
  type TopsisRankingRow,
  type AhpRunResult,
} from "@/app/lib/api/decision-support";
import { PATHS } from "@/app/routeVars";
import { IsmMethodPanel } from "@/components/decision-support/IsmMethodPanel";
import { hydrateIsmMatrix, remapIsmMatrix } from "@/components/decision-support/ism-input-rules";
import { AhpMethodPanel } from "@/components/decision-support/AhpMethodPanel";
import { ExecutionHistoryList } from "@/components/decision-support/ExecutionHistoryList";
import { InputSnapshotViewer } from "@/components/decision-support/InputSnapshotViewer";
import { NamedListEditor } from "@/components/decision-support/NamedListEditor";
import { SawMethodPanel } from "@/components/decision-support/SawMethodPanel";
import { TopsisMethodPanel } from "@/components/decision-support/TopsisMethodPanel";
import { ValidationIssueList } from "@/components/decision-support/ValidationIssueList";
import { parseApiRequestIssues, parseApiValidationIssues } from "@/components/decision-support/validation-issues";
import { createDefaultPairwiseMatrix, reconcilePairwiseMatrix } from "@/components/decision-support/square-matrix-rules";
import { Button } from "@/components/form/Button";
import { Input } from "@/components/form/Input";
import { Label } from "@/components/form/Label";
import { Checkbox } from "@/components/ui/checkbox";
import { EmptyState, NotFoundState } from "@/components/layout/empty-state";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";

function alignWeights(n: number, weights: number[]): number[] {
  const next = [...weights];
  while (next.length < n) next.push(1);
  return next.slice(0, n);
}

function alignTypes(n: number, types: CriterionType[]): CriterionType[] {
  const next = [...types];
  while (next.length < n) next.push("benefit");
  return next.slice(0, n);
}

function DecisionSupportContent() {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canEdit = has("edit_decision_support");
  const canView = has("view_decision_support");
  const operation = useRef(new Map<string | null, object>());
  const [, updateOperationState] = useState(0);
  const selectedCase = useRef<string | null>(null);
  const operationBusy = operation.current.has(selectedCase.current);
  const beginOperation = () => {
    const caseId = selectedCase.current;
    if (!canEdit || operation.current.has(caseId)) return null;
    const token = {};
    const version = selectionVersion.current;
    operation.current.set(caseId, token);
    updateOperationState(value => value + 1);
    return () => {
      if (operation.current.get(caseId) !== token) return;
      operation.current.delete(caseId);
      updateOperationState(value => value + 1);
      // A return during the request may have loaded the pre-save row. Refresh
      // only that returning case; normal completion keeps its current result.
      if (caseId && selectedCase.current === caseId && version !== selectionVersion.current) {
        hydrateFromCase(caseId);
      }
    };
  };
  const selectionVersion = useRef(0);
  const historyVersion = useRef(0);
  const [caseLoading, setCaseLoading] = useState(false);
  const [savedCase, setSavedCase] = useState<DecisionCase | null>(null);
  const [historyMethod, setHistoryMethod] = useState<DecisionMethod | "">("");
  const [historyPage, setHistoryPage] = useState(1);
  const historyView = useRef({method:historyMethod,page:historyPage});
  historyView.current={method:historyMethod,page:historyPage};
  const showRecoveredHistory = (caseId: string) => {
    if (selectedCase.current !== caseId) return;
    if (historyView.current.method !== "" || historyView.current.page !== 1) navigateHistory("",1);
  };
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const navigateHistory = (method: DecisionMethod | "", page: number) => {
    ++historyVersion.current;setSelectedRun(null);setHistoryLoading(false);setHistoryError(null);setHistoryMethod(method);setHistoryPage(page);
  };
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [methods, setMethods] = useState<DecisionMethod[]>([]);
  const [criteria, setCriteria] = useState<string[]>([]);
  const [alternatives, setAlternatives] = useState<string[]>([]);
  const [weights, setWeights] = useState<number[]>([]);
  const [types, setTypes] = useState<CriterionType[]>([]);
  const [matrix, setMatrix] = useState<(number | null)[][]>([]);
  const [ismMatrix, setIsmMatrix] = useState<unknown>([]);
  const [ahpMatrix, setAhpMatrix] = useState<(number | null)[][]>([]);
  const [issues, setIssues] = useState(parseApiValidationIssues(null));
  const [selectedRun, setSelectedRun] = useState<DecisionRun | null>(null);
  const [latestSawRanking, setLatestSawRanking] = useState<SawRankingRow[]>([]);
  const [latestTopsisRanking, setLatestTopsisRanking] = useState<TopsisRankingRow[]>([]);
  const [latestAhpResult, setLatestAhpResult] = useState<AhpRunResult | null>(null);

  useEffect(()=>{
    if(!canView){++historyVersion.current;setSelectedRun(null);setHistoryError(null);setHistoryLoading(false);}
  },[canView]);
  const casesQuery = useQuery({
    queryKey: ["decision-cases", projectId],
    queryFn: () => listDecisionCases(projectId),
    enabled: !!projectId,
  });

  const runsQuery = useQuery({
    queryKey: ["decision-runs", projectId, selectedCaseId, historyMethod, historyPage],
    queryFn: ({ signal }) => listDecisionRuns(projectId, selectedCaseId!, { method: historyMethod || undefined, page: historyPage, pageSize: 10, signal }),
    enabled: !!projectId && !!selectedCaseId && !caseLoading && canView,
  });

  const hydrateFromCase = (caseId: string) => {
    if (selectedCase.current === caseId && operation.current.has(caseId)) return;
    selectedCase.current = caseId;
    const version = ++selectionVersion.current;
    ++historyVersion.current;
    setHistoryLoading(false);
    setHistoryError(null);
    setCaseLoading(true);
    setSavedCase(null);
    setTitle("");
    setMethods([]);
    setCriteria([]);
    setAhpMatrix([]);
    setIsmMatrix([]);
    setHistoryMethod("");
    setHistoryPage(1);
    setSelectedCaseId(caseId);
    setSelectedRun(null);
    setIssues([]);
    setLatestSawRanking([]);
    setLatestTopsisRanking([]);
    setLatestAhpResult(null);
    void getDecisionCase(projectId, caseId).then((c) => {
      if (version !== selectionVersion.current) return;
      setSavedCase(c);
      setTitle(c.title);
      setMethods([...(c.selected_methods ?? [])]);
      const crit = [...(c.criteria ?? [])];
      const alts = [...(c.alternatives ?? [])];
      setCriteria(crit);
      setIsmMatrix(hydrateIsmMatrix(c.ism_matrix,crit.length));
      setAlternatives(alts);
      setWeights([...(c.weights ?? [])]);
      setTypes([...(c.types ?? [])]);
      setMatrix([...(c.performance_matrix ?? [])]);
      setAhpMatrix(Array.isArray(c.ahp_matrix) && c.ahp_matrix.length === 0 ? createDefaultPairwiseMatrix(crit.length) : structuredClone(c.ahp_matrix));
    }).catch(err => {
      if (version === selectionVersion.current) setIssues(parseApiRequestIssues(null));
    }).finally(() => {
      if (version === selectionVersion.current) setCaseLoading(false);
    });
  };

  const resetNew = () => {
    selectedCase.current = null;
    ++selectionVersion.current;
    ++historyVersion.current;
    setCaseLoading(false);
    setHistoryLoading(false);
    setHistoryError(null);
    setSavedCase(null);
    setHistoryMethod("");
    setHistoryPage(1);
    setSelectedCaseId(null);
    setTitle("");
    setMethods([]);
    setCriteria([]);
    setAlternatives([]);
    setWeights([]);
    setTypes([]);
    setMatrix([]);
    setAhpMatrix([]);
    setIsmMatrix([]);
    setIssues([]);
    setSelectedRun(null);
    setLatestSawRanking([]);
    setLatestTopsisRanking([]);
    setLatestAhpResult(null);
  };

  type SaveVariables = { body: Parameters<typeof patchDecisionCase>[2]; id: string | null; version: number; release: () => void };
  const saveMutation = useMutation({
    mutationFn: async ({ body, id, release }: SaveVariables) => {
      try {
        const value = id ? await patchDecisionCase(projectId, id, body) : await createDecisionCase(projectId, body as Parameters<typeof createDecisionCase>[1]);
        if (!isSavedCase(value,id ?? undefined)) throw new DecisionSupportRequestError("Invalid saved case response",null);
        return value;
      } finally { release(); }
    },
    onSuccess: (data, variables) => {
      void qc.invalidateQueries({ queryKey: ["decision-cases", projectId] });
      if (variables.version !== selectionVersion.current) return;
      selectedCase.current = data.id;
      setSavedCase(data); setIssues([]); setSelectedCaseId(data.id);
    },
    onError: (err: unknown, variables) => {
      if (variables.version !== selectionVersion.current) return;
      setLatestSawRanking([]);setLatestTopsisRanking([]);setLatestAhpResult(null);
      setIssues(parseApiRequestIssues(err instanceof DecisionSupportRequestError ? err.payload : null));
    },
  });
  const saveDraft = () => {
    const release = beginOperation(); if (!release) return;
    const body = structuredClone({ title, selected_methods: methods, criteria, alternatives, weights, types, performance_matrix: matrix, ahp_matrix: ahpMatrix, ...(methods.includes("ism") ? {ism_matrix:ismMatrix} : {}) });
    const changes = selectedCaseId ? Object.fromEntries(Object.entries(body).filter(([key, value]) =>
      JSON.stringify(value) !== JSON.stringify(savedCase?.[key as keyof DecisionCase]))) : body;
    saveMutation.mutate({ body: changes, id: selectedCaseId, version: selectionVersion.current, release });
  };

  const selectHistoricalRun = (runId: string) => {
    const caseId=selectedCase.current;
    if(!caseId||!canView)return;
    const version=selectionVersion.current,requestVersion=++historyVersion.current;
    setSelectedRun(null);setHistoryError(null);setHistoryLoading(true);
    const owned=()=>version===selectionVersion.current&&requestVersion===historyVersion.current&&selectedCase.current===caseId;
    void getDecisionRun(projectId,caseId,runId).then(run=>{if(owned()&&run.id===runId)setSelectedRun(run);})
    .catch(()=>{if(owned())setHistoryError(runId);})
    .finally(()=>{if(owned())setHistoryLoading(false);});
  };

  const toggleMethod = (m: DecisionMethod) => {
    if (m === "ism" && !methods.includes("ism")) setIsmMatrix((current: unknown) => hydrateIsmMatrix(current,criteria.length));
    setMethods((prev) => (prev.includes(m) ? prev.filter((x) => x !== m) : [...prev, m]));
  };

  if (isLoading) return <LoadingSkeleton rows={6} />;
  if (!project) return <NotFoundState title={t("common.projectNotFound")} />;

  if (casesQuery.isError) {
    return <QueryErrorState onRetry={() => void casesQuery.refetch()} />;
  }

  const caseRows = casesQuery.data?.results ?? [];
  const runRows = runsQuery.data?.results ?? [];

  return (
    <>
      <PageHeader title={t("decisionSupport.title")} subtitle={t("decisionSupport.subtitle")} />

      <div className="mt-6 grid gap-8 lg:grid-cols-[240px_1fr]">
        <aside className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-medium">{t("decisionSupport.cases")}</h2>
            <Button type="button" size="sm" variant="outline" disabled={!canEdit || operationBusy} onClick={resetNew}>
              {t("decisionSupport.createCase")}
            </Button>
          </div>
          {casesQuery.isLoading ? (
            <LoadingSkeleton rows={3} />
          ) : caseRows.length === 0 ? (
            <EmptyState title={t("decisionSupport.casesEmpty")} />
          ) : (
            <ul className="divide-y divide-border rounded-md border border-border">
              {caseRows.map((c) => (
                <li key={c.id}>
                  <button
                    type="button"
                    className={`w-full px-3 py-2 text-start text-sm hover:bg-muted/40 ${
                      selectedCaseId === c.id ? "bg-muted/60" : ""
                    }`}
                    onClick={() => hydrateFromCase(c.id)}
                  >
                    {c.title}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </aside>

        <section className="min-w-0 space-y-6">
          <div className="space-y-2">
            <Label htmlFor="ds-title">{t("decisionSupport.caseTitle")}</Label>
            <Input
              id="ds-title"
              disabled={!canEdit || operationBusy || caseLoading}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder={t("decisionSupport.caseTitlePlaceholder")}
            />
          </div>

          <fieldset className="space-y-2">
            <legend className="text-sm font-medium">{t("decisionSupport.methods")}</legend>
            <div className="flex flex-wrap gap-3">
              {DECISION_METHODS.map((m) => (
                <label key={m} className="flex items-center gap-2 text-sm">
                  <Checkbox
                    disabled={!canEdit || operationBusy || caseLoading}
                    checked={methods.includes(m)}
                    onCheckedChange={() => toggleMethod(m)}
                  />
                  <span className="uppercase">{m}</span>
                </label>
              ))}
            </div>
            <p className="text-xs text-muted-foreground">{t("decisionSupport.methodsHint")}</p>
          </fieldset>

          <NamedListEditor
            label={t("decisionSupport.criteria")}
            editable
            disabled={!canEdit || operationBusy || caseLoading}
            values={criteria}
            onChange={(next, operation) => {
              if (operation) setIsmMatrix(remapIsmMatrix(ismMatrix,next.length,operation));
              setAhpMatrix(reconcilePairwiseMatrix(criteria, next, ahpMatrix));
              setCriteria(next);
              if (methods.some(method => method === "saw" || method === "topsis")) {
                setWeights(alignWeights(next.length, weights));
                setTypes(alignTypes(next.length, types));
              }
            }}
          />
          <NamedListEditor
            disabled={!canEdit || operationBusy || caseLoading}
            label={t("decisionSupport.alternatives")}
            values={alternatives}
            onChange={setAlternatives}
          />

          <ValidationIssueList issues={issues} />

          <Button
            type="button"
            disabled={!canEdit || operationBusy || caseLoading || !title.trim() || saveMutation.isPending}
            onClick={saveDraft}
          >
            {t("decisionSupport.save")}
          </Button>

          {selectedCaseId && methods.includes("saw") ? (
            <SawMethodPanel
              key={projectId + ":" + selectedCaseId + ":saw"}
              disabled={!canEdit || operationBusy || caseLoading}
              beginOperation={beginOperation}
              onHistoryRecovered={showRecoveredHistory}
              projectId={projectId}
              caseId={selectedCaseId}
              criteria={criteria}
              alternatives={alternatives}
              weights={alignWeights(criteria.length, weights)}
              types={alignTypes(criteria.length, types)}
              matrix={matrix}
              onWeightsChange={setWeights}
              onTypesChange={setTypes}
              onMatrixChange={setMatrix}
              latestRanking={latestSawRanking}
            />
          ) : null}

          {selectedCaseId && methods.includes("topsis") ? (
            <TopsisMethodPanel
              key={projectId + ":" + selectedCaseId + ":topsis"}
              disabled={!canEdit || operationBusy || caseLoading}
              beginOperation={beginOperation}
              onHistoryRecovered={showRecoveredHistory}
              projectId={projectId}
              caseId={selectedCaseId}
              criteria={criteria}
              alternatives={alternatives}
              weights={alignWeights(criteria.length, weights)}
              types={alignTypes(criteria.length, types)}
              matrix={matrix}
              onWeightsChange={setWeights}
              onTypesChange={setTypes}
              onMatrixChange={setMatrix}
              latestRanking={latestTopsisRanking}
            />
          ) : null}

          {selectedCaseId && methods.includes("ahp") ? (
            <AhpMethodPanel
              disabled={!canEdit || operationBusy || caseLoading}
              beginOperation={beginOperation}
              onHistoryRecovered={showRecoveredHistory}
              key={projectId + ":" + selectedCaseId + ":ahp"}
              savedCriteria={savedCase?.criteria ?? []}
              onSavedCriteria={(next) => setSavedCase(current => current ? { ...current, criteria: next } : current)}
              onResult={setLatestAhpResult}
              projectId={projectId}
              caseId={selectedCaseId}
              criteria={criteria}
              matrix={ahpMatrix}
              onMatrixChange={setAhpMatrix}
              latestResult={latestAhpResult}
            />
          ) : null}

          {selectedCaseId && methods.includes("ism") && !caseLoading ? (
            <IsmMethodPanel key={projectId+":"+selectedCaseId+":ism"} projectId={projectId} caseId={selectedCaseId}
              criteria={criteria} matrix={ismMatrix} onMatrixChange={setIsmMatrix} savedCriteria={savedCase?.criteria ?? []}
              onSavedCase={setSavedCase} onHistoryRecovered={showRecoveredHistory}
              disabled={!canEdit || operationBusy} beginOperation={beginOperation}/>
          ) : null}

          {selectedCaseId && canView ? (
            <div className="space-y-3">
              <h2 className="text-sm font-medium">{t("decisionSupport.history")}</h2>
              <label className="flex items-center gap-2">
                {t("decisionSupport.historyMethod")}
                <select aria-label={t("decisionSupport.historyMethod")} value={historyMethod}
                  className="rounded border border-border bg-background p-1"
                  onChange={event => {
                    navigateHistory(event.target.value as DecisionMethod | "",1);
                  }}>
                  <option value="">{t("decisionSupport.historyAllMethods")}</option>
                  {DECISION_METHODS.map(method => <option key={method} value={method}>{method.toUpperCase()}</option>)}
                </select>
              </label>
              {runsQuery.isError ? <><QueryErrorState onRetry={() => void runsQuery.refetch()} />{historyPage>1&&<Button onClick={()=>navigateHistory(historyMethod,1)}>{t("decisionSupport.historyFirstPage")}</Button>}</>
                : runsQuery.isLoading ? <LoadingSkeleton rows={2} />
                : <ExecutionHistoryList filtered={!!historyMethod} runs={runRows} onSelect={selectHistoricalRun} />}
              <div className="flex items-center gap-2">
                <Button type="button" variant="outline" disabled={!runsQuery.data?.previous || runsQuery.isFetching}
                  onClick={() => navigateHistory(historyMethod,historyPage-1)}>{t("decisionSupport.historyPrevious")}</Button>
                <span>{t("decisionSupport.historyPage", { page: historyPage, count: runsQuery.data?.count ?? 0 })}</span>
                <Button type="button" variant="outline" disabled={!runsQuery.data?.next || runsQuery.isFetching}
                  onClick={() => navigateHistory(historyMethod,historyPage+1)}>{t("decisionSupport.historyNext")}</Button>
              </div>
              {historyLoading && <p role="status">{t("decisionSupport.historyLoading")}</p>}
              {historyError&&<div role="alert"><p>{t("decisionSupport.historyReadError")}</p><Button onClick={()=>selectHistoricalRun(historyError)}>{t("common.retry")}</Button></div>}
              <InputSnapshotViewer run={selectedRun} />
            </div>
          ) : null}
        </section>
      </div>
    </>
  );
}

export default function ProjectDecisionSupportPage() {
  const { t } = useTranslation();
  const { projectId = "" } = useParams();
  return (
    <main className="page-main page-shell mx-auto px-4 py-8">
      <ProjectProvider projectId={projectId}>
        <Breadcrumb
          items={[
            { label: t("nav.projects"), href: `/${PATHS.PROJECT}` },
            { label: t("nav.projectDecisionSupport") },
          ]}
        />
        <DecisionSupportContent key={projectId} />
      </ProjectProvider>
    </main>
  );
}
