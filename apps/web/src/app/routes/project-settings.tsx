import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import { useTranslation } from "react-i18next";
import { ProjectProvider, usePermission } from "@/app/contexts/project-context";
import {
  fetchProject,
  updateProject,
  type CreateProjectPayload,
} from "@/app/lib/api/projects";
import { PATHS } from "@/app/routeVars";
import { EmptyState } from "@/components/layout/empty-state";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Input, Label } from "@/components/form";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

function ProjectSettingsContent() {
  const { projectId } = useParams();
  const id = projectId ?? "";
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const { has } = usePermission(id);
  const canEdit = has("edit_project");

  const { data: project, isLoading, isError, refetch } = useQuery({
    queryKey: ["project", id],
    queryFn: () => fetchProject(id),
    enabled: Boolean(id),
  });

  const [form, setForm] = useState<Partial<CreateProjectPayload>>({});

  const saveMutation = useMutation({
    mutationFn: (payload: Partial<CreateProjectPayload>) =>
      updateProject(id, payload),
    onSuccess: () => {
      toast.success(t("projectSettings.saveSuccess", "تغییرات ذخیره شد"));
      void qc.invalidateQueries({ queryKey: ["project", id] });
      void qc.invalidateQueries({ queryKey: ["projects"] });
    },
    onError: (err: Error) => toast.error(err.message),
  });

  if (isLoading) {
    return <LoadingSkeleton rows={6} />;
  }
  if (isError) {
    return <QueryErrorState onRetry={() => void refetch()} />;
  }
  if (!project) {
    return <EmptyState title={t("common.projectNotFound")} />;
  }

  const values = {
    project_name: form.project_name ?? project.project_name,
    project_code: form.project_code ?? project.project_code,
    employer: form.employer ?? project.employer,
    contractor: form.contractor ?? project.contractor ?? "",
    consultant: form.consultant ?? project.consultant ?? "",
    location: form.location ?? project.location ?? "",
    contract_type: form.contract_type ?? project.contract_type ?? "",
    start_date: form.start_date ?? project.start_date ?? "",
    planned_finish_date:
      form.planned_finish_date ?? project.planned_finish_date ?? "",
    contract_amount:
      form.contract_amount ?? project.contract_amount ?? "",
  };

  const handleSubmit = (e: React.FormEvent) => {

    e.preventDefault();
    if (!canEdit) return;
    saveMutation.mutate({
      project_name: values.project_name,
      employer: values.employer,
      contractor: values.contractor || undefined,
      consultant: values.consultant || undefined,
      location: values.location || undefined,
      contract_type: values.contract_type || undefined,
      start_date: values.start_date || undefined,
      planned_finish_date: values.planned_finish_date || undefined,
      contract_amount: values.contract_amount || undefined,
    });
  };

  return (
    <>
      <Breadcrumb
        items={[
          { label: t("project.title", "پروژه‌ها"), href: `/${PATHS.PROJECT}` },
          {
            label: project.project_name,
            href: `/${PATHS.PROJECT}/${id}/${PATHS.PROJECT_OVERVIEW}`,
          },
          { label: t("projectSettings.title", "تنظیمات") },
        ]}
      />
      <PageHeader
        title={t("projectSettings.title", "تنظیمات پروژه")}
        subtitle={
          canEdit
            ? undefined
            : t("projectSettings.readOnly", "نمایش فقط خواندنی")
        }
      />

      <form onSubmit={handleSubmit} className='mx-auto max-w-2xl space-y-4'>
        <div>
          <Label htmlFor='input-projectName'>
            {t("projectSettings.projectName", "نام پروژه")}
          </Label>
          <Input
            id='input-projectName'
            value={values.project_name}
            disabled={!canEdit}
            onChange={(e) =>
              setForm((f) => ({ ...f, project_name: e.target.value }))
            }
            required
          />
        </div>
        <div>
          <Label htmlFor='input-projectCode'>
            {t("projectSettings.projectCode", "کد پروژه")}
          </Label>
          <Input
            id='input-projectCode'
            value={values.project_code}
            disabled
            readOnly
          />
        </div>
        <div>
          <Label htmlFor='input-employer'>
            {t("projectSettings.employer", "کارفرما")}
          </Label>
          <Input
            id='input-employer'
            value={values.employer}
            disabled={!canEdit}
            onChange={(e) =>
              setForm((f) => ({ ...f, employer: e.target.value }))
            }
            required
          />
        </div>
        <div>
          <Label htmlFor='input-contractor'>
            {t("projectSettings.contractor", "پیمانکار")}
          </Label>
          <Input
            id='input-contractor'
            value={values.contractor}
            disabled={!canEdit}
            onChange={(e) =>
              setForm((f) => ({ ...f, contractor: e.target.value }))
            }
          />
        </div>
        <div>
          <Label htmlFor='input-consultant'>
            {t("projectSettings.consultant", "مشاور")}
          </Label>
          <Input
            id='input-consultant'
            value={values.consultant}
            disabled={!canEdit}
            onChange={(e) =>
              setForm((f) => ({ ...f, consultant: e.target.value }))
            }
          />
        </div>
        <div>
          <Label htmlFor='input-location'>
            {t("projectSettings.location", "موقعیت")}
          </Label>
          <Input
            id='input-location'
            value={values.location}
            disabled={!canEdit}
            onChange={(e) =>
              setForm((f) => ({ ...f, location: e.target.value }))
            }
          />
        </div>

        {canEdit ? (
          <Button type='submit' loading={saveMutation.isPending}>
            {t("projectSettings.save", "ذخیره")}
          </Button>
        ) : null}
      </form>
    </>
  );
}

export default function ProjectSettingsPage() {
  const { projectId = "" } = useParams();

  return (
    <main className='page-main page-shell mx-auto px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <ProjectSettingsContent />
      </ProjectProvider>
    </main>
  );
}
