import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router";
import { fetchWBSTree } from "@/app/lib/api/wbs";
import { PATHS } from "@/app/routeVars";
import { WBSNodeRow } from "@/components/wbs/wbs-node";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/sprint-button";

export default function ProjectWBSPage() {
  const { projectId = "" } = useParams();
  const { data: tree = [], isLoading } = useQuery({
    queryKey: ["wbs", projectId],
    queryFn: () => fetchWBSTree(projectId),
  });

  return (
    <main className="page-main page-shell mx-auto max-w-5xl px-4 py-8">
      <Breadcrumb
        items={[
          { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
          { label: "WBS" },
        ]}
      />
      <PageHeader
        title="ساختار شکست کار"
        actions={
          <Button variant="secondary" disabled title="در اسپرینت بعدی">
            بارگذاری از اکسل
          </Button>
        }
      />

      {isLoading ? (
        <LoadingSkeleton rows={10} />
      ) : tree.length === 0 ? (
        <p className="text-muted-foreground">هنوز گره WBS ایجاد نشده است.</p>
      ) : (
        <div className="rounded-lg border border-border">
          {tree.map((node) => (
            <WBSNodeRow key={node.wbs_id} node={node} projectId={projectId} />
          ))}
        </div>
      )}
    </main>
  );
}
