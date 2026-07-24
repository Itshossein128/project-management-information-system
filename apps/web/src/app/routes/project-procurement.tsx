import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import { fetchSuppliers } from "@/app/lib/api/costs";
import { fetchMaterials } from "@/app/lib/api/materials";
import {
  approveProcurementRequest,
  cancelProcurementRequest,
  createProcurementRequest,
  deliverProcurementRequest,
  fetchProcurementRequests,
  placeProcurementOrder,
  REQUEST_STATUS_LABELS,
  type ProcurementRequest,
} from "@/app/lib/api/procurement";
import { PATHS } from "@/app/routeVars";
import { EmptyState } from "@/components/layout/empty-state";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

function WorkflowActions({
  projectId,
  row,
  canApprove,
  canProcure,
}: {
  projectId: string;
  row: ProcurementRequest;
  canApprove: boolean;
  canProcure: boolean;
}) {
  const toast = useToast();
  const qc = useQueryClient();
  const invalidate = () => {

    void qc.invalidateQueries({ queryKey: ["procurement", projectId] });
    void qc.invalidateQueries({ queryKey: ["material-requests", projectId] });
    void qc.invalidateQueries({ queryKey: ["material-balance", projectId] });
  };

  const approve = useMutation({
    mutationFn: () => approveProcurementRequest(projectId, row.id),
    onSuccess: () => {
      toast.success("درخواست تأیید شد");
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const cancel = useMutation({
    mutationFn: () => cancelProcurementRequest(projectId, row.id),
    onSuccess: () => {
      toast.success("درخواست لغو شد");
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const deliver = useMutation({
    mutationFn: () => deliverProcurementRequest(projectId, row.id, {}),
    onSuccess: () => {
      toast.success("تحویل ثبت شد");
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <div className="flex flex-wrap gap-1">
      {row.status === "pending" && canApprove ? (
        <Button size="sm" variant="primary" loading={approve.isPending} onClick={() => approve.mutate()}>
          تأیید
        </Button>
      ) : null}
      {row.status === "pending" && canProcure ? (
        <Button size="sm" variant="secondary" loading={cancel.isPending} onClick={() => cancel.mutate()}>
          لغو
        </Button>
      ) : null}
      {row.status === "ordered" && canProcure ? (
        <Button size="sm" variant="primary" loading={deliver.isPending} onClick={() => deliver.mutate()}>
          ثبت تحویل
        </Button>
      ) : null}
    </div>
  );
}

function PlaceOrderDrawer({
  projectId,
  request,
  open,
  onClose,
}: {
  projectId: string;
  request: ProcurementRequest | null;
  open: boolean;
  onClose: () => void;
}) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const [supplierId, setSupplierId] = useState("");

  const { data: suppliers = [] } = useQuery({
    queryKey: ["suppliers", projectId],
    queryFn: () => fetchSuppliers(projectId),
    enabled: open,
  });

  const place = useMutation({
    mutationFn: () =>
      placeProcurementOrder(projectId, request!.id, { supplier: supplierId }),
    onSuccess: () => {
      toast.success("سفارش خرید ثبت شد");
      void qc.invalidateQueries({ queryKey: ["procurement", projectId] });
      onClose();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <Drawer
      isOpen={open}
      onClose={onClose}
      title={t("pages.procurement.newOrder")}
      footer={
        <Button
          variant="primary"
          disabled={!supplierId || !request}
          loading={place.isPending}
          onClick={() => place.mutate()}
        >
          ثبت PO
        </Button>
      }
    >
      <label className="flex flex-col gap-1 text-sm">
        <span>تأمین‌کننده</span>
        <select
          className="rounded-md border px-3 py-2"
          value={supplierId}
          onChange={(e) => setSupplierId(e.target.value)}
        >
          <option value="">انتخاب…</option>
          {suppliers.map((s) => (
            <option key={s.id} value={s.id}>
              {s.supplier_name}
            </option>
          ))}
        </select>
      </label>
    </Drawer>
  );
}

function ProcurementContent() {
  const { t } = useTranslation();

  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const toast = useToast();
  const qc = useQueryClient();
  const canView = has("view_procurement");
  const canCreate = has("edit_reports");
  const canApprove = has("approve_procurement");
  const canProcure = has("edit_procurement");

  const [statusFilter, setStatusFilter] = useState("");
  const [createOpen, setCreateOpen] = useState(false);
  const [orderRequest, setOrderRequest] = useState<ProcurementRequest | null>(null);
  const [materialId, setMaterialId] = useState("");
  const [qty, setQty] = useState("");

  const {
    data: requests = [],
    isLoading: loadingRequests,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["procurement", projectId, statusFilter],
    queryFn: () => fetchProcurementRequests(projectId, statusFilter || undefined),
    enabled: canView,
  });

  const { data: materials = [] } = useQuery({
    queryKey: ["materials", projectId],
    queryFn: () => fetchMaterials(projectId),
    enabled: canCreate && createOpen,
  });

  const create = useMutation({
    mutationFn: () =>
      createProcurementRequest(projectId, {
        material: materialId,
        requested_qty: Number(qty),
      }),
    onSuccess: () => {
      toast.success("درخواست ثبت شد");
      setCreateOpen(false);
      setMaterialId("");
      setQty("");
      void qc.invalidateQueries({ queryKey: ["procurement", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (isLoading) return <LoadingSkeleton rows={10} />;
  if (!project) return <p>پروژه یافت نشد</p>;
  if (!canView) {
    return (
      <p className="rounded-lg border border-border bg-card p-8 text-center text-muted-foreground">
        {t("common.accessDenied")}
      </p>
    );
  }

  return (
    <div className="space-y-6" data-testid="procurement-page">
      <PageHeader title={t("pages.procurement.title")} subtitle={project.project_name} />

      <div className="flex flex-wrap items-end gap-3">
        <label className="flex flex-col gap-1 text-sm">
          <span>وضعیت</span>
          <select
            className="rounded-md border px-3 py-2"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">همه</option>
            {Object.entries(REQUEST_STATUS_LABELS).map(([k, v]) => (
              <option key={k} value={k}>
                {v}
              </option>
            ))}
          </select>
        </label>
        {canCreate ? (
          <Button variant="primary" onClick={() => setCreateOpen(true)}>
            درخواست جدید
          </Button>
        ) : null}
      </div>

      {loadingRequests ? (
        <LoadingSkeleton rows={8} />
      ) : isError ? (
        <QueryErrorState onRetry={() => void refetch()} />
      ) : requests.length === 0 ? (
        <EmptyState title={t("pages.procurement.empty")} description={t("pages.procurement.emptyDescription")} />
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm" data-testid="procurement-table">
            <thead className="bg-muted/50">
              <tr>
                {["شماره", "مصالح", "مقدار", "وضعیت", "PO", "عملیات"].map((h) => (
                  <th key={h} className="px-3 py-2 text-start">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {requests.map((r) => (
                <tr key={r.id} className="border-t border-border">
                  <td className="px-3 py-2">{r.request_number}</td>
                  <td className="px-3 py-2">{r.material_name}</td>
                  <td className="px-3 py-2">
                    {r.requested_qty} {r.unit}
                  </td>
                  <td className="px-3 py-2">{REQUEST_STATUS_LABELS[r.status] ?? r.status}</td>
                  <td className="px-3 py-2">
                    {r.purchase_order ? `PO-${r.purchase_order.po_number}` : "—"}
                  </td>
                  <td className="px-3 py-2">
                    <div className="flex flex-wrap items-center gap-2">
                      {r.status === "approved" && canProcure ? (
                        <Button size="sm" variant="primary" onClick={() => setOrderRequest(r)}>
                          سفارش
                        </Button>
                      ) : null}
                      <WorkflowActions
                        projectId={projectId}
                        row={r}
                        canApprove={canApprove}
                        canProcure={canProcure}
                      />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Drawer
        isOpen={createOpen}
        onClose={() => setCreateOpen(false)}
        title={t("pages.procurement.request")}
        footer={
          <Button
            variant="primary"
            disabled={!materialId || !qty}
            loading={create.isPending}
            onClick={() => create.mutate()}
          >
            ثبت
          </Button>
        }
      >
        <div className="space-y-4">
          <label className="flex flex-col gap-1 text-sm">
            <span>مصالح</span>
            <select
              className="rounded-md border px-3 py-2"
              value={materialId}
              onChange={(e) => setMaterialId(e.target.value)}
            >
              <option value="">انتخاب…</option>
              {materials.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.material_code} — {m.material_name}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span>مقدار</span>
            <input
              type="number"
              className="rounded-md border px-3 py-2"
              value={qty}
              onChange={(e) => setQty(e.target.value)}
            />
          </label>
        </div>
      </Drawer>

      <PlaceOrderDrawer
        projectId={projectId}
        request={orderRequest}
        open={Boolean(orderRequest)}
        onClose={() => setOrderRequest(null)}
      />
    </div>
  );
}

export default function ProjectProcurementPage() {
  const { t, i18n } = useTranslation();
  const { projectId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto px-4 py-8">
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "تأمین و خرید" },
          ]}
        />
        <ProcurementContent />
      </main>
    </ProjectProvider>
  );
}
