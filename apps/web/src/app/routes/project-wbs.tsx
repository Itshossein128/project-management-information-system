import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router";
import { useState } from "react";
import { ProjectProvider, usePermission } from "@/app/contexts/project-context";
import { fetchWBSTree } from "@/app/lib/api/wbs";
import { PATHS } from "@/app/routeVars";
import { WBSNodeRow } from "@/components/wbs/wbs-node";
import { WbsEmptyState } from "@/components/wbs/wbs-empty-state";
import { MspImportWizard } from "@/components/wbs/msp-import-wizard";
import { SaveAsTemplateModal } from "@/components/templates/save-as-template-modal";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { Button } from "@/components/ui/sprint-button";

function ProjectWBSContent() {
  const { projectId } = useProjectParams();
  const { has } = usePermission(projectId);
  const canEditWBS = has("edit_wbs");
  const qc = useQueryClient();
  const [mspOpen, setMspOpen] = useState(false);
  const [saveTemplateOpen, setSaveTemplateOpen] = useState(false);

  const { data: tree = [], isLoading } = useQuery({
    queryKey: ["wbs", projectId],
    queryFn: () => fetchWBSTree(projectId),
  });

  return (
    <>
      <Breadcrumb
        items={[
          { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
          { label: "WBS" },
        ]}
      />
      <PageHeader
        title='ساختار شکست کار'
        subtitle={!canEditWBS ? "نمایش فقط خواندنی" : undefined}
        actions={
          canEditWBS ? (
            <div className='flex flex-wrap gap-2'>
              <Button
                variant='secondary'
                onClick={() => setSaveTemplateOpen(true)}
              >
                ذخیره به‌عنوان قالب
              </Button>
              <Button variant='secondary' onClick={() => setMspOpen(true)}>
                بارگذاری از MSP
              </Button>
            </div>
          ) : undefined
        }
      />

      {isLoading ? (
        <LoadingSkeleton rows={10} />
      ) : tree.length === 0 ? (
        canEditWBS ? (
          <WbsEmptyState
            projectId={projectId}
            onCreated={() =>
              void qc.invalidateQueries({ queryKey: ["wbs", projectId] })
            }
          />
        ) : (
          <p className='text-muted-foreground'>هنوز گره WBS ایجاد نشده است.</p>
        )
      ) : (
        <div className='overflow-x-auto rounded-lg border border-border'>
          <div className='min-w-max'>
            {tree.map((node) => (
              <WBSNodeRow
                key={node.wbs_id}
                node={node}
                projectId={projectId}
                canEdit={canEditWBS}
              />
            ))}
          </div>
        </div>
      )}

      {canEditWBS ? (
        <>
          <MspImportWizard
            open={mspOpen}
            onOpenChange={setMspOpen}
            projectId={projectId}
            onComplete={() =>
              void qc.invalidateQueries({ queryKey: ["wbs", projectId] })
            }
          />
          <SaveAsTemplateModal
            open={saveTemplateOpen}
            onOpenChange={setSaveTemplateOpen}
            projectId={projectId}
          />
        </>
      ) : null}
    </>
  );
}

function useProjectParams() {
  const { projectId = "" } = useParams();
  return { projectId };
}

export default function ProjectWBSPage() {
  const { projectId } = useProjectParams();

  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <ProjectWBSContent />
      </ProjectProvider>
    </main>
  );
}
