import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export interface ManagementDecisionRow {
  id: string;
  subject: string;
  options: string;
  criteria: string;
  proposer: string | null;
  final_decision: string;
  execution_owner: string;
  due_date: string | null;
  rationale: string;
  execution_status: string;
  workflow_instance: string | null;
  created_at: string;
}

export interface WorkflowStageRow {
  order: number;
  name: string;
  approver_user: string | null;
  approver_role?: string;
  approval_mode?: string;
  on_reject?: string;
  deadline_days?: number | null;
}

export interface WorkflowDefinitionRow {
  id: string;
  name: string;
  workflow_type: string;
  status: string;
  description: string;
  stages?: WorkflowStageRow[];
  created_at: string;
}

export interface WorkflowInstanceRow {
  id: string;
  definition: string;
  subject_type: string;
  subject_id: string;
  status: string;
  current_stage_order: number | null;
  current_due_at: string | null;
  started_at: string | null;
  completed_at: string | null;
}

export interface WorkflowActionLogRow {
  actor: string;
  acted_at: string;
  action: string;
  from_status: string;
  to_status: string;
  stage_order: number | null;
  comment: string;
}

export function fetchDecisions(projectId: string) {
  return apiJson<{ results: ManagementDecisionRow[] }>(
    `${base(projectId)}/decisions/`,
  );
}

export function createDecision(
  projectId: string,
  body: {
    subject: string;
    rationale: string;
    execution_owner: string;
    options?: string;
    criteria?: string;
    proposer?: string;
    approver_ids?: string[];
  },
) {
  return apiJson<ManagementDecisionRow>(`${base(projectId)}/decisions/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function fetchWorkflowDefinitions(projectId: string) {
  return apiJson<{ results: WorkflowDefinitionRow[] }>(
    `${base(projectId)}/workflows/definitions/`,
  );
}

export function createWorkflowDefinition(
  projectId: string,
  body: {
    name: string;
    workflow_type: string;
    description?: string;
    stages: WorkflowStageRow[];
  },
) {
  return apiJson<WorkflowDefinitionRow>(
    `${base(projectId)}/workflows/definitions/`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

export function activateWorkflowDefinition(projectId: string, definitionId: string) {
  return apiJson<WorkflowDefinitionRow>(
    `${base(projectId)}/workflows/definitions/${definitionId}/activate/`,
    { method: "POST", body: JSON.stringify({}) },
  );
}

export function retireWorkflowDefinition(projectId: string, definitionId: string) {
  return apiJson<WorkflowDefinitionRow>(
    `${base(projectId)}/workflows/definitions/${definitionId}/retire/`,
    { method: "POST", body: JSON.stringify({}) },
  );
}

export function fetchWorkflowInstances(
  projectId: string,
  params: Record<string, string> = {},
) {
  const qs = new URLSearchParams(params).toString();
  return apiJson<{ results: WorkflowInstanceRow[] }>(
    `${base(projectId)}/workflows/instances/${qs ? `?${qs}` : ""}`,
  );
}

export function startWorkflowInstance(
  projectId: string,
  body: {
    definition: string;
    subject_type: string;
    subject_id: string;
    comment?: string;
  },
) {
  return apiJson<WorkflowInstanceRow>(`${base(projectId)}/workflows/instances/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function approveWorkflowInstance(
  projectId: string,
  instanceId: string,
  comment = "",
) {
  return apiJson<WorkflowInstanceRow>(
    `${base(projectId)}/workflows/instances/${instanceId}/approve/`,
    { method: "POST", body: JSON.stringify({ comment }) },
  );
}

export function rejectWorkflowInstance(
  projectId: string,
  instanceId: string,
  comment = "",
) {
  return apiJson<WorkflowInstanceRow>(
    `${base(projectId)}/workflows/instances/${instanceId}/reject/`,
    { method: "POST", body: JSON.stringify({ comment }) },
  );
}

export function cancelWorkflowInstance(
  projectId: string,
  instanceId: string,
  comment = "",
) {
  return apiJson<WorkflowInstanceRow>(
    `${base(projectId)}/workflows/instances/${instanceId}/cancel/`,
    { method: "POST", body: JSON.stringify({ comment }) },
  );
}

export function fetchWorkflowInstanceLog(projectId: string, instanceId: string) {
  return apiJson<{ results: WorkflowActionLogRow[] }>(
    `${base(projectId)}/workflows/instances/${instanceId}/log/`,
  );
}
