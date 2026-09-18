import { Check, Circle, Minus, X } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { RequisitionScope, WorkflowStep, WorkflowStepState } from "~/lib/api/procurement";
import { formatDisplayDateTime } from "@/app/lib/jalali-utils";

interface Props {
  timeline: WorkflowStep[];
  scope: RequisitionScope;
  status: string;
}

/** Parse "3/8" progress string into a 0–100 percentage for progress bars. */
export function workflowProgressPercent(progress: string | null | undefined): number {
  if (!progress) return 0;
  const [done, total] = progress.split("/").map(Number);
  if (!total || Number.isNaN(done) || Number.isNaN(total)) return 0;
  return Math.min(100, Math.round((done / total) * 100));
}

function StepIcon({ state }: { state: WorkflowStepState }) {
  switch (state) {
    case "completed":
      return (
        <span className="flex size-7 items-center justify-center rounded-full bg-success-600 text-white">
          <Check className="size-4" />
        </span>
      );
    case "current":
      return (
        <span className="flex size-7 items-center justify-center rounded-full bg-primary text-primary-foreground ring-4 ring-primary/20">
          <Circle className="size-3 fill-current" />
        </span>
      );
    case "skipped":
      return (
        <span className="flex size-7 items-center justify-center rounded-full bg-muted text-muted-foreground">
          <Minus className="size-4" />
        </span>
      );
    case "rejected":
      return (
        <span className="flex size-7 items-center justify-center rounded-full bg-destructive text-destructive-foreground">
          <X className="size-4" />
        </span>
      );
    case "pending":
      return (
        <span className="flex size-7 items-center justify-center rounded-full border-2 border-muted-foreground/30 bg-background text-muted-foreground">
          <Circle className="size-3" />
        </span>
      );
    default: {
      const _exhaustive: never = state;
      return _exhaustive;
    }
  }
}

export function ProcurementWorkflowStepper({ timeline, scope, status }: Props) {
  const { t } = useTranslation();

  if (!timeline.length) return null;

  return (
    <div className="rounded-lg border border-border bg-card p-4" data-testid="procurement-workflow-stepper">
      <h3 className="mb-3 text-sm font-medium">{t("pages.procurement.approval.stepperTitle")}</h3>
      <div className="overflow-x-auto pb-2">
        <div className="flex min-w-max items-start gap-0 px-2">
        {timeline.map((step, idx) => (
          <div key={step.code} className="flex items-start">
            <div className="flex w-28 flex-col items-center gap-1.5 sm:w-32">
              <StepIcon state={step.state} />
              <p
                className={`text-center text-xs leading-tight ${
                  step.state === "current"
                    ? "font-semibold text-primary"
                    : step.state === "completed"
                      ? "font-medium text-foreground"
                      : step.state === "skipped"
                        ? "text-muted-foreground line-through"
                        : step.state === "rejected"
                      ? "font-medium text-destructive"
                      : "text-muted-foreground"
                }`}
                title={
                  step.state === "skipped" && scope === "workshop"
                    ? t("pages.procurement.approval.skippedWorkshopTooltip")
                    : undefined
                }
              >
                {step.label}
              </p>
              {step.state === "skipped" ? (
                <span className="text-[10px] text-muted-foreground">{t("pages.procurement.approval.skipped")}</span>
              ) : null}
              {step.state === "completed" && step.completed_at ? (
                <div className="max-w-28 text-center text-[10px] leading-snug text-muted-foreground">
                  <p>{formatDisplayDateTime(step.completed_at)}</p>
                  {step.completed_by_name ? <p className="truncate">{step.completed_by_name}</p> : null}
                </div>
              ) : null}
            </div>
            {idx < timeline.length - 1 && (
              <div
                className={`mt-3.5 h-0.5 w-6 sm:w-8 ${
                  step.state === "completed" ? "bg-success-500" : "bg-muted-foreground/20"
                }`}
              />
            )}
          </div>
        ))}
        </div>
      </div>
      {(status === "approved" || status === "rejected") && (
        <p className="mt-2 px-2 text-xs text-muted-foreground">
          {status === "approved"
            ? t("pages.procurement.approval.terminal.approved")
            : t("pages.procurement.approval.terminal.rejected")}
        </p>
      )}
    </div>
  );
}
