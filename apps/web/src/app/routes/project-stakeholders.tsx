import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router";
import {
  ProjectProvider,
  usePermission,
  useProject,
} from "@/app/contexts/project-context";
import {
  asList,
  createStakeholder,
  fetchStakeholders,
} from "@/app/lib/api/central-data";
import { PATHS } from "@/app/routeVars";
import { Input, Label } from "@/components/form";
import { AccessDenied, NotFoundState } from "@/components/layout/empty-state";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

function StakeholdersContent() {
  const { t } = useTranslation();
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_project");
  const canEdit = has("edit_project");
  const toast = useToast();
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const [org, setOrg] = useState("");
  const [influence, setInfluence] = useState("");

  const { data, isLoading: listLoading } = useQuery({
    queryKey: ["stakeholders", projectId],
    queryFn: () => fetchStakeholders(projectId),
    enabled: canView && Boolean(projectId),
  });

  const create = useMutation({
    mutationFn: () =>
      createStakeholder(projectId, {
        name,
        organization_name: org,
        influence: influence ? Number(influence) : null,
      }),
    onSuccess: () => {
      toast.success(t("centralData.stakeholderCreated", "ذینفع ثبت شد"));
      setName("");
      setOrg("");
      setInfluence("");
      void qc.invalidateQueries({ queryKey: ["stakeholders", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (isLoading || listLoading) return <LoadingSkeleton rows={8} />;
  if (!project) return <NotFoundState title={t("common.projectNotFound")} />;
  if (!canView) return <AccessDenied />;

  const rows = asList(data ?? []);

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("centralData.stakeholders", "ذینفعان")}
        subtitle={project.project_name}
      />
      <ul className="divide-y rounded border">
        {rows.map((s) => (
          <li key={s.id} className="flex justify-between px-3 py-2 text-sm">
            <span>
              {s.name}
              {s.organization_name ? ` — ${s.organization_name}` : ""}
            </span>
            <span className="text-muted-foreground">
              {s.influence != null ? `I=${s.influence}` : ""}
            </span>
          </li>
        ))}
        {rows.length === 0 ? (
          <li className="px-3 py-4 text-sm text-muted-foreground">
            {t("centralData.noStakeholders", "ذینفعی ثبت نشده است.")}
          </li>
        ) : null}
      </ul>
      {canEdit ? (
        <div className="grid max-w-xl gap-2">
          <Label>{t("centralData.name", "نام")}</Label>
          <Input value={name} onChange={(e) => setName(e.target.value)} />
          <Label>{t("centralData.organization", "سازمان")}</Label>
          <Input value={org} onChange={(e) => setOrg(e.target.value)} />
          <Label>{t("centralData.influence", "نفوذ (۱–۵)")}</Label>
          <Input
            value={influence}
            onChange={(e) => setInfluence(e.target.value)}
            inputMode="numeric"
          />
          <Button
            variant="primary"
            loading={create.isPending}
            disabled={!name}
            onClick={() => create.mutate()}
          >
            {t("common.add", "افزودن")}
          </Button>
        </div>
      ) : null}
    </div>
  );
}

export default function ProjectStakeholdersPage() {
  const { t } = useTranslation();
  const { projectId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto px-4 py-8">
        <Breadcrumb
          items={[
            { label: t("project.title"), href: `/${PATHS.PROJECT}` },
            {
              label: t("centralData.stakeholders", "ذینفعان"),
            },
          ]}
        />
        <StakeholdersContent />
      </main>
    </ProjectProvider>
  );
}
