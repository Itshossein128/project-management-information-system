import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ChevronDown, ChevronLeft, Pencil, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  createWBSNode,
  deleteWBSNode,
  updateWBSNode,
  type WBSNode,
} from "@/app/lib/api/wbs";
import { Button } from "@/components/ui/sprint-button";
import { Input } from "@/components/form";
import { useToast } from "@/components/ui/toast";

const INDENT_PX = 24;

interface WBSNodeRowProps {
  node: WBSNode;
  projectId: string;
  depth?: number;
  canEdit?: boolean;
}

export function WBSNodeRow({
  node,
  projectId,
  depth = 0,
  canEdit = true,
}: WBSNodeRowProps) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const [expanded, setExpanded] = useState(true);
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(node.wbs_name);
  const [addingChild, setAddingChild] = useState(false);
  const [childCode, setChildCode] = useState("");
  const [childName, setChildName] = useState("");

  const hasChildren = node.children.length > 0;
  const level = node.depth > 0 ? node.depth - 1 : depth;
  const indent = level * INDENT_PX;

  const invalidate = () => void qc.invalidateQueries({ queryKey: ["wbs", projectId] });

  const updateMutation = useMutation({
    mutationFn: (payload: { wbs_name?: string; weight_physical?: number | null }) =>
      updateWBSNode(projectId, node.wbs_id, payload),
    onSuccess: () => { invalidate(); setEditing(false); },
    onError: (e: Error) => toast.error(e.message),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createWBSNode(projectId, { parent_id: node.wbs_id, wbs_code: childCode, wbs_name: childName }),
    onSuccess: () => {
      invalidate();
      setAddingChild(false);
      setChildCode("");
      setChildName("");
      setExpanded(true);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteWBSNode(projectId, node.wbs_id),
    onSuccess: invalidate,
    onError: (e: Error) => toast.error(e.message),
  });

  const weightPct =
    node.weight_physical != null ? Math.round(Number(node.weight_physical) * 100) : null;

  const childrenWeightSum = node.children.reduce(
    (sum, c) => sum + (c.weight_physical ? Number(c.weight_physical) : 0),
    0,
  );
  const weightWarning = hasChildren && Math.abs(childrenWeightSum - 1) > 0.01;

  return (
    <div>
      <div
        className="group flex flex-wrap items-center gap-2 border-b border-border/50 py-2 pe-2"
        style={{ paddingInlineStart: indent + 8 }}
      >
        {hasChildren ? (
          <button
            type="button"
            onClick={() => setExpanded(!expanded)}
            className="text-muted-foreground"
            aria-label={expanded ? t("wbs.collapse") : t("wbs.expand")}
          >
            {expanded ? <ChevronDown className="size-4" /> : <ChevronLeft className="size-4" />}
          </button>
        ) : (
          <span className="w-4" />
        )}

        <span className="text-xs text-muted-foreground">{node.wbs_code}</span>

        {editing && canEdit ? (
          <Input
            className="h-8 max-w-xs"
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") updateMutation.mutate({ wbs_name: name });
              if (e.key === "Escape") { setEditing(false); setName(node.wbs_name); }
            }}
            onBlur={() => updateMutation.mutate({ wbs_name: name })}
            autoFocus
          />
        ) : (
          <span
            className="font-medium"
            onDoubleClick={canEdit ? () => setEditing(true) : undefined}
          >
            {node.wbs_name}
          </span>
        )}

        {canEdit ? (
          <button
            type="button"
            className="opacity-0 group-hover:opacity-100"
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
          <span className="text-xs text-amber-600" title={t("wbs.weightWarning")}>⚠</span>
        )}

        {canEdit ? (
          <div className="ms-auto flex gap-1 opacity-0 group-hover:opacity-100">
            <Button variant="ghost" size="icon-sm" onClick={() => setAddingChild(true)} title={t("wbs.addChild")}>
              <Plus className="size-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon-sm"
              disabled={hasChildren}
              title={hasChildren ? t("wbs.deleteDisabled") : t("wbs.delete")}
              onClick={() => deleteMutation.mutate()}
            >
              <Trash2 className="size-4" />
            </Button>
          </div>
        ) : null}
      </div>

      {canEdit && addingChild && (
        <div className="flex flex-wrap gap-2 py-2" style={{ paddingInlineStart: indent + 32 }}>
          <Input placeholder={t("wbs.code")} value={childCode} onChange={(e) => setChildCode(e.target.value)} className="h-8 w-24" />
          <Input placeholder={t("wbs.name")} value={childName} onChange={(e) => setChildName(e.target.value)} className="h-8 max-w-xs" />
          <Button size="sm" variant="primary" loading={createMutation.isPending} onClick={() => createMutation.mutate()}>
            {t("wbs.save")}
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setAddingChild(false)}>{t("wbs.cancel")}</Button>
        </div>
      )}

      {expanded &&
        node.children.map((child) => (
          <WBSNodeRow
            key={child.wbs_id}
            node={child}
            projectId={projectId}
            depth={depth + 1}
            canEdit={canEdit}
          />
        ))}
    </div>
  );
}
