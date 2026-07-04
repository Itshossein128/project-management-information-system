import type { UserBusinessAssignment } from "@/app/lib/api-types";
import { splitAssignmentsForTablePreview } from "@/app/lib/assignment-preview";
import { Modal } from "@/components/overlay/modal";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";

// Function to manage getBusinessName
function getBusinessName(a: UserBusinessAssignment): string {
  if (typeof a.business === "object" && a.business) return a.business.name;
  return "—";
}

// Function to manage getJobLabel
function getJobLabel(a: UserBusinessAssignment): string {
  if (typeof a.job_position === "object" && a.job_position) return a.job_position.label;
  return "—";
}

// Function to manage AllAssignmentsModal
export function AllAssignmentsModal(props: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  userLabel: string;
  assignments: UserBusinessAssignment[];
}) {
  const { t } = useTranslation();

  // Variable holding lines
  const lines = useMemo(() => {
    // Prefer rich rows if present; fallback to display lines.
    const hasRich = props.assignments.some(
      (a) => typeof a.business === "object" || typeof a.job_position === "object",
    );
    if (hasRich) return null;
    return splitAssignmentsForTablePreview(props.assignments, 999).lines;
  }, [props.assignments]);

  return (
    <Modal
      open={props.open}
      onOpenChange={props.onOpenChange}
      idBase="allAssignments"
      title={t("assignments.modalTitle", { user: props.userLabel })}
    >
      <div id="container-allAssignmentsModal">
        <p className="mb-4 text-muted-foreground text-sm" id="text-allAssignmentsSubtitle">
          {t("assignments.modalSubtitle")}
        </p>

        {props.assignments.length === 0 ? (
          <p id="text-allAssignmentsEmpty" className="text-muted-foreground text-sm">
            {t("assignments.empty")}
          </p>
        ) : (
          <div id="list-allAssignments" className="space-y-2">
            {lines
              ? lines.map((line, index) => (
                  <div
                    key={`${index}-${line}`}
                    id={`item-assignment-${index}`}
                    className="rounded-md border border-border px-3 py-2"
                  >
                    <span id={`text-assignmentLine-${index}`}>{line}</span>
                  </div>
                ))
              : props.assignments.map((a, index) => (
                  <div
                    key={a.id ?? index}
                    id={`item-assignment-${index}`}
                    className="rounded-md border border-border px-3 py-2"
                  >
                    <div className="flex flex-col gap-1">
                      <span id={`text-assignmentBusiness-${index}`} className="font-medium">
                        {getBusinessName(a)}
                      </span>
                      <span id={`text-assignmentJob-${index}`} className="text-muted-foreground text-sm">
                        {getJobLabel(a)}
                      </span>
                    </div>
                  </div>
                ))}
          </div>
        )}
      </div>
    </Modal>
  );
}

