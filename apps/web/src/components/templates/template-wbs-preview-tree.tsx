import { ChevronDown, ChevronLeft } from "lucide-react";
import { useState } from "react";

interface PreviewNode {
  wbs_code: string;
  wbs_name: string;
  children?: PreviewNode[];
  activities?: { activity_code: string; activity_name: string }[];
}

interface TemplateWBSPreviewTreeProps {
  nodes: PreviewNode[];
  /** Indent in px per level (default 24). */
  indentPx?: number;
}

function PreviewRow({
  node,
  depth,
  indentPx,
}: {
  node: PreviewNode;
  depth: number;
  indentPx: number;
}) {
  const [expanded, setExpanded] = useState(depth < 2);
  const hasChildren = (node.children?.length ?? 0) > 0;
  const activityCount = node.activities?.length ?? 0;

  return (
    <div>
      <div
        className="flex items-center gap-2 border-b border-border/40 py-1.5 text-sm"
        style={{ paddingInlineStart: depth * indentPx + 8 }}
      >
        {hasChildren ? (
          <button
            type="button"
            className="text-muted-foreground"
            onClick={() => setExpanded(!expanded)}
            aria-expanded={expanded}
          >
            {expanded ? <ChevronDown className="size-3.5" /> : <ChevronLeft className="size-3.5" />}
          </button>
        ) : (
          <span className="w-3.5" />
        )}
        <span className="text-xs text-muted-foreground">{node.wbs_code}</span>
        <span>{node.wbs_name}</span>
        {activityCount > 0 ? (
          <span className="text-xs text-muted-foreground">({activityCount} فعالیت)</span>
        ) : null}
      </div>
      {expanded &&
        node.children?.map((child) => (
          <PreviewRow key={child.wbs_code} node={child} depth={depth + 1} indentPx={indentPx} />
        ))}
    </div>
  );
}

export function TemplateWBSPreviewTree({ nodes, indentPx = 24 }: TemplateWBSPreviewTreeProps) {
  return (
    <div className="max-h-64 overflow-auto rounded-md border border-border">
      {nodes.map((node) => (
        <PreviewRow key={node.wbs_code} node={node} depth={0} indentPx={indentPx} />
      ))}
    </div>
  );
}
