import {
  Background,
  Controls,
  MarkerType,
  ReactFlow,
  type Edge,
  type Node,
  type NodeProps,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import dagre from "@dagrejs/dagre";
import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  fetchActivityNetwork,
  type ActivityStatus,
} from "@/app/lib/api/activities";
import { LoadingSkeleton } from "@/components/layout/page-header";
import { cn } from "@/app/lib/utils";

const STATUS_COLORS: Record<ActivityStatus, string> = {
  not_started: "border-neutral-300 bg-neutral-50 dark:border-neutral-600 dark:bg-neutral-900",
  in_progress: "border-info-400 bg-info-50 dark:border-info-600 dark:bg-info-950/40",
  suspended: "border-warning-400 bg-warning-50 dark:border-warning-600 dark:bg-warning-950/40",
  completed: "border-success-400 bg-success-50 dark:border-success-600 dark:bg-success-950/40",
};

type ActivityNodeData = {
  code: string;
  name: string;
  status: ActivityStatus;
  planned_start: string | null;
  planned_finish: string | null;
  is_critical: boolean;
};

function ActivityNodeCard({ data }: NodeProps<Node<ActivityNodeData>>) {
  return (
    <div
      className={cn(
        "min-w-[160px] max-w-[200px] rounded-lg border-2 px-3 py-2 text-xs shadow-sm",
        STATUS_COLORS[data.status],
        data.is_critical && "border-danger-600 ring-2 ring-danger-400/50",
      )}
    >
      <div className="font-mono font-semibold">{data.code}</div>
      <div className="truncate text-muted-foreground">{data.name}</div>
      <div className="mt-1 text-[10px] text-muted-foreground">
        {data.planned_start ?? "—"} → {data.planned_finish ?? "—"}
      </div>
    </div>
  );
}

const nodeTypes = { activity: ActivityNodeCard };

function layoutGraph(
  nodes: { id: string; code: string; name: string; status: ActivityStatus; planned_start: string | null; planned_finish: string | null; is_critical: boolean }[],
  edges: { from: string; to: string; relation_type: string; lag_days: number }[],
) {
  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: "LR", nodesep: 40, ranksep: 60 });

  for (const n of nodes) {
    g.setNode(n.id, { width: 180, height: 72 });
  }
  for (const e of edges) {
    g.setEdge(e.from, e.to);
  }
  dagre.layout(g);

  const flowNodes: Node<ActivityNodeData>[] = nodes.map((n) => {
    const pos = g.node(n.id);
    return {
      id: n.id,
      type: "activity",
      position: { x: pos.x - 90, y: pos.y - 36 },
      data: {
        code: n.code,
        name: n.name,
        status: n.status,
        planned_start: n.planned_start,
        planned_finish: n.planned_finish,
        is_critical: n.is_critical,
      },
    };
  });

  const flowEdges: Edge[] = edges.map((e, i) => ({
    id: `e-${i}`,
    source: e.from,
    target: e.to,
    label: e.lag_days !== 0 ? `${e.relation_type} (${e.lag_days})` : e.relation_type,
    markerEnd: { type: MarkerType.ArrowClosed },
    style: { strokeWidth: 1.5 },
  }));

  return { flowNodes, flowEdges };
}

export interface NetworkDiagramViewProps {
  projectId: string;
  onNodeClick: (activityId: string) => void;
}

export function NetworkDiagramView({ projectId, onNodeClick }: NetworkDiagramViewProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["activity-network", projectId],
    queryFn: () => fetchActivityNetwork(projectId),
  });

  const { flowNodes, flowEdges } = useMemo(() => {
    if (!data) return { flowNodes: [], flowEdges: [] };
    return layoutGraph(data.nodes, data.edges);
  }, [data]);

  if (isLoading) return <LoadingSkeleton rows={8} />;

  if (!data?.nodes.length) {
    return (
      <div className="flex min-h-[320px] items-center justify-center rounded-lg border border-dashed border-border text-sm text-muted-foreground">
        فعالیتی برای نمایش شبکه وجود ندارد.
      </div>
    );
  }

  return (
    <div className="h-[min(70vh,640px)] w-full rounded-lg border border-border" dir="ltr">
      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        nodeTypes={nodeTypes}
        fitView
        onNodeClick={(_, node) => onNodeClick(node.id)}
        proOptions={{ hideAttribution: true }}
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
