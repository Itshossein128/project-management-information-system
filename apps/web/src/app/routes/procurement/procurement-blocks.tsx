import { useProductTour } from "@/components/tour/useProductTour";
import { ProductTourButton } from "@/components/tour/ProductTourButton";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useParams } from "react-router";
import { useTranslation } from "react-i18next";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/sprint-button";
import { DataTable } from "@/components/ui/data-table";
import { Modal } from "@/components/overlay/modal";
import { EmptyState } from "@/components/layout/empty-state";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { useToast } from "@/components/ui/toast";
import { ProjectProvider, usePermission, useProject } from "~/contexts/project-context";
import {
  createBlock,
  deleteBlock,
  fetchBlocks,
  updateBlock,
  type Block,
  type BlockPayload,
} from "~/lib/api/procurement";
import { fetchWBSFlat } from "~/lib/api/wbs";
import { PATHS } from "~/routeVars";

const emptyForm = (): BlockPayload => ({
  block_code: "",
  block_name: "",
  wbs: "",
  budget: "0",
  is_active: true,
});

function BlockFormModal({
  open,
  onOpenChange,
  projectId,
  editBlock,
  canEdit,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectId: string;
  editBlock: Block | null;
  canEdit: boolean;
}) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const [form, setForm] = useState<BlockPayload>(emptyForm);

  const { data: wbsNodes = [] } = useQuery({
    queryKey: ["wbs-flat", projectId],
    queryFn: () => fetchWBSFlat(projectId),
    enabled: open,
  });

  const resetForm = (block: Block | null) => {
    if (block) {
      setForm({
        block_code: block.block_code,
        block_name: block.block_name,
        wbs: block.wbs ?? "",
        budget: block.budget,
        is_active: block.is_active,
      });
    } else {
      setForm(emptyForm());
    }
  };

  useEffect(() => {
    if (open) {
      resetForm(editBlock);
    }
  }, [open, editBlock]);

  const saveMutation = useMutation({
    mutationFn: async (payload: BlockPayload) => {
      const body: BlockPayload = {
        block_code: payload.block_code.trim(),
        block_name: payload.block_name.trim(),
        budget: payload.budget ?? "0",
        is_active: payload.is_active ?? true,
        wbs: payload.wbs ? payload.wbs : null,
      };
      if (editBlock) {
        return updateBlock(projectId, editBlock.id, body);
      }
      return createBlock(projectId, body);
    },
    onSuccess: () => {
      toast.success(
        editBlock
          ? t("pages.procurement.blocks.updateSuccess")
          : t("pages.procurement.blocks.createSuccess"),
      );
      void qc.invalidateQueries({ queryKey: ["blocks", projectId] });
      onOpenChange(false);
    },
    onError: (e: Error) => toast.error(e.message || t("pages.procurement.blocks.saveError")),
  });

  const handleOpenChange = (next: boolean) => {
    onOpenChange(next);
  };

  if (!canEdit) return null;

  return (
    <Modal
      open={open}
      onOpenChange={handleOpenChange}
      title={
        editBlock
          ? t("pages.procurement.blocks.editTitle")
          : t("pages.procurement.blocks.createTitle")
      }
      idBase="blockForm"
    >
      <form
        className="space-y-4 p-4"
        onSubmit={(e) => {
          e.preventDefault();
          if (!form.block_code.trim() || !form.block_name.trim()) {
            toast.error(t("pages.procurement.blocks.requiredFields"));
            return;
          }
          saveMutation.mutate(form);
        }}
      >
        <label className="flex flex-col gap-1 text-sm">
          <span>{t("pages.procurement.blocks.blockCode")}</span>
          <input
            className="rounded-md border px-3 py-2"
            value={form.block_code}
            maxLength={30}
            required
            onChange={(e) => setForm({ ...form, block_code: e.target.value })}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>{t("pages.procurement.blocks.blockName")}</span>
          <input
            className="rounded-md border px-3 py-2"
            value={form.block_name}
            maxLength={200}
            required
            onChange={(e) => setForm({ ...form, block_name: e.target.value })}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>{t("pages.procurement.blocks.wbs")}</span>
          <select
            className="rounded-md border px-3 py-2"
            value={form.wbs ?? ""}
            onChange={(e) => setForm({ ...form, wbs: e.target.value })}
          >
            <option value="">{t("pages.procurement.blocks.noWbs")}</option>
            {wbsNodes.map((node) => (
              <option key={node.wbs_id} value={node.wbs_id}>
                {node.wbs_code} — {node.wbs_name}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>{t("pages.procurement.blocks.budget")}</span>
          <input
            type="number"
            min="0"
            step="any"
            className="rounded-md border px-3 py-2"
            value={form.budget ?? "0"}
            onChange={(e) => setForm({ ...form, budget: e.target.value })}
          />
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={form.is_active ?? true}
            onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
          />
          <span>{t("pages.procurement.blocks.isActive")}</span>
        </label>
        <div className="flex justify-end gap-2 border-t border-border pt-4">
          <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>
            {t("common.cancel")}
          </Button>
          <Button type="submit" variant="primary" loading={saveMutation.isPending}>
            {editBlock ? t("common.save") : t("common.create")}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

function ProcurementBlocksContent() {
  const { t } = useTranslation();
  const { startTour } = useProductTour({
    tourId: "procurement-blocks",
    steps: [
      {
        element: "[data-tour='blocks-catalog']",
        popover: {
          title: t("tour.procurementBlocks.step1Title"),
          description: t("tour.procurementBlocks.step1Desc"),
        },
      },
      {
        element: "[data-tour='blocks-overview']",
        popover: {
          title: t("tour.procurementBlocks.step2Title"),
          description: t("tour.procurementBlocks.step2Desc"),
        },
      },
    ],
  });

  const toast = useToast();
  const qc = useQueryClient();
  const { projectId, project, isLoading: projectLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_procurement");
  const canEdit = has("edit_reports");

  const [formOpen, setFormOpen] = useState(false);
  const [editBlock, setEditBlock] = useState<Block | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Block | null>(null);

  const { data: blocks = [], isLoading, isError, refetch } = useQuery({
    queryKey: ["blocks", projectId, "all"],
    queryFn: () => fetchBlocks(projectId, { includeSystem: true }),
    enabled: canView,
  });

  const deleteMutation = useMutation({
    mutationFn: (blockId: string) => deleteBlock(projectId, blockId),
    onSuccess: () => {
      toast.success(t("pages.procurement.blocks.deleteSuccess"));
      setDeleteTarget(null);
      void qc.invalidateQueries({ queryKey: ["blocks", projectId] });
    },
    onError: (e: Error) => toast.error(e.message || t("pages.procurement.blocks.deleteError")),
  });

  const openCreate = () => {
    setEditBlock(null);
    setFormOpen(true);
  };

  const openEdit = (block: Block) => {
    setEditBlock(block);
    setFormOpen(true);
  };

  if (projectLoading) return <LoadingSkeleton rows={8} />;
  if (!project) return <p>{t("project.notFound")}</p>;
  if (!canView) return <p className="p-8 text-center">{t("common.accessDenied")}</p>;

  const columns = [
    {
      key: "block_code",
      label: t("pages.procurement.blocks.blockCode"),
      render: (row: Block) => (
        <span className="font-medium">
          {row.is_system ? "🔒 " : ""}
          {row.block_code}
        </span>
      ),
    },
    {
      key: "block_name",
      label: t("pages.procurement.blocks.blockName"),
      render: (row: Block) => row.block_name,
    },
    {
      key: "wbs",
      label: t("pages.procurement.blocks.wbs"),
      render: (row: Block) =>
        row.wbs_code ? `${row.wbs_code} — ${row.wbs_name ?? ""}` : "—",
    },
    {
      key: "budget",
      label: t("pages.procurement.blocks.budget"),
      render: (row: Block) => Number(row.budget).toLocaleString(),
    },
    {
      key: "is_active",
      label: t("pages.procurement.blocks.status"),
      render: (row: Block) => (
        <Badge
          variant={row.is_active ? "success" : "neutral"}
          label={
            row.is_active
              ? t("pages.procurement.blocks.active")
              : t("pages.procurement.blocks.inactive")
          }
        />
      ),
    },
    ...(canEdit
      ? [
          {
            key: "actions",
            label: t("pages.procurement.blocks.actions"),
            render: (row: Block) =>
              row.is_system ? (
                <span className="text-xs text-muted-foreground">{t("pages.procurement.blocks.systemBlock")}</span>
              ) : (
                <div className="flex gap-1">
                  <Button variant="ghost" size="sm" onClick={() => openEdit(row)}>
                    {t("common.edit")}
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => setDeleteTarget(row)}>
                    {t("common.delete")}
                  </Button>
                </div>
              ),
          },
        ]
      : []),
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("pages.procurement.blocks.title")}
        subtitle={project.project_name}
        actions={
          canEdit ? (
            <Button variant="primary" onClick={openCreate}>
              {t("pages.procurement.blocks.add")}
            </Button>
          ) : undefined
        }
      />

      {isLoading ? (
        <LoadingSkeleton rows={8} />
      ) : isError ? (
        <QueryErrorState onRetry={() => void refetch()} />
      ) : blocks.length === 0 ? (
        <EmptyState
          title={t("pages.procurement.blocks.empty")}
          description={t("pages.procurement.blocks.emptyDescription")}
          action={
            canEdit ? (
              <Button variant="primary" onClick={openCreate}>
                {t("pages.procurement.blocks.add")}
              </Button>
            ) : undefined
          }
        />
      ) : (
        <DataTable
          columns={columns}
          data={blocks}
          rowKey={(row) => row.id}
          emptyMessage={t("pages.procurement.blocks.empty")}
        />
      )}

      <BlockFormModal
        open={formOpen}
        onOpenChange={setFormOpen}
        projectId={projectId}
        editBlock={editBlock}
        canEdit={canEdit}
      />

      <Modal
        open={Boolean(deleteTarget)}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title={t("pages.procurement.blocks.deleteTitle")}
        idBase="deleteBlock"
      >
        <p className="mb-4 px-4 text-sm">
          {t("pages.procurement.blocks.deleteConfirm", {
            code: deleteTarget?.block_code,
            name: deleteTarget?.block_name,
          })}
        </p>
        <div className="flex justify-end gap-2 border-t border-border px-4 py-3">
          <Button variant="ghost" onClick={() => setDeleteTarget(null)}>
            {t("common.cancel")}
          </Button>
          <Button
            variant="danger"
            loading={deleteMutation.isPending}
            onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
          >
            {t("common.delete")}
          </Button>
        </div>
      </Modal>
    </div>
  );
}

export default function ProcurementBlocksPage() {
  const { projectId } = useParams();
  const { t } = useTranslation();

  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto px-4 py-8">
        <Breadcrumb
          items={[
            { label: t("project.title"), href: `/${PATHS.PROJECT}` },
            {
              label: t("pages.procurement.title"),
              href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT}`,
            },
            { label: t("pages.procurement.blocks.title") },
          ]}
        />
        <ProcurementBlocksContent />
      </main>
    </ProjectProvider>
  );
}
