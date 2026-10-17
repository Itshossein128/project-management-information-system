import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";
import { usePermission } from "@/app/contexts/project-context";
import { ApiRequestError } from "@/app/lib/api-client";
import { PATHS } from "@/app/routeVars";
import {
  approveProject,
  archiveProject,
  completeProject,
  type ProjectDetail,
  rejectProject,
  submitProject,
  suspendProject,
} from "@/app/lib/api/projects";
import { useToast } from "@/components/ui/toast";

type LifecycleAction =
  | "submit"
  | "approve"
  | "reject"
  | "suspend"
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
    onError: (err: Error) => {
      if (err instanceof ApiRequestError && err.code === "activation_gates_failed") return;
      toast.error(err.message);
    },
  });

  const activationError = run.error instanceof ApiRequestError &&
    run.error.code === "activation_gates_failed" ? run.error : null;
  const details = activationError?.details;
  const missing = details && typeof details === "object" && "missing" in details &&
    Array.isArray(details.missing) ? details.missing.filter((item): item is string => typeof item === "string") : [];
  const requirementMessages = new Map([
    ["project_manager", t("project.activationMissingManager")],
    ["scope_description", t("project.activationMissingScope")],
    ["budget_approved", t("project.activationMissingAmount")],
  ]);
  const status = project.status;
  const busy = run.isPending;
  if (!canEdit && !canApprove) return null;

  return (
    <div
      className="mb-4 flex flex-wrap items-center gap-2 rounded-lg border border-border bg-muted/20 p-3"
      data-testid="project-lifecycle-bar"
    >
      {activationError ? (
        <div
          role="alert"
          className="w-full space-y-2 rounded-md border border-danger-500/50 bg-danger-50 p-3 text-sm text-danger-900 dark:bg-danger-950 dark:text-danger-100"
        >
          <p className="font-semibold">{t("project.activationIncomplete")}</p>
          {missing.length > 0 ? (
            <ul className="list-disc space-y-1 ps-5">
              {Array.from(new Set(missing)).map((field) => (
                <li key={field}>{requirementMessages.get(field) ?? t("project.activationMissingOther")}</li>
              ))}
            </ul>
          ) : null}
          <p>{t("project.activationCompletionHint")}</p>
          {canEdit ? (
            <Link
              to={`/${PATHS.PROJECT}/${project.project_id}/${PATHS.PROJECT_SETTINGS}`}
              className="inline-flex rounded font-semibold underline underline-offset-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {t("project.completeActivationInfo")}
            </Link>
          ) : <p>{t("project.activationContactEditor")}</p>}
        </div>
      ) : null}
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
