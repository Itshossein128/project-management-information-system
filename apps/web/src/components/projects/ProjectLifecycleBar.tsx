import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { usePermission } from "@/app/contexts/project-context";
import {
  approveProject,
  archiveProject,
  completeProject,
  type ProjectDetail,
  rejectProject,
  resumeProject,
  submitProject,
  suspendProject,
} from "@/app/lib/api/projects";
import { useToast } from "@/components/ui/toast";

type LifecycleAction =
  | "submit"
  | "approve"
  | "reject"
  | "suspend"
  | "resume"
  | "complete"
  | "archive";

interface Props {
  project: ProjectDetail;
}

export function ProjectLifecycleBar({ project }: Props) {
  const { t } = useTranslation();
  const toast = useToast();
  const queryClient = useQueryClient();
  const { has } = usePermission(project.project_id);
  const canEdit = has("edit_project");
  const canApprove = has("approve_project") || canEdit;

  const run = useMutation({
    mutationFn: async (action: LifecycleAction) => {
      const id = project.project_id;
      switch (action) {
        case "submit":
          return submitProject(id);
        case "approve":
          return approveProject(id);
        case "reject":
          return rejectProject(id);
        case "suspend":
          return suspendProject(id);
        case "resume":
          return resumeProject(id);
        case "complete":
          return completeProject(id);
        case "archive":
          return archiveProject(id);
        default: {
          const _exhaustive: never = action;
          throw new Error(`Unknown action ${_exhaustive}`);
        }
      }
    },
    onSuccess: () => {
      toast.success(t("project.lifecycleUpdated", "وضعیت پروژه به‌روز شد"));
      void queryClient.invalidateQueries({ queryKey: ["project", project.project_id] });
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const status = project.status;
  const busy = run.isPending;
  if (!canEdit && !canApprove) return null;

  return (
    <div
      className="mb-4 flex flex-wrap items-center gap-2 rounded-lg border border-border bg-muted/20 p-3"
      data-testid="project-lifecycle-bar"
    >
      {canEdit && status === "draft" ? (
        <button
          type="button"
          disabled={busy}
          data-testid="project-submit-btn"
          className="rounded-md bg-primary px-3 py-1.5 text-sm text-primary-foreground disabled:opacity-50"
          onClick={() => run.mutate("submit")}
        >
          {t("project.submitForApproval", "ارسال برای تصویب")}
        </button>
      ) : null}
      {canApprove && status === "pending_approval" ? (
        <>
          <button
            type="button"
            disabled={busy}
            data-testid="project-approve-btn"
            className="rounded-md bg-success-600 px-3 py-1.5 text-sm text-white disabled:opacity-50"
            onClick={() => run.mutate("approve")}
          >
            {t("project.approve", "تصویب و فعال‌سازی")}
          </button>
          <button
            type="button"
            disabled={busy}
            data-testid="project-reject-btn"
            className="rounded-md bg-danger-600 px-3 py-1.5 text-sm text-white disabled:opacity-50"
            onClick={() => run.mutate("reject")}
          >
            {t("project.reject", "رد")}
          </button>
        </>
      ) : null}
      {canEdit && status === "active" ? (
        <>
          <button
            type="button"
            disabled={busy}
            className="rounded-md border border-border px-3 py-1.5 text-sm"
            onClick={() => run.mutate("suspend")}
          >
            {t("project.suspend", "تعلیق")}
          </button>
          <button
            type="button"
            disabled={busy}
            className="rounded-md border border-border px-3 py-1.5 text-sm"
            onClick={() => run.mutate("complete")}
          >
            {t("project.complete", "خاتمه")}
          </button>
        </>
      ) : null}
      {canEdit && status === "suspended" ? (
        <button
          type="button"
          disabled={busy}
          className="rounded-md border border-border px-3 py-1.5 text-sm"
          onClick={() => run.mutate("resume")}
        >
          {t("project.resume", "ازسرگیری")}
        </button>
      ) : null}
      {canEdit && (status === "completed" || status === "active" || status === "suspended") ? (
        <button
          type="button"
          disabled={busy}
          className="rounded-md border border-border px-3 py-1.5 text-sm"
          onClick={() => run.mutate("archive")}
        >
          {t("project.archive", "بایگانی")}
        </button>
      ) : null}
    </div>
  );
}
