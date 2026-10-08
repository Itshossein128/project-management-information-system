import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChevronLeft, Pencil, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { fetchMembers } from "@/app/lib/api/members";
import {
  createWBSNode,
  deleteWBSNode,
  moveWBSNode,
  updateWBSNode,
  type WBSNode,
} from "@/app/lib/api/wbs";
import { Button } from "@/components/ui/sprint-button";
import { Input } from "@/components/form";
import { useToast } from "@/components/ui/toast";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from "@/components/ui/collapsible";

const INDENT_PX = 24;
const UNDO_DURATION_MS = 10_000;

interface WBSNodeRowProps {
  node: WBSNode;
  projectId: string;
  parentId?: string | null;
  depth?: number;
  canEdit?: boolean;
}

function parseWeight(value: string | null | undefined): number | null {
  if (value == null || value === "") return null;
  const n = Number(value);
  return Number.isNaN(n) ? null : n;
}

function uniqueTempCode(): string {
  return `t${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`;
}

export function WBSNodeRow({
  node,
  projectId,
  parentId = null,
  depth = 0,
  canEdit = true,
}: WBSNodeRowProps) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const [expanded, setExpanded] = useState(true);
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(node.wbs_name);
  const [acceptance, setAcceptance] = useState(node.acceptance_criteria ?? "");
  const [responsible, setResponsible] = useState(node.responsible ?? "");
  const [status, setStatus] = useState(node.status ?? "active");
  const [addingChild, setAddingChild] = useState(false);
  const [childCode, setChildCode] = useState("");
  const [childName, setChildName] = useState("");

  const { data: members = [] } = useQuery({
    queryKey: ["members", projectId],
    queryFn: () => fetchMembers(projectId),
    enabled: Boolean(projectId),
  });
  const activeMembers = members.filter((m) => m.status === "active" && m.user_id);
  const responsibleLabel =
    activeMembers.find((m) => m.user_id === node.responsible)?.full_name ||
    members.find((m) => m.user_id === node.responsible)?.full_name ||
    (node.responsible ? node.responsible.slice(0, 8) : null);

  const hasChildren = node.children.length > 0;
  const level = node.depth > 0 ? node.depth - 1 : depth;
  const indent = level * INDENT_PX;
  const defaultChildCode = `${node.wbs_code}.${node.children.length + 1}`;

  const invalidate = () =>
    void qc.invalidateQueries({ queryKey: ["wbs", projectId] });

  const offerUndo = (message: string, run: () => Promise<void>) => {
    toast.success(message, {
      duration: UNDO_DURATION_MS,
      action: {
        label: t("common.undo"),
        onClick: () => {
          void run()
            .then(() => {
              invalidate();
              toast.success(t("common.undoSuccess"));
            })
            .catch((err: Error) => toast.error(err.message));
        },
      },
    });
  };

  const updateMutation = useMutation({
    mutationFn: (payload: {
      wbs_name?: string;
      weight_physical?: number | null;
      responsible?: string | null;
      acceptance_criteria?: string;
      status?: "draft" | "active" | "completed" | "on_hold";
    }) => updateWBSNode(projectId, node.wbs_id, payload),
    onSuccess: (_data, payload) => {
      invalidate();
      setEditing(false);
      const previousName = node.wbs_name;
      if (payload.wbs_name != null && payload.wbs_name !== previousName) {
        offerUndo(t("wbs.updated"), async () => {
          await updateWBSNode(projectId, node.wbs_id, { wbs_name: previousName });
        });
      }
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createWBSNode(projectId, {
        parent_id: node.wbs_id,
        wbs_code: childCode || defaultChildCode,
        wbs_name: childName,
      }),
    onSuccess: (created) => {
      invalidate();
      setAddingChild(false);
      setChildCode("");
      setChildName("");
      setExpanded(true);
      offerUndo(t("wbs.created"), async () => {
        await deleteWBSNode(projectId, created.wbs_id);
      });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteWBSNode(projectId, node.wbs_id),
    onSuccess: () => {
      const snapshot = {
        parent_id: parentId,
        wbs_code: node.wbs_code,
        wbs_name: node.wbs_name,
        weight_physical: parseWeight(node.weight_physical),
        weight_financial: parseWeight(node.weight_financial),
        description: node.description ?? "",
      };
      invalidate();
      offerUndo(t("wbs.deleted"), async () => {
        try {
          await createWBSNode(projectId, {
            parent_id: snapshot.parent_id,
            wbs_code: snapshot.wbs_code,
            wbs_name: snapshot.wbs_name,
            weight_physical: snapshot.weight_physical,
            weight_financial: snapshot.weight_financial,
            description: snapshot.description,
          });
        } catch {
          // Codes may have been renumbered after delete; recreate with a temp code.
          await createWBSNode(projectId, {
            parent_id: snapshot.parent_id,
            wbs_code: uniqueTempCode(),
            wbs_name: snapshot.wbs_name,
            weight_physical: snapshot.weight_physical,
            weight_financial: snapshot.weight_financial,
            description: snapshot.description,
          });
        }
      });
    },
    onError: (e: Error) => {
      const msg = e.message;
      if (msg.includes("wbs_has_cost") || msg.includes("cost records")) {
        toast.error(t("wbs.deleteHasCost"));
      } else if (msg.includes("wbs_has_progress") || msg.includes("progress recorded")) {
        toast.error(t("wbs.deleteHasProgress"));
      } else if (msg.includes("wbs_has_documents") || msg.includes("documents")) {
        toast.error(t("wbs.deleteHasDocuments"));
      } else if (msg.includes("activities attached") || msg.includes("wbs_has_activities")) {
        toast.error(t("wbs.deleteHasActivities"));
      } else if (msg.includes("has children") || msg.includes("wbs_has_children")) {
        toast.error(t("wbs.deleteHasChildren"));
      } else {
        toast.error(msg);
      }
    },
  });

  const weightPct =
    node.weight_physical != null
      ? Math.round(Number(node.weight_physical) * 100)
      : null;

  const childrenWeightSum = node.children.reduce(
    (sum, c) => sum + (c.weight_physical ? Number(c.weight_physical) : 0),
    0,
  );
  const weightWarning = hasChildren && Math.abs(childrenWeightSum - 1) > 0.01;

  return (
    <Collapsible open={expanded} onOpenChange={setExpanded} asChild>
      <div data-testid={`wbs-node-${node.wbs_code}`} data-wbs-id={node.wbs_id}>
        <div
        className="group flex flex-wrap items-center gap-2 border-b border-border/50 py-2 pe-2"
        style={{ paddingInlineStart: indent + 8 }}
        data-testid={`wbs-row-${node.wbs_code}`}
        draggable={canEdit}
        onDragStart={(e) => {
          e.dataTransfer.setData("text/wbs-id", node.wbs_id);
          e.dataTransfer.setData("text/wbs-parent-id", parentId ?? "");
          e.dataTransfer.effectAllowed = "move";
        }}
        onDragOver={(e) => {
          if (!canEdit) return;
          e.preventDefault();
          e.dataTransfer.dropEffect = "move";
        }}
        onDrop={(e) => {
          if (!canEdit) return;
          e.preventDefault();
          const draggedId = e.dataTransfer.getData("text/wbs-id");
          const previousParentId = e.dataTransfer.getData("text/wbs-parent-id") || null;
          if (!draggedId || draggedId === node.wbs_id) return;
          void moveWBSNode(projectId, draggedId, {
            new_parent_id: node.wbs_id,
            position: "sorted_child",
          })
            .then(() => {
              invalidate();
              offerUndo(t("wbs.moved"), async () => {
                if (previousParentId) {
                  await moveWBSNode(projectId, draggedId, {
                    new_parent_id: previousParentId,
                    position: "sorted_child",
                  });
                } else {
                  // Root move undo is not supported without a root-target API.
                  throw new Error(t("wbs.moveUndoRootUnsupported"));
                }
              });
            })
            .catch((err: Error) => toast.error(err.message));
        }}
        >
          {hasChildren ? (
            <CollapsibleTrigger asChild>
              <button
                type="button"
                className="rounded-sm text-muted-foreground hover:bg-muted/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 [&[data-state=open]>svg]:-rotate-90"
                aria-label={expanded ? t("wbs.collapse") : t("wbs.expand")}
              >
                <ChevronLeft className="size-4 transition-transform duration-200" />
              </button>
            </CollapsibleTrigger>
          ) : (
            <span className="w-4" />
          )}

          <span className="text-xs text-muted-foreground">{node.wbs_code}</span>

        {editing && canEdit ? (
          <div className="flex flex-wrap items-center gap-2">
            <Input
              className="h-8 max-w-xs"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
            <select
              className="h-8 rounded border px-2 text-sm"
              value={status}
              onChange={(e) =>
                setStatus(e.target.value as "draft" | "active" | "completed" | "on_hold")
              }
              aria-label={t("wbs.status")}
            >
              <option value="draft">{t("wbs.statusDraft")}</option>
              <option value="active">{t("wbs.statusActive")}</option>
              <option value="completed">{t("wbs.statusCompleted")}</option>
              <option value="on_hold">{t("wbs.statusOnHold")}</option>
            </select>
            <select
              className="h-8 max-w-[12rem] rounded border px-2 text-sm"
              value={responsible}
              onChange={(e) => setResponsible(e.target.value)}
              aria-label={t("wbs.responsible")}
              data-testid={`wbs-responsible-select-${node.wbs_code}`}
            >
              <option value="">{t("wbs.responsibleNone")}</option>
              {activeMembers.map((m) => (
                <option key={m.user_id!} value={m.user_id!}>
                  {m.full_name || m.email || m.user_id}
                </option>
              ))}
            </select>
            <Input
              className="h-8 max-w-sm"
              value={acceptance}
              onChange={(e) => setAcceptance(e.target.value)}
              placeholder={t("wbs.acceptanceCriteria")}
              aria-label={t("wbs.acceptanceCriteria")}
            />
            <Button
              size="sm"
              variant="primary"
              loading={updateMutation.isPending}
              onClick={() => {
                updateMutation.mutate({
                  wbs_name: name.trim() || node.wbs_name,
                  responsible: responsible || null,
                  acceptance_criteria: acceptance,
                  status,
                });
              }}
            >
              {t("wbs.save")}
            </Button>
            <Button
              size="sm"
              variant="secondary"
              onClick={() => {
                setEditing(false);
                setName(node.wbs_name);
                setAcceptance(node.acceptance_criteria ?? "");
                setResponsible(node.responsible ?? "");
                setStatus(node.status ?? "active");
              }}
            >
              {t("wbs.cancel")}
            </Button>
          </div>
        ) : (
          <div
            className="flex min-w-0 flex-wrap items-baseline gap-x-3 gap-y-0.5"
            onDoubleClick={canEdit ? () => setEditing(true) : undefined}
          >
            <span className="font-medium">
              {node.wbs_name}
              {node.status && node.status !== "active" ? (
                <span className="ms-2 text-xs text-muted-foreground">({node.status})</span>
              ) : null}
            </span>
            {responsibleLabel ? (
              <span
                className="text-xs text-muted-foreground"
                data-testid={`wbs-responsible-view-${node.wbs_code}`}
              >
                {t("wbs.responsible")}: {responsibleLabel}
              </span>
            ) : null}
            {(node.acceptance_criteria ?? "").trim() ? (
              <span
                className="max-w-md truncate text-xs text-muted-foreground"
                title={node.acceptance_criteria}
                data-testid={`wbs-acceptance-view-${node.wbs_code}`}
              >
                {t("wbs.acceptanceCriteria")}: {node.acceptance_criteria}
              </span>
            ) : null}
          </div>
        )}

        {canEdit ? (
          <button
            type="button"
            className="rounded-sm opacity-0 hover:bg-muted/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 focus-visible:opacity-100 group-hover:opacity-100 group-focus-within:opacity-100"
            onClick={() => setEditing(true)}
            aria-label={t("wbs.edit")}
          >
            <Pencil className="size-3.5 text-muted-foreground" />
          </button>
        ) : null}

        {weightPct != null && (
          <span className="text-xs text-muted-foreground">{weightPct}%</span>
        )}

        {weightWarning && (
          <span
            className="text-xs text-warning-600"
            title={t("wbs.weightWarning")}
          >
            ⚠
          </span>
        )}

        {canEdit ? (
          <div className="ms-auto flex gap-1 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon-sm"
                  onClick={() => {
                    setChildCode(defaultChildCode);
                    setAddingChild(true);
                  }}
                  aria-label={t("wbs.addChild")}
                >
                  <Plus className="size-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>{t("wbs.addChild")}</TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon-sm"
                  disabled={hasChildren}
                  aria-label={
                    hasChildren ? t("wbs.deleteDisabled") : t("wbs.delete")
                  }
                  onClick={() => deleteMutation.mutate()}
                >
                  <Trash2 className="size-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                {hasChildren ? t("wbs.deleteDisabled") : t("wbs.delete")}
              </TooltipContent>
            </Tooltip>
          </div>
          ) : null}
        </div>

        <CollapsibleContent>
          {canEdit && addingChild && (
            <div
              className="flex flex-wrap gap-2 py-2"
              style={{ paddingInlineStart: indent + 32 }}
            >
              <Input
                placeholder={t("wbs.code")}
                value={childCode || defaultChildCode}
                disabled
                className="h-8 w-24"
              />
              <Input
                placeholder={t("wbs.name")}
                value={childName}
                onChange={(e) => setChildName(e.target.value)}
                className="h-8 max-w-xs"
              />
              <Button
                size="sm"
                variant="primary"
                loading={createMutation.isPending}
                onClick={() => createMutation.mutate()}
              >
                {t("wbs.save")}
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setAddingChild(false)}
              >
                {t("wbs.cancel")}
              </Button>
            </div>
          )}

          {node.children.map((child) => (
            <WBSNodeRow
              key={child.wbs_id}
              node={child}
              projectId={projectId}
              parentId={node.wbs_id}
              depth={depth + 1}
              canEdit={canEdit}
            />
          ))}
        </CollapsibleContent>
      </div>
    </Collapsible>
  );
}
