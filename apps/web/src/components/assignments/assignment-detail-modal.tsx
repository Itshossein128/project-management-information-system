import type { UserBusinessAssignment } from "@/app/lib/api-types";
import { Modal } from "@/components/overlay/modal";
import { useTranslation } from "react-i18next";

// Function to manage getUserName
function getUserName(a: UserBusinessAssignment): string {
  if (typeof a.user === "object" && a.user) return a.user.full_name;
  return "—";
}

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

// Function to manage AssignmentDetailModal
export function AssignmentDetailModal(props: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  assignment: UserBusinessAssignment | null;
}) {
  const { t } = useTranslation();

  // Variable holding a
  const a = props.assignment;
  return (
    <Modal
      open={props.open}
      onOpenChange={props.onOpenChange}
      idBase="assignmentDetail"
      title={t("assignmentDetail.modalTitle")}
      className="max-w-xl"
    >
      <div id="container-assignmentDetail">
        {!a ? (
          <p id="text-assignmentDetailEmpty" className="text-muted-foreground text-sm">
            {t("assignmentDetail.empty")}
          </p>
        ) : (
          <div id="container-assignmentDetailFields" className="grid gap-3">
            <div id="container-assignmentDetail-user">
              <div id="text-assignmentDetailLabel-user" className="text-xs text-muted-foreground">
                {t("assignmentDetail.user")}
              </div>
              <div id="text-assignmentDetailValue-user" className="text-sm font-medium">
                {getUserName(a)}
              </div>
            </div>
            <div id="container-assignmentDetail-business">
              <div id="text-assignmentDetailLabel-business" className="text-xs text-muted-foreground">
                {t("assignmentDetail.business")}
              </div>
              <div id="text-assignmentDetailValue-business" className="text-sm font-medium">
                {getBusinessName(a)}
              </div>
            </div>
            <div id="container-assignmentDetail-jobPosition">
              <div id="text-assignmentDetailLabel-jobPosition" className="text-xs text-muted-foreground">
                {t("assignmentDetail.jobPosition")}
              </div>
              <div id="text-assignmentDetailValue-jobPosition" className="text-sm font-medium">
                {getJobLabel(a)}
              </div>
            </div>
            <div id="container-assignmentDetail-status">
              <div id="text-assignmentDetailLabel-status" className="text-xs text-muted-foreground">
                {t("assignmentDetail.status")}
              </div>
              <div id="text-assignmentDetailValue-status" className="text-sm">
                {a.status ?? "—"}
              </div>
            </div>
            <div id="container-assignmentDetail-wage">
              <div id="text-assignmentDetailLabel-wage" className="text-xs text-muted-foreground">
                {t("assignmentDetail.wage")}
              </div>
              <div id="text-assignmentDetailValue-wage" className="text-sm">
                {a.wage ?? "—"}
              </div>
            </div>
            <div id="container-assignmentDetail-weeklyTotal">
              <div id="text-assignmentDetailLabel-weeklyTotal" className="text-xs text-muted-foreground">
                {t("assignmentDetail.weeklyTotal")}
              </div>
              <div id="text-assignmentDetailValue-weeklyTotal" className="text-sm">
                {a.weekly_total ?? "—"}
              </div>
            </div>
            <div id="container-assignmentDetail-monthlyTotal">
              <div id="text-assignmentDetailLabel-monthlyTotal" className="text-xs text-muted-foreground">
                {t("assignmentDetail.monthlyTotal")}
              </div>
              <div id="text-assignmentDetailValue-monthlyTotal" className="text-sm">
                {a.monthly_total ?? "—"}
              </div>
            </div>
            <div id="container-assignmentDetail-tools">
              <div id="text-assignmentDetailLabel-tools" className="text-xs text-muted-foreground">
                {t("assignmentDetail.tools")}
              </div>
              <div id="text-assignmentDetailValue-tools" className="text-sm">
                {a.tools?.length ? a.tools.join(", ") : "—"}
              </div>
            </div>
            <div id="container-assignmentDetail-startDate">
              <div id="text-assignmentDetailLabel-startDate" className="text-xs text-muted-foreground">
                {t("assignmentDetail.startDate")}
              </div>
              <div id="text-assignmentDetailValue-startDate" className="text-sm">
                {a.start_date ?? "—"}
              </div>
            </div>
            <div id="container-assignmentDetail-endDate">
              <div id="text-assignmentDetailLabel-endDate" className="text-xs text-muted-foreground">
                {t("assignmentDetail.endDate")}
              </div>
              <div id="text-assignmentDetailValue-endDate" className="text-sm">
                {a.end_date ?? "—"}
              </div>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}

