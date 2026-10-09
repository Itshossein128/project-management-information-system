import { apiJson } from "@/app/lib/api-client";
import { PATHS } from "@/app/routeVars";

const projectBase = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export interface PortfolioSummary {
  projects: Array<{
    project_id: string;
    project_code: string;
    project_name: string;
    currency: string;
    total_budget: number;
    total_commitment: number;
    total_actual: number;
  }>;
  totals_by_currency: Record<
    string,
    {
      total_budget: number;
      total_commitment: number;
      total_actual: number;
      project_count: number;
    }
  >;
  totals: { project_count: number; note?: string };
}

export function fetchPortfolioSummary() {
  return apiJson<PortfolioSummary>(`/v1/portfolio/summary/`);
}

export interface OrganizationUnit {
  id: string;
  code: string;
  name: string;
  parent?: string | null;
  status: string;
}

export function fetchOrganizationUnits() {
  return apiJson<OrganizationUnit[] | { results: OrganizationUnit[] }>(
    `/v1/organization-units/`,
  );
}

export function createOrganizationUnit(body: {
  code: string;
  name: string;
  parent?: string | null;
  status?: string;
}) {
  return apiJson<OrganizationUnit>(`/v1/organization-units/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export interface ManagedContractType {
  id: string;
  code: string;
  name_fa: string;
  name_en: string;
  is_active: boolean;
}

export function fetchContractTypes() {
  return apiJson<ManagedContractType[] | { results: ManagedContractType[] }>(
    `/v1/contract-types/`,
  );
}

export function createContractType(body: {
  code: string;
  name_fa: string;
  name_en?: string;
  is_active?: boolean;
}) {
  return apiJson<ManagedContractType>(`/v1/contract-types/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export interface IPCCollectionList {
  results: Array<{
    id: string;
    amount: string;
    collected_at: string;
    currency: string;
    reference: string;
  }>;
  collections_total: string;
  remaining_receivable: string;
  gross_amount: string;
  net_amount: string | null;
}

export function fetchIPCCollections(projectId: string, ipcId: string) {
  return apiJson<IPCCollectionList>(
    `${projectBase(projectId)}/ipcs/${ipcId}/collections/`,
  );
}

export function addIPCCollection(
  projectId: string,
  ipcId: string,
  body: { amount: string; collected_at: string; currency?: string; reference?: string },
) {
  return apiJson(`${projectBase(projectId)}/ipcs/${ipcId}/collections/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export interface CBSNode {
  id: string;
  cbs_code: string;
  cbs_name: string;
  cost_type: string;
  depth: number;
}

export function fetchCBS(projectId: string) {
  return apiJson<CBSNode[]>(`${projectBase(projectId)}/cbs/`);
}

export function createCBSNode(
  projectId: string,
  body: { cbs_code: string; cbs_name: string; cost_type?: string; parent_id?: string },
) {
  return apiJson<CBSNode>(`${projectBase(projectId)}/cbs/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export interface CommitmentRow {
  id: string;
  commitment_number: string;
  amount: string;
  remaining: number;
  status: string;
  counterparty: string;
  payment_terms?: string;
  contract?: string | null;
  requisition?: string | null;
}

export function fetchCommitments(projectId: string) {
  return apiJson<CommitmentRow[] | { results: CommitmentRow[] }>(
    `${projectBase(projectId)}/commitments/`,
  );
}

export function createCommitment(
  projectId: string,
  body: Record<string, unknown>,
) {
  return apiJson<CommitmentRow>(`${projectBase(projectId)}/commitments/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export interface PaymentRow {
  id: string;
  commitment: string | null;
  actual_cost: string | null;
  amount: string;
  paid_at: string;
  document_ref: string;
  status: string;
  duplicate_exception_reason?: string;
}

export function fetchPayments(projectId: string) {
  return apiJson<PaymentRow[]>(`${projectBase(projectId)}/payments/`);
}

export function createPayment(
  projectId: string,
  body: Record<string, unknown>,
) {
  return apiJson<PaymentRow>(`${projectBase(projectId)}/payments/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export interface LedgerRow {
  row_type: "commitment" | "actual" | "payment";
  id: string;
  amount: number;
  document_ref: string;
  status: string;
  commitment_id?: string | null;
}

export function fetchLedgerReport(projectId: string) {
  return apiJson<{ rows: LedgerRow[] }>(
    `${projectBase(projectId)}/costs/ledger-report/`,
  );
}

export function createCommitmentFromRequisition(
  projectId: string,
  requisitionId: string,
  body: Record<string, unknown>,
) {
  return apiJson<CommitmentRow>(
    `${projectBase(projectId)}/requisitions/${requisitionId}/create-commitment/`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

export interface StakeholderRow {
  id: string;
  name: string;
  organization_name: string;
  role: string;
  email: string | null;
  phone: string | null;
  influence: number | null;
  interest: number | null;
  communication_need: string;
  relationship_owner: string | null;
  status: string;
  contacts_redacted?: boolean;
}

export interface StakeholderMatrixCell {
  influence: number;
  interest: number;
  stakeholders: Array<{ id: string; name: string }>;
}

export interface CommunicationPlanRow {
  id: string;
  audience: string;
  message: string;
  channel_type: string;
  frequency: string;
  owner: string | null;
  stakeholder: string | null;
  status: string;
  created_at: string;
}

export function fetchStakeholders(projectId: string) {
  return apiJson<StakeholderRow[] | { results: StakeholderRow[] }>(
    `${projectBase(projectId)}/stakeholders/`,
  );
}

export function fetchStakeholderMatrix(projectId: string) {
  return apiJson<{ cells: StakeholderMatrixCell[] }>(
    `${projectBase(projectId)}/stakeholders/matrix/`,
  );
}

export function createStakeholder(
  projectId: string,
  body: Record<string, unknown>,
) {
  return apiJson<StakeholderRow>(`${projectBase(projectId)}/stakeholders/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function fetchCommunicationPlans(projectId: string) {
  return apiJson<{ results: CommunicationPlanRow[] }>(
    `${projectBase(projectId)}/communication-plans/`,
  );
}

export function createCommunicationPlan(
  projectId: string,
  body: {
    audience: string;
    message: string;
    frequency: string;
    channel_type?: string;
    owner?: string | null;
    stakeholder?: string | null;
    status?: string;
  },
) {
  return apiJson<CommunicationPlanRow>(
    `${projectBase(projectId)}/communication-plans/`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}

export function updateCommunicationPlan(
  projectId: string,
  planId: string,
  body: Partial<CommunicationPlanRow>,
) {
  return apiJson<CommunicationPlanRow>(
    `${projectBase(projectId)}/communication-plans/${planId}/`,
    {
      method: "PATCH",
      body: JSON.stringify(body),
    },
  );
}

export function deleteCommunicationPlan(projectId: string, planId: string) {
  return apiJson<void>(
    `${projectBase(projectId)}/communication-plans/${planId}/`,
    { method: "DELETE" },
  );
}

export function asList<T>(data: T[] | { results: T[] }): T[] {
  return Array.isArray(data) ? data : (data.results ?? []);
}
