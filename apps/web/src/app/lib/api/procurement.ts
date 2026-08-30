import { client } from "./client";

// Types
export type RequisitionScope = 'block' | 'workshop';

export interface Block {
  id: string;
  project: string;
  block_code: string;
  block_name: string;
  wbs: string | null;
  wbs_code?: string | null;
  wbs_name?: string | null;
  budget: string;
  is_active: boolean;
  block_kind?: 'standard' | 'workshop';
  block_kind_display?: string;
  is_system?: boolean;
  created_at: string;
  updated_at: string;
}

export interface BlockPayload {
  block_code: string;
  block_name: string;
  wbs?: string | null;
  budget?: string | number;
  is_active?: boolean;
}

export interface RequisitionItem {
  id: string;
  line_number: number;
  material: string;
  material_name: string;
  material_code: string;
  wbs_node: string | null;
  requested_qty: string;
  approved_qty: string | null;
  purchased_qty: string;
  status: string;
  status_display: string;
  assigned_to: number | null;
  assigned_to_name: string | null;
  notes: string;
}

export type WorkflowStepState = "completed" | "current" | "pending" | "skipped" | "rejected";

export interface PartialApproveDetail {
  item_id: string;
  line_number: number;
  material_code: string;
  requested_qty: string;
  approved_qty: string;
  status: string;
}

export interface WorkflowStepEvent {
  action?: string;
  action_display?: string;
  performed_at?: string;
  performed_by_name?: string;
  details?: PartialApproveDetail[];
}

export interface WorkflowStep {
  code: string;
  label: string;
  required_role: string;
  required_role_label: string;
  state: WorkflowStepState;
  completed_at?: string | null;
  completed_by_name?: string | null;
  events?: WorkflowStepEvent[];
}

export interface NextApprover {
  role: string;
  role_label: string;
}

export interface ApprovalSummary {
  last_action?: {
    at: string;
    by_name: string | null;
    action: string;
    action_display: string;
    step_label: string;
  } | null;
  workflow_progress: string;
  workflow_step_label: string | null;
}

export interface RequisitionHeader {
  id: string;
  project: string;
  scope: RequisitionScope;
  scope_display?: string;
  block: string;
  block_code: string;
  block_name: string;
  requisition_number: string;
  requisition_type: string;
  requisition_type_display: string;
  priority: string;
  priority_display: string;
  urgency: string;
  status: string;
  status_display: string;
  requested_by: number;
  requested_by_name: string;
  request_date: string;
  required_by_date: string | null;
  is_grn_provisional: boolean;
  notes: string;
  items?: RequisitionItem[];
  item_count?: number;
  workflow_timeline?: WorkflowStep[];
  next_approver?: NextApprover | null;
  approval_summary?: ApprovalSummary;
  last_action_at?: string | null;
  last_action_by_name?: string | null;
  last_action_display?: string | null;
  next_approver_role?: string | null;
  next_approver_role_label?: string | null;
  workflow_progress?: string | null;
  workflow_step_label?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApprovalLog {
  id: string;
  requisition: string;
  requisition_number?: string;
  requisition_scope?: RequisitionScope;
  step_from: string;
  step_from_display: string;
  step_to: string;
  step_to_display: string;
  action: string;
  action_display: string;
  performed_by: number;
  performed_by_name: string;
  performed_at: string;
  comments: string;
  details?: PartialApproveDetail[];
}

export interface InventoryAllocation {
  id: string;
  requisition_item: string;
  block: string;
  block_code: string;
  material: string;
  material_name: string;
  mr_tag: string;
  allocated_qty: string;
  received_qty: string;
  issued_qty: string;
  available_qty: number;
  created_at: string;
  updated_at: string;
}

export interface InternalTransfer {
  id: string;
  source_block: string;
  source_block_code: string;
  target_block: string;
  target_block_code: string;
  material: string;
  material_name: string;
  quantity: string;
  reason: string;
  approved_by: number | null;
  approved_at: string | null;
  status: string;
  status_display: string;
  cost_adjustment_notes: string;
  created_at: string;
  updated_at: string;
}

function normalizeList<T>(data: any): T[] {
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.results)) return data.results;
  return [];
}

// Blocks API
export async function fetchBlocks(
  projectId: string,
  options?: { standardOnly?: boolean; includeSystem?: boolean },
): Promise<Block[]> {
  const params: Record<string, string> = {};
  if (options?.includeSystem) {
    params.include_system = 'true';
  } else if (options?.standardOnly !== false) {
    params.exclude_system = 'true';
  }
  const { data } = await client.get<any>(`/v1/projects/${projectId}/blocks/`, { params });
  return normalizeList<Block>(data);
}

export async function createBlock(projectId: string, payload: BlockPayload): Promise<Block> {
  const { data } = await client.post<Block>(`/v1/projects/${projectId}/blocks/`, payload);
  return data;
}

export async function updateBlock(
  projectId: string,
  blockId: string,
  payload: Partial<BlockPayload>,
): Promise<Block> {
  const { data } = await client.patch<Block>(`/v1/projects/${projectId}/blocks/${blockId}/`, payload);
  return data;
}

export async function deleteBlock(projectId: string, blockId: string): Promise<void> {
  await client.delete(`/v1/projects/${projectId}/blocks/${blockId}/`);
}

// Requisitions API
export async function fetchRequisitions(projectId: string, params?: Record<string, any>): Promise<RequisitionHeader[]> {
  const { data } = await client.get<any>(`/v1/projects/${projectId}/requisitions/`, { params });
  return normalizeList<RequisitionHeader>(data);
}

export async function fetchRequisition(projectId: string, reqId: string): Promise<RequisitionHeader> {
  const { data } = await client.get<RequisitionHeader>(`/v1/projects/${projectId}/requisitions/${reqId}/`);
  return data;
}

export async function createRequisition(projectId: string, payload: any): Promise<RequisitionHeader> {
  const { data } = await client.post<RequisitionHeader>(`/v1/projects/${projectId}/requisitions/`, payload);
  return data;
}

// Approval Workflow API
export async function submitRequisition(projectId: string, reqId: string, comments: string = ""): Promise<RequisitionHeader> {
  const { data } = await client.post<RequisitionHeader>(`/v1/projects/${projectId}/requisitions/${reqId}/submit/`, { comments });
  return data;
}

export async function approveRequisition(projectId: string, reqId: string, comments: string = ""): Promise<RequisitionHeader> {
  const { data } = await client.post<RequisitionHeader>(`/v1/projects/${projectId}/requisitions/${reqId}/approve/`, { comments });
  return data;
}

export async function rejectRequisition(projectId: string, reqId: string, comments: string = ""): Promise<RequisitionHeader> {
  const { data } = await client.post<RequisitionHeader>(`/v1/projects/${projectId}/requisitions/${reqId}/reject/`, { comments });
  return data;
}

export async function returnRequisition(projectId: string, reqId: string, comments: string = ""): Promise<RequisitionHeader> {
  const { data } = await client.post<RequisitionHeader>(`/v1/projects/${projectId}/requisitions/${reqId}/return/`, { comments });
  return data;
}

export async function fetchApprovalLogs(projectId: string, reqId: string): Promise<ApprovalLog[]> {
  const { data } = await client.get<any>(`/v1/projects/${projectId}/requisitions/${reqId}/approval-logs/`);
  return normalizeList<ApprovalLog>(data);
}

// Procurement Operations API
export async function assignItems(projectId: string, reqId: string, assignments: any[]) {
  const { data } = await client.post(`/v1/projects/${projectId}/requisitions/${reqId}/assign-items/`, { assignments });
  return data;
}

export async function partialApprove(projectId: string, reqId: string, approvals: any[]) {
  const { data } = await client.post<any>(`/v1/projects/${projectId}/requisitions/${reqId}/partial-approve/`, { approvals });
  return data;
}

// Block Inventory API
export async function fetchBlockStock(projectId: string, blockId: string): Promise<any[]> {
  const { data } = await client.get<any>(`/v1/projects/${projectId}/blocks/${blockId}/stock/`);
  return normalizeList<any>(data);
}

export async function recordGRN(projectId: string, blockId: string, payload: { requisition_item_id: string; received_qty: number }) {
  const { data } = await client.post<any>(`/v1/projects/${projectId}/blocks/${blockId}/grn/`, payload);
  return data;
}

export async function issueStock(projectId: string, blockId: string, payload: { allocation_id: string; issue_qty: number }) {
  const { data } = await client.post<any>(`/v1/projects/${projectId}/blocks/${blockId}/issue/`, payload);
  return data;
}

// Internal Transfers API
export async function fetchTransfers(projectId: string): Promise<InternalTransfer[]> {
  const { data } = await client.get<any>(`/v1/projects/${projectId}/transfers/`);
  return normalizeList<InternalTransfer>(data);
}

export async function createTransfer(projectId: string, payload: any): Promise<InternalTransfer> {
  const { data } = await client.post<InternalTransfer>(`/v1/projects/${projectId}/transfers/`, payload);
  return data;
}

export interface LiquidityStatusItem {
  block_code: string;
  block_name: string;
  budget: number;
  total_requested_value: number;
  remaining_liquidity: number;
}

export interface LiquidityReportResponse {
  project_id: string;
  on_hold_count?: number;
  liquidity_status: LiquidityStatusItem[];
}

export interface MaterialDeviationItem {
  block_code: string;
  block_name?: string;
  material_code?: string;
  material_name: string;
  estimated_qty: number | null;
  requested_qty: number;
  deviation_qty: number;
  deviation_percent: number;
}

export interface MaterialDeviationReportResponse {
  project_id: string;
  deviation_data: MaterialDeviationItem[];
}

export interface AuditTrailSummary {
  total_actions: number;
  approved_actions: number;
  rejected_actions: number;
}

export interface AuditTrailReportResponse {
  project_id: string;
  count: number;
  summary: AuditTrailSummary;
  logs?: ApprovalLog[];
}

// Reports API
export async function fetchLiquidityReport(projectId: string): Promise<LiquidityReportResponse> {
  const { data } = await client.get<LiquidityReportResponse>(`/v1/projects/${projectId}/reports/liquidity/`);
  return data;
}

export async function fetchMaterialDeviationReport(projectId: string): Promise<MaterialDeviationReportResponse> {
  const { data } = await client.get<MaterialDeviationReportResponse>(`/v1/projects/${projectId}/reports/material-deviation/`);
  return data;
}

export async function fetchAuditTrailReport(projectId: string, params?: Record<string, any>): Promise<AuditTrailReportResponse> {
  const { data } = await client.get<AuditTrailReportResponse>(`/v1/projects/${projectId}/reports/audit-trail/`, { params });
  return data;
}

export async function fetchProcurementStatusReport(projectId: string) {
  const { data } = await client.get<any>(`/v1/projects/${projectId}/reports/procurement-status/`);
  return data;
}
