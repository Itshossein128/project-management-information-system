import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router";
import { useAuth } from "@/app/contexts/auth-context";
import {
  ProjectProvider,
  usePermission,
  useProject,
} from "@/app/contexts/project-context";
import {
  activateWorkflowDefinition,
  approveWorkflowInstance,
  createDecision,
  createWorkflowDefinition,
  fetchDecisions,
  fetchWorkflowDefinitions,
  fetchWorkflowInstanceLog,
  fetchWorkflowInstances,
  rejectWorkflowInstance,
  startWorkflowInstance,
} from "@/app/lib/api/workflow";
import { PATHS } from "@/app/routeVars";
import { Input, Label } from "@/components/form";
import { AccessDenied, EmptyState, NotFoundState } from "@/components/layout/empty-state";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

function DecisionsWorkflowContent() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_project") || has("view_documents");
  const canEdit = has("edit_project");
  const toast = useToast();
  const qc = useQueryClient();

  const [decisionSubject, setDecisionSubject] = useState("");
  const [decisionRationale, setDecisionRationale] = useState("");
  const [executionOwner, setExecutionOwner] = useState(user?.id ?? "");
  const [defName, setDefName] = useState("");
  const [selectedInstanceId, setSelectedInstanceId] = useState<string | null>(null);
  const [actionComment, setActionComment] = useState("");

  const { data: decisions, isLoading: dLoading } = useQuery({
    queryKey: ["decisions", projectId],
    queryFn: () => fetchDecisions(projectId),
    enabled: canView && Boolean(projectId),
  });

  const { data: definitions, isLoading: defLoading } = useQuery({
    queryKey: ["workflow-definitions", projectId],
    queryFn: () => fetchWorkflowDefinitions(projectId),
    enabled: canView && Boolean(projectId),
  });

  const { data: instances, isLoading: instLoading } = useQuery({
    queryKey: ["workflow-instances", projectId],
    queryFn: () => fetchWorkflowInstances(projectId),
    enabled: canView && Boolean(projectId),
  });

  const { data: logData, isLoading: logLoading } = useQuery({
    queryKey: ["workflow-log", projectId, selectedInstanceId],
    queryFn: () => fetchWorkflowInstanceLog(projectId, selectedInstanceId!),
    enabled: Boolean(selectedInstanceId) && canView,
  });

  const createDecisionMut = useMutation({
    mutationFn: () =>
      createDecision(projectId, {
        subject: decisionSubject,
        rationale: decisionRationale,
        execution_owner: executionOwner,
        proposer: user?.id,
        approver_ids: user?.id ? [user.id] : [],
        options: "",
        criteria: "",
      }),
    onSuccess: () => {
      toast.success(t("workflow.decisionCreated", "Decision recorded"));
      setDecisionSubject("");
      setDecisionRationale("");
      void qc.invalidateQueries({ queryKey: ["decisions", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const createDefMut = useMutation({
    mutationFn: () => {
      const approver = user?.id;
      if (!approver) throw new Error(t("workflow.noCurrentUser", "Sign in to create workflows"));
      return createWorkflowDefinition(projectId, {
        name: defName || t("workflow.defaultDefName", "Budget change approval"),
        workflow_type: "budget_change",
        description: "",
        stages: [
          {
            order: 1,
            name: t("workflow.stageOne", "Stage 1 review"),
            approver_user: approver,
            approval_mode: "any",
            on_reject: "stop",
            deadline_days: 3,
          },
          {
            order: 2,
            name: t("workflow.stageTwo", "Stage 2 approve"),
            approver_user: approver,
            approval_mode: "any",
            on_reject: "stop",
            deadline_days: 5,
          },
        ],
      });
    },
    onSuccess: () => {
      toast.success(t("workflow.definitionCreated", "Workflow definition created"));
      setDefName("");
      void qc.invalidateQueries({ queryKey: ["workflow-definitions", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const activateMut = useMutation({
    mutationFn: (defId: string) => activateWorkflowDefinition(projectId, defId),
    onSuccess: () => {
      toast.success(t("workflow.definitionActivated", "Definition activated"));
      void qc.invalidateQueries({ queryKey: ["workflow-definitions", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const startMut = useMutation({
    mutationFn: (defId: string) =>
      startWorkflowInstance(projectId, {
        definition: defId,
        subject_type: "budget_change",
        subject_id: crypto.randomUUID(),
        comment: "",
      }),
    onSuccess: (inst) => {
      toast.success(t("workflow.instanceStarted", "Workflow started"));
      setSelectedInstanceId(inst.id);
      void qc.invalidateQueries({ queryKey: ["workflow-instances", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const approveMut = useMutation({
    mutationFn: (instanceId: string) =>
      approveWorkflowInstance(projectId, instanceId, actionComment),
    onSuccess: (_, instanceId) => {
      toast.success(t("common.approve", "Approve"));
      setSelectedInstanceId(instanceId);
      void qc.invalidateQueries({ queryKey: ["workflow-instances", projectId] });
      void qc.invalidateQueries({ queryKey: ["workflow-log", projectId, instanceId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const rejectMut = useMutation({
    mutationFn: (instanceId: string) =>
      rejectWorkflowInstance(projectId, instanceId, actionComment),
    onSuccess: (_, instanceId) => {
      toast.success(t("common.reject", "Reject"));
      setSelectedInstanceId(instanceId);
      void qc.invalidateQueries({ queryKey: ["workflow-instances", projectId] });
      void qc.invalidateQueries({ queryKey: ["workflow-log", projectId, instanceId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (isLoading || dLoading || defLoading || instLoading) {
    return <LoadingSkeleton rows={10} />;
  }
  if (!project) return <NotFoundState title={t("common.projectNotFound")} />;
  if (!canView) return <AccessDenied />;

  const decisionRows = decisions?.results ?? [];
  const definitionRows = definitions?.results ?? [];
  const instanceRows = instances?.results ?? [];
  const logRows = logData?.results ?? [];
  const activeDefs = definitionRows.filter((d) => d.status === "active");

  return (
    <div className="space-y-8">
      <PageHeader
        title={t("workflow.title", "Decisions & workflow")}
        subtitle={project.project_name}
      />

      <section className="space-y-3">
        <h2 className="text-sm font-medium">{t("workflow.decisions", "Management decisions")}</h2>
        <ul className="divide-y rounded border text-sm">
          {decisionRows.map((d) => (
            <li key={d.id} className="space-y-1 px-3 py-2">
              <p className="font-medium">{d.subject}</p>
              <p className="text-muted-foreground">{d.rationale}</p>
              <p className="text-xs text-muted-foreground">
                {t("workflow.executionOwner", "Execution owner")}: {d.execution_owner}
              </p>
            </li>
          ))}
          {decisionRows.length === 0 ? (
            <li className="px-3 py-4 text-muted-foreground">
              {t("workflow.noDecisions", "No decisions yet.")}
            </li>
          ) : null}
        </ul>
        {canEdit ? (
          <div className="grid max-w-xl gap-2">
            <Label>{t("workflow.decisionSubject", "Subject")}</Label>
            <Input value={decisionSubject} onChange={(e) => setDecisionSubject(e.target.value)} />
            <Label>{t("workflow.rationale", "Rationale")}</Label>
            <Input
              value={decisionRationale}
              onChange={(e) => setDecisionRationale(e.target.value)}
            />
            <Label>{t("workflow.executionOwnerId", "Execution owner (user ID)")}</Label>
            <Input value={executionOwner} onChange={(e) => setExecutionOwner(e.target.value)} />
            <Button
              variant="primary"
              loading={createDecisionMut.isPending}
              disabled={!decisionSubject || !decisionRationale.trim() || !executionOwner}
              onClick={() => createDecisionMut.mutate()}
            >
              {t("workflow.recordDecision", "Record decision")}
            </Button>
          </div>
        ) : null}
      </section>

      <section className="space-y-3">
        <h2 className="text-sm font-medium">{t("workflow.definitions", "Workflow definitions")}</h2>
        {definitionRows.length === 0 ? (
          <EmptyState title={t("workflow.noDefinitions", "No workflow definitions")} />
        ) : (
          <ul className="divide-y rounded border text-sm">
            {definitionRows.map((def) => (
              <li key={def.id} className="flex flex-wrap items-center gap-2 px-3 py-2">
                <span className="font-medium">{def.name}</span>
                <span className="text-xs text-muted-foreground">{def.workflow_type}</span>
                <span className="rounded bg-muted px-2 py-0.5 text-xs">{def.status}</span>
                {canEdit && def.status !== "active" ? (
                  <Button
                    size="sm"
                    variant="ghost"
                    loading={activateMut.isPending}
                    onClick={() => activateMut.mutate(def.id)}
                  >
                    {t("workflow.activate", "Activate")}
                  </Button>
                ) : null}
                {canEdit && def.status === "active" ? (
                  <Button
                    size="sm"
                    variant="ghost"
                    loading={startMut.isPending}
                    onClick={() => startMut.mutate(def.id)}
                  >
                    {t("workflow.startInstance", "Start instance")}
                  </Button>
                ) : null}
              </li>
            ))}
          </ul>
        )}
        {canEdit ? (
          <div className="grid max-w-xl gap-2">
            <Label>{t("workflow.definitionName", "Definition name")}</Label>
            <Input
              value={defName}
              onChange={(e) => setDefName(e.target.value)}
              placeholder={t("workflow.defaultDefName", "Budget change approval")}
            />
            <Button
              variant="primary"
              loading={createDefMut.isPending}
              disabled={!user?.id}
              onClick={() => createDefMut.mutate()}
            >
              {t("workflow.createBudgetChangeDef", "Create budget_change definition (2 stages)")}
            </Button>
          </div>
        ) : null}
      </section>

      <section className="space-y-3">
        <h2 className="text-sm font-medium">{t("workflow.instances", "Workflow instances")}</h2>
        <ul className="divide-y rounded border text-sm">
          {instanceRows.map((inst) => (
            <li key={inst.id} className="space-y-2 px-3 py-2">
              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  className="text-start font-medium underline-offset-2 hover:underline"
                  onClick={() => setSelectedInstanceId(inst.id)}
                >
                  {inst.id.slice(0, 8)}…
                </button>
                <span className="rounded bg-muted px-2 py-0.5 text-xs">{inst.status}</span>
                <span className="text-xs text-muted-foreground">
                  {inst.subject_type} · stage {inst.current_stage_order ?? "—"}
                </span>
              </div>
              {canEdit && inst.status === "in_progress" ? (
                <div className="flex flex-wrap gap-2">
                  <Input
                    className="max-w-xs"
                    placeholder={t("workflow.commentOptional", "Comment (optional)")}
                    value={selectedInstanceId === inst.id ? actionComment : ""}
                    onChange={(e) => {
                      setSelectedInstanceId(inst.id);
                      setActionComment(e.target.value);
                    }}
                  />
                  <Button
                    size="sm"
                    loading={approveMut.isPending}
                    onClick={() => approveMut.mutate(inst.id)}
                  >
                    {t("common.approve", "Approve")}
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    loading={rejectMut.isPending}
                    onClick={() => rejectMut.mutate(inst.id)}
                  >
                    {t("common.reject", "Reject")}
                  </Button>
                </div>
              ) : null}
            </li>
          ))}
          {instanceRows.length === 0 ? (
            <li className="px-3 py-4 text-muted-foreground">
              {t("workflow.noInstances", "No instances yet.")}
              {activeDefs.length === 0 && canEdit
                ? ` ${t("workflow.activateFirst", "Activate a definition first.")}`
                : null}
            </li>
          ) : null}
        </ul>
      </section>

      {selectedInstanceId ? (
        <section className="space-y-2">
          <h2 className="text-sm font-medium">{t("workflow.actionLog", "Action log")}</h2>
          {logLoading ? (
            <LoadingSkeleton rows={3} />
          ) : (
            <ul className="divide-y rounded border text-sm">
              {logRows.map((entry, idx) => (
                <li key={`${entry.acted_at}-${idx}`} className="px-3 py-2">
                  <span className="font-medium">{entry.action}</span>
                  <span className="text-muted-foreground">
                    {" "}
                    {entry.from_status} → {entry.to_status}
                  </span>
                  {entry.comment ? (
                    <p className="text-xs text-muted-foreground">{entry.comment}</p>
                  ) : null}
                </li>
              ))}
              {logRows.length === 0 ? (
                <li className="px-3 py-4 text-muted-foreground">{t("workflow.emptyLog", "No log entries.")}</li>
              ) : null}
            </ul>
          )}
        </section>
      ) : null}
    </div>
  );
}

export default function ProjectDecisionsWorkflowPage() {
  const { t } = useTranslation();
  const { projectId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto px-4 py-8">
        <Breadcrumb
          items={[
            { label: t("project.title"), href: `/${PATHS.PROJECT}` },
            { label: t("workflow.title", "Decisions & workflow") },
          ]}
        />
        <DecisionsWorkflowContent />
      </main>
    </ProjectProvider>
  );
}
