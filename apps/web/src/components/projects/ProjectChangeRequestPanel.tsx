import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { usePermission } from "@/app/contexts/project-context";
import {
  approveProjectChangeRequest,
  createProjectChangeRequest,
  fetchProjectChangeRequests,
  rejectProjectChangeRequest,
  submitProjectChangeRequest,
  type ProjectChangeRequest,
} from "@/app/lib/api/projects";
import { Button } from "@/components/ui/sprint-button";
import { Input } from "@/components/form";
import { useToast } from "@/components/ui/toast";

interface Props {
  projectId: string;
}

export function ProjectChangeRequestPanel({ projectId }: Props) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const { has } = usePermission(projectId);
  const canEdit = has("edit_project");
  const canApprove = has("approve_project") || has("edit_project");

  const [reason, setReason] = useState("");
  const [employer, setEmployer] = useState("");
  const [contractAmount, setContractAmount] = useState("");
  const [scope, setScope] = useState("");

  const { data: requests = [], isLoading } = useQuery({
    queryKey: ["project-change-requests", projectId],
    queryFn: () => fetchProjectChangeRequests(projectId),
  });

  const open = requests.find((r) => r.status === "draft" || r.status === "submitted");

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["project-change-requests", projectId] });
    void qc.invalidateQueries({ queryKey: ["project", projectId] });
  };

  const createMutation = useMutation({
    mutationFn: () => {
      const proposed_changes: Record<string, unknown> = {};
      if (employer.trim()) proposed_changes.employer = employer.trim();
      if (contractAmount.trim()) proposed_changes.contract_amount = contractAmount.trim();
      if (scope.trim()) proposed_changes.scope_description = scope.trim();
      return createProjectChangeRequest(projectId, reason.trim(), proposed_changes);
    },
    onSuccess: () => {
      toast.success(t("project.crCreated", "درخواست تغییر ایجاد شد"));
      setReason("");
      setEmployer("");
      setContractAmount("");
      setScope("");
      invalidate();
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const actionMutation = useMutation({
    mutationFn: async ({
      cr,
      action,
    }: {
      cr: ProjectChangeRequest;
      action: "submit" | "approve" | "reject";
    }) => {
      if (action === "submit") return submitProjectChangeRequest(projectId, cr.id);
      if (action === "approve") return approveProjectChangeRequest(projectId, cr.id);
      return rejectProjectChangeRequest(projectId, cr.id);
    },
    onSuccess: () => {
      toast.success(t("common.saved", "ذخیره شد"));
      invalidate();
    },
    onError: (err: Error) => toast.error(err.message),
  });

  return (
    <section
      className="mx-auto mt-10 max-w-2xl space-y-3 border-t pt-8"
      data-testid="project-change-request-panel"
    >
      <h2 className="text-base font-semibold">
        {t("project.changeRequests", "درخواست‌های تغییر")}
      </h2>
      <p className="text-sm text-muted-foreground">
        {t(
          "project.changeRequestsHint",
          "پس از فعال‌سازی، فیلدهای محافظت‌شده فقط از مسیر درخواست تغییر قابل ویرایش هستند.",
        )}
      </p>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
      ) : null}

      {open ? (
        <div
          className="space-y-2 rounded-md border border-border p-3 text-sm"
          data-testid={`cr-item-${open.status}`}
        >
          <p>
            <span className="text-muted-foreground">{t("project.crStatus", "وضعیت")}: </span>
            {open.status}
          </p>
          <p>
            <span className="text-muted-foreground">{t("project.crReason", "دلیل")}: </span>
            {open.reason}
          </p>
          <pre className="overflow-x-auto rounded bg-muted/40 p-2 text-xs">
            {JSON.stringify(open.proposed_changes, null, 2)}
          </pre>
          <div className="flex flex-wrap gap-2">
            {open.status === "draft" && canEdit ? (
              <Button
                type="button"
                size="sm"
                data-testid="cr-submit-btn"
                loading={actionMutation.isPending}
                onClick={() => actionMutation.mutate({ cr: open, action: "submit" })}
              >
                {t("project.crSubmit", "ارسال")}
              </Button>
            ) : null}
            {open.status === "submitted" && canApprove ? (
              <>
                <Button
                  type="button"
                  size="sm"
                  data-testid="cr-approve-btn"
                  loading={actionMutation.isPending}
                  onClick={() => actionMutation.mutate({ cr: open, action: "approve" })}
                >
                  {t("project.crApprove", "تایید")}
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant="secondary"
                  data-testid="cr-reject-btn"
                  loading={actionMutation.isPending}
                  onClick={() => actionMutation.mutate({ cr: open, action: "reject" })}
                >
                  {t("project.crReject", "رد")}
                </Button>
              </>
            ) : null}
          </div>
        </div>
      ) : canEdit ? (
        <form
          className="space-y-3"
          onSubmit={(e) => {
            e.preventDefault();
            if (reason.trim().length < 10) {
              toast.error(
                t("project.crReasonMin", "دلیل باید حداقل ۱۰ کاراکتر باشد"),
              );
              return;
            }
            if (!employer && !contractAmount && !scope) {
              toast.error(t("project.crNeedField", "حداقل یک فیلد پیشنهادی لازم است"));
              return;
            }
            createMutation.mutate();
          }}
        >
          <div>
            <label className="mb-1 block text-sm" htmlFor="cr-reason">
              {t("project.crReason", "دلیل")}
            </label>
            <Input
              id="cr-reason"
              data-testid="cr-reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-sm" htmlFor="cr-field-employer">
              {t("project.employer", "کارفرما")}
            </label>
            <Input
              id="cr-field-employer"
              data-testid="cr-field-employer"
              value={employer}
              onChange={(e) => setEmployer(e.target.value)}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm" htmlFor="cr-field-amount">
              {t("project.amount", "مبلغ قرارداد")}
            </label>
            <Input
              id="cr-field-amount"
              data-testid="cr-field-amount"
              value={contractAmount}
              onChange={(e) => setContractAmount(e.target.value)}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm" htmlFor="cr-field-scope">
              {t("project.scope", "شرح محدوده")}
            </label>
            <Input
              id="cr-field-scope"
              data-testid="cr-field-scope"
              value={scope}
              onChange={(e) => setScope(e.target.value)}
            />
          </div>
          <Button
            type="submit"
            data-testid="cr-create-btn"
            loading={createMutation.isPending}
          >
            {t("project.crCreate", "ایجاد درخواست تغییر")}
          </Button>
        </form>
      ) : null}
    </section>
  );
}
