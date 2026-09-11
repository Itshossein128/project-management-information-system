import { useProductTour } from "@/components/tour/useProductTour";
import { ProductTourButton } from "@/components/tour/ProductTourButton";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { PageHeader, Breadcrumb, LoadingSkeleton } from "@/components/layout/page-header";
import { ProjectProvider, useProject } from "~/contexts/project-context";
import {
  approveTransfer,
  createTransfer,
  fetchBlocks,
  fetchTransfers,
  rejectTransfer,
} from "~/lib/api/procurement";
import { fetchMaterials } from "~/lib/api/materials";
import { PATHS } from "~/routeVars";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { useToast } from "@/components/ui/toast";

function TransfersContent() {
  const { t } = useTranslation();
  const { startTour } = useProductTour({
    tourId: "procurement-transfers",
    steps: [
      {
        element: "[data-tour='transfer-form']",
        popover: {
          title: t("tour.procurementTransfers.step1Title"),
          description: t("tour.procurementTransfers.step1Desc"),
        },
      },
      {
        element: "[data-tour='transfer-list']",
        popover: {
          title: t("tour.procurementTransfers.step2Title"),
          description: t("tour.procurementTransfers.step2Desc"),
        },
      },
      {
        element: "[data-tour='transfer-approve']",
        popover: {
          title: t("tour.procurementTransfers.step3Title"),
          description: t("tour.procurementTransfers.step3Desc"),
        },
      },
    ],
  });

  const { projectId, project } = useProject();
  const qc = useQueryClient();
  const toast = useToast();
  const [sourceBlock, setSourceBlock] = useState("");
  const [targetBlock, setTargetBlock] = useState("");
  const [materialId, setMaterialId] = useState("");
  const [quantity, setQuantity] = useState("");
  const [reason, setReason] = useState("");

  const { data: blocks = [] } = useQuery({
    queryKey: ["blocks", projectId, "all"],
    queryFn: () => fetchBlocks(projectId, { includeSystem: true }),
  });
  const { data: rawMaterials = [] } = useQuery({
    queryKey: ["materials", projectId],
    queryFn: () => fetchMaterials(projectId),
  });
  const materials = Array.isArray(rawMaterials) ? rawMaterials : ((rawMaterials as { results?: unknown[] })?.results ?? []);

  const { data: transfers = [], isLoading, isError, refetch } = useQuery({
    queryKey: ["transfers", projectId],
    queryFn: () => fetchTransfers(projectId),
  });

  const createMut = useMutation({
    mutationFn: () =>
      createTransfer(projectId, {
        source_block: sourceBlock,
        target_block: targetBlock,
        material: materialId,
        quantity: Number(quantity),
        reason,
      }),
    onSuccess: () => {
      toast.success(t("pages.procurement.transfers.createSuccess"));
      setQuantity("");
      setReason("");
      void qc.invalidateQueries({ queryKey: ["transfers", projectId] });
    },
    onError: (e: Error) => toast.error(e.message || t("pages.procurement.transfers.createError")),
  });

  const approveMut = useMutation({
    mutationFn: (id: string) => approveTransfer(projectId, id),
    onSuccess: () => {
      toast.success(t("pages.procurement.transfers.approveSuccess"));
      void qc.invalidateQueries({ queryKey: ["transfers", projectId] });
      void qc.invalidateQueries({ queryKey: ["blockStock", projectId] });
    },
    onError: (e: Error) => toast.error(e.message || t("pages.procurement.transfers.approveError")),
  });

  const rejectMut = useMutation({
    mutationFn: (id: string) => rejectTransfer(projectId, id),
    onSuccess: () => {
      toast.success(t("pages.procurement.transfers.rejectSuccess"));
      void qc.invalidateQueries({ queryKey: ["transfers", projectId] });
    },
    onError: (e: Error) => toast.error(e.message || t("pages.procurement.transfers.rejectError")),
  });

  const handleCreate = () => {
    if (!sourceBlock || !targetBlock || !materialId || !quantity || !reason.trim()) {
      return toast.error(t("pages.procurement.transfers.requiredFields"));
    }
    createMut.mutate();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <PageHeader title={t("pages.procurement.transfers.title")} subtitle={project?.project_name} />
        <ProductTourButton onClick={startTour} />
      </div>

      <div className="space-y-4 rounded-lg border border-border bg-card p-4" data-tour="transfer-form">
        <h3 className="font-medium">{t("pages.procurement.transfers.formTitle")}</h3>
        <p className="text-sm text-muted-foreground">{t("pages.procurement.transfers.formHint")}</p>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <label className="flex flex-col gap-1 text-sm">
            <span>{t("pages.procurement.transfers.sourceBlock")}</span>
            <select className="rounded-md border px-3 py-2" value={sourceBlock} onChange={(e) => setSourceBlock(e.target.value)}>
              <option value="">{t("pages.procurement.workshop.selectBlock")}</option>
              {blocks.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.block_code} — {b.block_name}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span>{t("pages.procurement.transfers.targetBlock")}</span>
            <select className="rounded-md border px-3 py-2" value={targetBlock} onChange={(e) => setTargetBlock(e.target.value)}>
              <option value="">{t("pages.procurement.workshop.selectBlock")}</option>
              {blocks.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.block_code} — {b.block_name}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span>{t("pages.procurement.workshop.material")}</span>
            <select className="rounded-md border px-3 py-2" value={materialId} onChange={(e) => setMaterialId(e.target.value)}>
              <option value="">{t("pages.procurement.workshop.selectMaterial")}</option>
              {(materials as { id: string; material_code: string; material_name: string }[]).map((m) => (
                <option key={m.id} value={m.id}>
                  {m.material_code} — {m.material_name}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span>{t("pages.procurement.workshop.quantity")}</span>
            <input
              type="number"
              min="0.0001"
              step="any"
              className="rounded-md border px-3 py-2"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
            />
          </label>
        </div>
        <label className="flex flex-col gap-1 text-sm">
          <span>{t("pages.procurement.transfers.reason")}</span>
          <textarea className="rounded-md border px-3 py-2" rows={3} value={reason} onChange={(e) => setReason(e.target.value)} />
        </label>
        <Button type="button" onClick={handleCreate} disabled={createMut.isPending}>
          {t("pages.procurement.transfers.submit")}
        </Button>
      </div>

      <div data-tour="transfer-list">
        {isLoading ? (
          <LoadingSkeleton rows={6} />
        ) : isError ? (
          <QueryErrorState onRetry={() => void refetch()} />
        ) : transfers.length === 0 ? (
          <p className="rounded-lg border border-border p-8 text-center text-sm text-muted-foreground">
            {t("pages.procurement.transfers.empty")}
          </p>
        ) : (
          <div className="overflow-x-auto rounded-lg border border-border">
            <table className="w-full text-sm text-start">
              <thead className="bg-muted/50">
                <tr>
                  <th className="px-3 py-2 text-start">{t("pages.procurement.transfers.sourceBlock")}</th>
                  <th className="px-3 py-2 text-start">{t("pages.procurement.transfers.targetBlock")}</th>
                  <th className="px-3 py-2 text-start">{t("pages.procurement.workshop.material")}</th>
                  <th className="px-3 py-2 text-start">{t("pages.procurement.workshop.quantity")}</th>
                  <th className="px-3 py-2 text-start">{t("pages.procurement.workshop.colStatus")}</th>
                  <th className="px-3 py-2 text-start">{t("pages.procurement.workshop.colActions")}</th>
                </tr>
              </thead>
              <tbody>
                {transfers.map((row, index) => (
                  <tr key={row.id} className="border-t border-border">
                    <td className="px-3 py-2">{row.source_block_code}</td>
                    <td className="px-3 py-2">{row.target_block_code}</td>
                    <td className="px-3 py-2">{row.material_name}</td>
                    <td className="px-3 py-2">{row.quantity}</td>
                    <td className="px-3 py-2">{row.status_display}</td>
                    <td className="px-3 py-2" {...(index === 0 ? { "data-tour": "transfer-approve" } : {})}>
                      {row.status === "pending" ? (
                        <div className="flex gap-2">
                          <Button size="sm" onClick={() => approveMut.mutate(row.id)} disabled={approveMut.isPending}>
                            {t("pages.procurement.transfers.approve")}
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => rejectMut.mutate(row.id)}
                            disabled={rejectMut.isPending}
                          >
                            {t("pages.procurement.transfers.reject")}
                          </Button>
                        </div>
                      ) : (
                        <span className="text-xs text-muted-foreground">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default function ProcurementTransfersPage() {
  const { projectId } = useParams();
  const { t } = useTranslation();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto px-4 py-8">
        <Breadcrumb
          items={[
            { label: t("project.title"), href: `/${PATHS.PROJECT}` },
            { label: t("pages.procurement.title"), href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT}` },
            { label: t("pages.procurement.transfers.title") },
          ]}
        />
        <TransfersContent />
      </main>
    </ProjectProvider>
  );
}
