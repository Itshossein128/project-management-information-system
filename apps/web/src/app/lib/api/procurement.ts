import { client } from "./client";

// Types
export interface Block {
  id: string;
  project: string;
  block_code: string;
  block_name: string;
  wbs: string | null;
  budget: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
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

export interface RequisitionHeader {
  id: string;
  project: string;
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
  created_at: string;
  updated_at: string;
}

export interface ApprovalLog {
  id: string;
  requisition: string;
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

// Blocks API
export async function fetchBlocks(projectId: string) {
  const { data } = await client.get<Block[]>(`/v1/projects/${projectId}/blocks/`);
  return data;
}

// Requisitions API
export async function fetchRequisitions(projectId: string, params?: Record<string, any>) {
  const { data } = await client.get<RequisitionHeader[]>(`/v1/projects/${projectId}/requisitions/`, { params });
  return data;
}

export async function fetchRequisition(projectId: string, reqId: string) {
  const { data } = await client.get<RequisitionHeader>(`/v1/projects/${projectId}/requisitions/${reqId}/`);
  return data;
}

export async function createRequisition(projectId: string, payload: any) {
  const { data } = await client.post<RequisitionHeader>(`/v1/projects/${projectId}/requisitions/`, payload);
  return data;
}

// Approval Workflow API
export async function submitRequisition(projectId: string, reqId: string, comments: string = "") {
  const { data } = await client.post<RequisitionHeader>(`/v1/projects/${projectId}/requisitions/${reqId}/submit/`, { comments });
  return data;
}

export async function approveRequisition(projectId: string, reqId: string, comments: string = "") {
  const { data } = await client.post<RequisitionHeader>(`/v1/projects/${projectId}/requisitions/${reqId}/approve/`, { comments });
  return data;
}

export async function rejectRequisition(projectId: string, reqId: string, comments: string = "") {
  const { data } = await client.post<RequisitionHeader>(`/v1/projects/${projectId}/requisitions/${reqId}/reject/`, { comments });
  return data;
}

export async function returnRequisition(projectId: string, reqId: string, comments: string = "") {
  const { data } = await client.post<RequisitionHeader>(`/v1/projects/${projectId}/requisitions/${reqId}/return/`, { comments });
  return data;
}

export async function fetchApprovalLogs(projectId: string, reqId: string) {
  const { data } = await client.get<ApprovalLog[]>(`/v1/projects/${projectId}/requisitions/${reqId}/approval-logs/`);
  return data;
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
export async function fetchBlockStock(projectId: string, blockId: string) {
  const { data } = await client.get<any[]>(`/v1/projects/${projectId}/blocks/${blockId}/stock/`);
  return data;
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
export async function fetchTransfers(projectId: string) {
  const { data } = await client.get<InternalTransfer[]>(`/v1/projects/${projectId}/transfers/`);
  return data;
}

export async function createTransfer(projectId: string, payload: any) {
  const { data } = await client.post<InternalTransfer>(`/v1/projects/${projectId}/transfers/`, payload);
  return data;
}

// Reports API
export async function fetchLiquidityReport(projectId: string) {
  const { data } = await client.get<any>(`/v1/projects/${projectId}/reports/liquidity/`);
  return data;
}

export async function fetchMaterialDeviationReport(projectId: string) {
  const { data } = await client.get<any>(`/v1/projects/${projectId}/reports/material-deviation/`);
  return data;
}

export async function fetchAuditTrailReport(projectId: string, params?: Record<string, any>) {
  const { data } = await client.get<any>(`/v1/projects/${projectId}/reports/audit-trail/`, { params });
  return data;
}

export async function fetchProcurementStatusReport(projectId: string) {
  const { data } = await client.get<any>(`/v1/projects/${projectId}/reports/procurement-status/`);
  return data;
}
