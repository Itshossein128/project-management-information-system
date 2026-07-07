import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Lock, Trash2 } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  createProjectTemplate,
  deleteProjectTemplate,
  fetchProjectTemplates,
  projectTypeLabels,
  type ProjectType,
} from "@/app/lib/api/templates";
import { Breadcrumb, PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/sprint-button";
import { Input } from "@/components/form";
import { Label } from "@/components/ui/label";
import { Modal } from "@/components/overlay/modal";
import { useToast } from "@/components/ui/toast";

const PROJECT_TYPES: ProjectType[] = [
  "residential",
  "road",
  "commercial",
  "industrial",
  "epc",
  "other",
];

export default function SettingsTemplatesPage() {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const [createOpen, setCreateOpen] = useState(false);
  const [templateName, setTemplateName] = useState("");
  const [description, setDescription] = useState("");
  const [projectType, setProjectType] = useState<ProjectType>("other");

  const { data: templates = [], isLoading } = useQuery({
    queryKey: ["project-templates"],
    queryFn: () => fetchProjectTemplates(),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createProjectTemplate({
        template_name: templateName,
        description,
        project_type: projectType,
      }),
    onSuccess: () => {
      toast.success(t("templates.createSuccess"));
      setCreateOpen(false);
      setTemplateName("");
      setDescription("");
      setProjectType("other");
      void qc.invalidateQueries({ queryKey: ["project-templates"] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteProjectTemplate(id),
    onSuccess: () => {
      toast.success(t("templates.deleteSuccess"));
      void qc.invalidateQueries({ queryKey: ["project-templates"] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <main className="page-main page-shell mx-auto max-w-4xl px-4 py-8">
      <Breadcrumb
        items={[
          { label: t("templates.settings") },
          { label: t("templates.title") },
        ]}
      />
      <PageHeader
        title={t("templates.title")}
        subtitle={t("templates.subtitle")}
        actions={
          <Button variant="primary" onClick={() => setCreateOpen(true)}>
            {t("templates.new")}
          </Button>
        }
      />

      {isLoading ? (
        <p className="text-muted-foreground">{t("templates.loading")}</p>
      ) : (
        <ul className="divide-y divide-border rounded-lg border border-border">
          {templates.map((tpl) => (
            <li
              key={tpl.template_id}
              className="flex flex-wrap items-center justify-between gap-3 px-4 py-3"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  {tpl.is_system ? (
                    <Lock className="size-4 text-muted-foreground" aria-label={t("templates.systemTemplate")} />
                  ) : null}
                  <span className="font-medium">{tpl.template_name}</span>
                  <Badge variant="info" label={projectTypeLabels[tpl.project_type]} />
                </div>
                {tpl.description ? (
                  <p className="mt-1 text-sm text-muted-foreground">{tpl.description}</p>
                ) : null}
                <p className="mt-1 text-xs text-muted-foreground">
                  {t("templates.wbsNodes", { count: tpl.wbs_node_count })}
                  {tpl.is_system ? ` · ${t("templates.systemTemplate")}` : ""}
                </p>
              </div>
              {!tpl.is_system ? (
                <Button
                  variant="ghost"
                  size="icon-sm"
                  title={t("templates.delete")}
                  onClick={() => deleteMutation.mutate(tpl.template_id)}
                  disabled={deleteMutation.isPending}
                >
                  <Trash2 className="size-4 text-destructive" />
                </Button>
              ) : null}
            </li>
          ))}
        </ul>
      )}

      <Modal
        open={createOpen}
        onOpenChange={setCreateOpen}
        title={t("templates.createTitle")}
        idBase="createTemplate"
        className="max-w-lg"
      >
        <div className="space-y-4">
          <div>
            <Label>{t("templates.templateName")} *</Label>
            <Input value={templateName} onChange={(e) => setTemplateName(e.target.value)} />
          </div>
          <div>
            <Label>{t("templates.description")}</Label>
            <Input value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
          <div>
            <Label>{t("templates.projectType")}</Label>
            <select
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
              value={projectType}
              onChange={(e) => setProjectType(e.target.value as ProjectType)}
            >
              {PROJECT_TYPES.map((pt) => (
                <option key={pt} value={pt}>
                  {projectTypeLabels[pt]}
                </option>
              ))}
            </select>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setCreateOpen(false)}>
              {t("common.cancel")}
            </Button>
            <Button
              variant="primary"
              loading={createMutation.isPending}
              disabled={!templateName.trim()}
              onClick={() => createMutation.mutate()}
            >
              {t("templates.create")}
            </Button>
          </div>
        </div>
      </Modal>
    </main>
  );
}
