import { useTranslation } from "react-i18next";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router";
import { useMemo, useState } from "react";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import { fetchWBSTree, type WBSNode } from "@/app/lib/api/wbs";
import { PATHS } from "@/app/routeVars";
import { WBSNodeRow } from "@/components/wbs/wbs-node";
import { WbsEmptyState } from "@/components/wbs/wbs-empty-state";
import { WbsPackageMetaWarning } from "@/components/wbs/wbs-package-meta-warning";
import { MspImportWizard } from "@/components/wbs/msp-import-wizard";
import { SaveAsTemplateModal } from "@/components/templates/save-as-template-modal";
import { EmptyState } from "@/components/layout/empty-state";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Button } from "@/components/ui/sprint-button";

function collectLeafPackages(nodes: WBSNode[]): WBSNode[] {
  return nodes.flatMap((n) =>
    n.children.length === 0 ? [n] : collectLeafPackages(n.children),
  );
}

function ProjectWBSContent() {
  const { t } = useTranslation();

  const { projectId, project, isLoading: projectLoading, isError: projectError, error: projectErr, refetch: refetchProject } = useProject();
  const { has } = usePermission(projectId);
  const canEditWBS = has("edit_wbs") && project?.status !== "archived";
  const qc = useQueryClient();
  const [mspOpen, setMspOpen] = useState(false);
  const [saveTemplateOpen, setSaveTemplateOpen] = useState(false);

  const { data: tree = [], isLoading, isError, error, refetch } = useQuery({
    queryKey: ["wbs", projectId],
    queryFn: () => fetchWBSTree(projectId),
    enabled: Boolean(project),
  });

  const leafPackages = useMemo(() => collectLeafPackages(tree), [tree]);

  if (projectLoading) return <LoadingSkeleton rows={10} />;
  if (projectError) return <QueryErrorState error={projectErr} onRetry={refetchProject} />;

  return (
    <>
      <Breadcrumb
        items={[
          { label: t("nav.sidebarProjects"), href: `/${PATHS.PROJECT}` },
          {
            label: project?.project_name ?? t("nav.projectOverview"),
            href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_OVERVIEW}`,
          },
          { label: "WBS" },
        ]}
      />
      <PageHeader
        title={t("pages.wbs.title")}
        subtitle={!canEditWBS ? t("common.readOnly") : undefined}
        actions={
          canEditWBS ? (
            <div className='flex flex-wrap gap-2'>
              <Button
                variant='secondary'
                onClick={() => setSaveTemplateOpen(true)}
              >
                {t("wbs.saveAsTemplate")}
              </Button>
              <Button
                variant='secondary'
                onClick={() => setMspOpen(true)}
                data-testid="msp-import-btn"
              >
                {t("wbs.importFromMsp")}
              </Button>
            </div>
          ) : undefined
        }
      />

      {isLoading ? (
        <LoadingSkeleton rows={10} />
      ) : isError ? (
        <QueryErrorState error={error} onRetry={() => void refetch()} />
      ) : tree.length === 0 ? (
        canEditWBS ? (
          <>
            <p className="mb-3 text-sm text-muted-foreground" data-testid="wbs-empty-warning">
              {t("wbs.emptyWarning")}
            </p>
            <WbsEmptyState
              projectId={projectId}
              onCreated={() =>
                void qc.invalidateQueries({ queryKey: ["wbs", projectId] })
              }
            />
          </>
        ) : (
          <EmptyState
            title={t("pages.wbs.empty")}
            description={t("wbs.readOnlyEmptyDescription")}
          />
        )
      ) : (
        <div className="space-y-3">
          <WbsPackageMetaWarning nodes={leafPackages} />
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
  const { t, i18n } = useTranslation();
  const { projectId } = useProjectParams();

  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <ProjectWBSContent />
      </ProjectProvider>
    </main>
  );
}
