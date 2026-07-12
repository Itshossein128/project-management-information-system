import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import { createContract } from "@/app/lib/api/contracts";
import { PATHS } from "@/app/routeVars";
import {
  ContractForm,
  EMPTY_CONTRACT_FORM,
  formToContractPayload,
  type ContractFormValues,
} from "@/components/contracts/ContractForm";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

function ContractFormPage({ mode }: { mode: "create" | "edit" }) {
  const { projectId, project, isLoading } = useProject();
  const { contractId } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const { has } = usePermission(projectId);
  const canEdit = has("edit_contracts");
  const [values, setValues] = useState<ContractFormValues>(EMPTY_CONTRACT_FORM);

  const save = useMutation({
    mutationFn: () => createContract(projectId, formToContractPayload(values)),
    onSuccess: (data) => {
      toast.success(mode === "create" ? "قرارداد ایجاد شد" : "قرارداد ذخیره شد");
      navigate(`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_CONTRACTS}/${data.id}`);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (isLoading) return <LoadingSkeleton rows={10} />;
  if (!project) return <p>پروژه یافت نشد</p>;
  if (!canEdit) {
    return (
      <p className="rounded-lg border p-8 text-center text-muted-foreground">
        دسترسی به ویرایش قراردادها ندارید.
      </p>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={mode === "create" ? "قرارداد جدید" : "ویرایش قرارداد"}
        subtitle={project.project_name}
      />
      <ContractForm
        values={values}
        onChange={(patch) => setValues((prev) => ({ ...prev, ...patch }))}
      />
      <div className="flex gap-2">
        <Button variant="primary" loading={save.isPending} onClick={() => save.mutate()}>
          ذخیره
        </Button>
        <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_CONTRACTS}`}>
          <Button variant="secondary">انصراف</Button>
        </Link>
      </div>
    </div>
  );
}

export default function ProjectContractFormPage() {
  const { projectId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto max-w-4xl px-4 py-8">
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "قراردادها", href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_CONTRACTS}` },
            { label: "جدید" },
          ]}
        />
        <ContractFormPage mode="create" />
      </main>
    </ProjectProvider>
  );
}
