import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, ChevronLeft, Pencil, Plus, Trash2, User } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { ApiRequestError } from "@/app/lib/api-client";
import { fetchMembers } from "@/app/lib/api/members";
import {
  createWBSNode,
  deleteWBSNode,
  moveWBSNode,
  updateWBSNode,
  type WBSNode,
} from "@/app/lib/api/wbs";
import { Button } from "@/components/ui/sprint-button";
import { Field, Input, Select, TextArea } from "@/components/form";
import { useToast } from "@/components/ui/toast";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from "@/components/ui/collapsible";

const INDENT_PX = 24;
const UNDO_DURATION_MS = 10_000;

// Tailwind utility classes for consistent spacing and hover states
const rowClasses =
  "group flex min-h-12 items-center gap-3 py-2 transition-colors hover:bg-muted/60 focus-within:bg-muted/60";
// Hidden until hover/focus on pointer devices; always visible on touch devices.
const revealClasses =
  "opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100 focus-visible:opacity-100 [@media(hover:none)]:opacity-100";
const NO_RESPONSIBLE = "__none__";
const STATUS_STYLES: Record<string, string> = {
  draft: "bg-muted text-muted-foreground",
  completed: "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300",
  on_hold: "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300",
};
const STATUS_KEYS: Record<string, string> = {
  draft: "wbs.statusDraft",
  active: "wbs.statusActive",
  completed: "wbs.statusCompleted",
  on_hold: "wbs.statusOnHold",
};
const indentStyle = (depth: number) => ({ paddingLeft: `${depth * INDENT_PX}px` });

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
  const [description, setDescription] = useState(node.description ?? "");
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
      description?: string;
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
    onError: (e: Error) => toast.error(
      e instanceof ApiRequestError && e.code === "duplicate_wbs_code"
        ? t("wbs.duplicateCode") : e.message,
    ),
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
      <div role="treeitem" aria-expanded={hasChildren ? expanded : undefined} aria-level={depth + 1} tabIndex={0} onKeyDown={(e) => { if (e.target === e.currentTarget && (e.key === "Enter" || e.key === " ")) setExpanded(!expanded); }} data-testid={`wbs-node-${node.wbs_code}`} data-wbs-id={node.wbs_id}>
        <div
        className={`${rowClasses} border-b border-border/50 pe-2 ${editing ? "items-start" : ""}`}
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
                className="inline-flex size-6 items-center justify-center rounded-md text-muted-foreground hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring [&[data-state=open]>svg]:-rotate-90"
                aria-label={expanded ? t("wbs.collapse") : t("wbs.expand")}
              >
                <ChevronLeft className="size-4 transition-transform duration-200" />
              </button>
            </CollapsibleTrigger>
          ) : (
            <span className="inline-block size-6" aria-hidden="true" />
          )}

          <span
            dir="ltr"
            className="shrink-0 rounded-md bg-muted px-1.5 py-0.5 font-mono text-xs tabular-nums text-muted-foreground"
          >
            {node.wbs_code}
          </span>

        {editing && canEdit ? (
          <div
            className="grid min-w-0 flex-1 gap-4 rounded-xl border border-border bg-card p-4 shadow-sm sm:grid-cols-2 lg:grid-cols-4"
            data-testid={`wbs-edit-form-${node.wbs_code}`}
          >
            <Field
              name={`wbs-name-${node.wbs_id}`}
              label={t("wbs.name")}
              htmlFor={`wbs-name-input-${node.wbs_id}`}
              className="lg:col-span-2"
            >
              {() => (
                <Input
                  id={`wbs-name-input-${node.wbs_id}`}
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  autoFocus
                />
              )}
            </Field>
            <Select
              name={`wbs-status-${node.wbs_id}`}
              label={t("wbs.status")}
              aria-label={t("wbs.status")}
              value={status}
              onChange={(e) =>
                setStatus(e.target.value as "draft" | "active" | "completed" | "on_hold")
              }
              options={[
                { value: "draft", label: t("wbs.statusDraft") },
                { value: "active", label: t("wbs.statusActive") },
                { value: "completed", label: t("wbs.statusCompleted") },
                { value: "on_hold", label: t("wbs.statusOnHold") },
              ]}
            />
            <div data-testid={`wbs-responsible-select-${node.wbs_code}`} className="min-w-0">
              <Select
                name={`wbs-responsible-${node.wbs_id}`}
                label={t("wbs.responsible")}
                aria-label={t("wbs.responsible")}
                value={responsible || NO_RESPONSIBLE}
                onChange={(e) =>
                  setResponsible(e.target.value === NO_RESPONSIBLE ? "" : e.target.value)
                }
                options={[
                  { value: NO_RESPONSIBLE, label: t("wbs.responsibleNone") },
                  ...activeMembers.map((m) => ({
                    value: m.user_id!,
                    label: m.full_name || m.email || m.user_id!,
                  })),
                ]}
              />
            </div>
            <TextArea
              name={`wbs-description-field-${node.wbs_id}`}
              label={t("wbs.description")}
              fieldClassName="sm:col-span-2"
              className="min-h-20 resize-y"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              data-testid={`wbs-description-${node.wbs_code}`}
            />
            <TextArea
              name={`wbs-acceptance-field-${node.wbs_id}`}
              label={t("wbs.acceptanceCriteria")}
              fieldClassName="sm:col-span-2"
              className="min-h-20 resize-y"
              value={acceptance}
              onChange={(e) => setAcceptance(e.target.value)}
            />
            <div className="flex items-center justify-end gap-2 border-t border-border pt-3 sm:col-span-2 lg:col-span-4">
              <Button
                size="sm"
                variant="secondary"
                onClick={() => {
                  setEditing(false);
                  setName(node.wbs_name);
                  setDescription(node.description ?? "");
                  setAcceptance(node.acceptance_criteria ?? "");
                  setResponsible(node.responsible ?? "");
                  setStatus(node.status ?? "active");
                }}
              >
                {t("wbs.cancel")}
              </Button>
              <Button
                size="sm"
                variant="primary"
                loading={updateMutation.isPending}
                onClick={() => {
                  updateMutation.mutate({
                    wbs_name: name.trim() || node.wbs_name,
                    description,
                    responsible: responsible || null,
                    acceptance_criteria: acceptance,
                    status,
                  });
                }}
              >
                {t("wbs.save")}
              </Button>
            </div>
          </div>
        ) : (
          <div
            className="flex min-w-0 flex-wrap items-baseline gap-x-3 gap-y-0.5"
            onDoubleClick={canEdit ? () => setEditing(true) : undefined}
          >
            <span className={depth === 0 ? "font-semibold" : "font-medium"}>
              {node.wbs_name}
            </span>
            {node.status && node.status !== "active" ? (
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_STYLES[node.status] ?? "bg-muted text-muted-foreground"}`}
              >
                {STATUS_KEYS[node.status] ? t(STATUS_KEYS[node.status]) : node.status}
              </span>
            ) : null}
            {(node.description ?? "").trim() ? (
              <span
                className="max-w-md truncate text-xs text-muted-foreground"
                title={node.description}
                data-testid={`wbs-description-view-${node.wbs_code}`}
              >
                {t("wbs.description")}: {node.description}
              </span>
            ) : null}
            {responsibleLabel ? (
              <span
                className="inline-flex items-center gap-1 rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground"
                title={t("wbs.responsible")}
                data-testid={`wbs-responsible-view-${node.wbs_code}`}
              >
                <User className="size-3" aria-hidden="true" />
                <span className="sr-only">{t("wbs.responsible")}: </span>
                {responsibleLabel}
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

        {canEdit && !editing ? (
          <button
            type="button"
            className={`inline-flex size-7 items-center justify-center rounded-md hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${revealClasses}`}
            onClick={() => setEditing(true)}
            aria-label={t("wbs.edit")}
          >
            <Pencil className="size-3.5 text-muted-foreground" />
          </button>
        ) : null}

        {!editing ? (
        <div className="ms-auto flex shrink-0 items-center gap-3">
          {weightWarning && (
            <span
              className="text-amber-600"
              title={t("wbs.weightWarning")}
              role="img"
              aria-label={t("wbs.weightWarning")}
            >
              <AlertTriangle className="size-4" />
            </span>
          )}
          {weightPct != null && (
            <span
              className="flex w-24 items-center gap-2"
              title={`${weightPct}%`}
            >
              <span className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
                <span
                  className="block h-full rounded-full bg-primary"
                  style={{ width: `${Math.min(100, weightPct)}%` }}
                />
              </span>
              <span className="w-9 text-end text-xs tabular-nums text-muted-foreground">
                {weightPct}%
              </span>
            </span>
          )}

        {canEdit ? (
          <div className={`flex gap-1 ${revealClasses}`}>
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
