import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router";
import { ProjectProvider, useProject } from "@/app/contexts/project-context";
import {
  DECISION_METHODS,
  type CriterionType,
  type DecisionMethod,
  DecisionSupportRequestError,
  createDecisionCase,
  getDecisionCase,
  getDecisionRun,
  listDecisionCases,
  listDecisionRuns,
  patchDecisionCase,
  type DecisionRun,
  type SawRankingRow,
} from "@/app/lib/api/decision-support";
import { PATHS } from "@/app/routeVars";
import { ExecutionHistoryList } from "@/components/decision-support/ExecutionHistoryList";
import { InputSnapshotViewer } from "@/components/decision-support/InputSnapshotViewer";
import { NamedListEditor } from "@/components/decision-support/NamedListEditor";
import { SawMethodPanel } from "@/components/decision-support/SawMethodPanel";
import { ValidationIssueList } from "@/components/decision-support/ValidationIssueList";
import { parseApiValidationIssues } from "@/components/decision-support/validation-issues";
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
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [methods, setMethods] = useState<DecisionMethod[]>([]);
  const [criteria, setCriteria] = useState<string[]>([]);
  const [alternatives, setAlternatives] = useState<string[]>([]);
  const [weights, setWeights] = useState<number[]>([]);
  const [types, setTypes] = useState<CriterionType[]>([]);
  const [matrix, setMatrix] = useState<(number | null)[][]>([]);
  const [issues, setIssues] = useState(parseApiValidationIssues(null));
  const [selectedRun, setSelectedRun] = useState<DecisionRun | null>(null);
  const [latestRanking, setLatestRanking] = useState<SawRankingRow[]>([]);

  const casesQuery = useQuery({
    queryKey: ["decision-cases", projectId],
    queryFn: () => listDecisionCases(projectId),
    enabled: !!projectId,
  });

  const runsQuery = useQuery({
    queryKey: ["decision-runs", projectId, selectedCaseId],
    queryFn: () => listDecisionRuns(projectId, selectedCaseId!),
    enabled: !!projectId && !!selectedCaseId,
  });

  const hydrateFromCase = (caseId: string) => {
    setSelectedCaseId(caseId);
    setSelectedRun(null);
    setIssues([]);
    setLatestRanking([]);
    void getDecisionCase(projectId, caseId).then((c) => {
      setTitle(c.title);
      setMethods([...(c.selected_methods ?? [])]);
      const crit = [...(c.criteria ?? [])];
      const alts = [...(c.alternatives ?? [])];
      setCriteria(crit);
      setAlternatives(alts);
      setWeights(alignWeights(crit.length, (c.weights ?? []).map(Number)));
      setTypes(
        alignTypes(
          crit.length,
          (c.types ?? []).map((x) => (x === "cost" ? "cost" : "benefit")),
        ),
      );
      setMatrix([...(c.performance_matrix ?? [])]);
    });
  };

  const resetNew = () => {
    setSelectedCaseId(null);
    setTitle("");
    setMethods([]);
    setCriteria([]);
    setAlternatives([]);
    setWeights([]);
    setTypes([]);
    setMatrix([]);
    setIssues([]);
    setSelectedRun(null);
    setLatestRanking([]);
  };

  const saveMutation = useMutation({
    mutationFn: async () => {
      const n = criteria.length;
      const body = {
        title,
        selected_methods: methods,
        criteria,
        alternatives,
        weights: alignWeights(n, weights),
        types: alignTypes(n, types),
        performance_matrix: matrix,
      };
      if (selectedCaseId) {
        return patchDecisionCase(projectId, selectedCaseId, body);
      }
      return createDecisionCase(projectId, { ...body, title });
    },
    onSuccess: (data) => {
      setIssues([]);
      setSelectedCaseId(data.id);
      void qc.invalidateQueries({ queryKey: ["decision-cases", projectId] });
      void qc.invalidateQueries({ queryKey: ["decision-case", projectId, data.id] });
    },
    onError: (err: unknown) => {
      if (err instanceof DecisionSupportRequestError) {
        setIssues(parseApiValidationIssues(err.payload));
      } else {
        setIssues([{ code: "error", path: "", message: String(err) }]);
      }
    },
  });

  const toggleMethod = (m: DecisionMethod) => {
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
            <Button type="button" size="sm" variant="outline" onClick={resetNew}>
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

        <section className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="ds-title">{t("decisionSupport.caseTitle")}</Label>
            <Input
              id="ds-title"
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
            values={criteria}
            onChange={(next) => {
              setCriteria(next);
              setWeights(alignWeights(next.length, weights));
              setTypes(alignTypes(next.length, types));
            }}
          />
          <NamedListEditor
            label={t("decisionSupport.alternatives")}
            values={alternatives}
            onChange={setAlternatives}
          />

          <ValidationIssueList issues={issues} />

          <Button
            type="button"
            disabled={!title.trim() || saveMutation.isPending}
            onClick={() => saveMutation.mutate()}
          >
            {t("decisionSupport.save")}
          </Button>

          {selectedCaseId && methods.includes("saw") ? (
            <SawMethodPanel
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
              latestRanking={latestRanking}
            />
          ) : null}

          {selectedCaseId ? (
            <div className="space-y-3">
              <h2 className="text-sm font-medium">{t("decisionSupport.history")}</h2>
              <ExecutionHistoryList
                runs={runRows}
                onSelect={(runId) => {
                  void getDecisionRun(projectId, selectedCaseId, runId).then((run) => {
                    setSelectedRun(run);
                    if (run.method === "saw" && run.result?.ranking) {
                      setLatestRanking(run.result.ranking);
                    }
                  });
                }}
              />
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
        <DecisionSupportContent />
      </ProjectProvider>
    </main>
  );
}
