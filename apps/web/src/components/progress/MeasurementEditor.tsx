import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { fetchActivities } from "@/app/lib/api/activities";
import {
  approveActivityMeasurement,
  changeActivityMeasurement,
  fetchActivityMeasurement,
  updateActivityMeasurement,
  type MeasurementMethod,
} from "@/app/lib/api/progress";
import { Field, Input, Select } from "@/components/form";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

export function MeasurementEditor({ projectId }: { projectId: string }) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const [activityId, setActivityId] = useState("");
  const [method, setMethod] = useState<MeasurementMethod>("quantity");
  const [totalQty, setTotalQty] = useState("");
  const [changeReason, setChangeReason] = useState("");

  const { data: activitiesData } = useQuery({
    queryKey: ["activities", projectId, "measurement-editor"],
    queryFn: () => fetchActivities(projectId, { page: 1, per_page: 200 }),
  });

  const { data: measurement } = useQuery({
    queryKey: ["activity-measurement", projectId, activityId],
    queryFn: () => fetchActivityMeasurement(projectId, activityId),
    enabled: Boolean(activityId),
    retry: false,
  });

  useEffect(() => {
    if (!measurement) return;
    setMethod(measurement.method);
    setTotalQty(
      measurement.total_quantity != null ? String(measurement.total_quantity) : "",
    );
  }, [measurement]);

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["activity-measurement", projectId, activityId] });
    void qc.invalidateQueries({ queryKey: ["progress-activities", projectId] });
  };

  const saveDraft = useMutation({
    mutationFn: () =>
      updateActivityMeasurement(projectId, activityId, {
        method,
        total_quantity: totalQty === "" ? null : Number(totalQty),
      }),
    onSuccess: () => {
      toast.success(t("common.save"));
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const approve = useMutation({
    mutationFn: () =>
      approveActivityMeasurement(
        projectId,
        activityId,
        measurement?.status === "approved" ? undefined : changeReason || undefined,
      ),
    onSuccess: () => {
      toast.success(t("progress.measurementApproved", { defaultValue: "Measurement approved" }));
      setChangeReason("");
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const startChange = useMutation({
    mutationFn: () =>
      changeActivityMeasurement(projectId, activityId, {
        reason: changeReason.trim(),
        method,
        total_quantity: totalQty === "" ? null : Number(totalQty),
      }),
    onSuccess: () => {
      toast.success(t("progress.measurementChangeStarted", { defaultValue: "Change submitted" }));
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const activities = activitiesData?.results ?? [];

  return (
    <section
      className="space-y-3 rounded-xl border border-border bg-card p-4"
      data-testid="measurement-editor"
    >
      <h2 className="text-lg font-semibold">
        {t("progress.measurementTitle", { defaultValue: "Activity measurement method" })}
      </h2>
      <Select
        name="measurement_activity"
        label={t("progress.selectActivity", { defaultValue: "Activity" })}
        value={activityId || undefined}
        placeholder="…"
        onChange={(e) => setActivityId(e.target.value)}
        options={activities.map((a) => ({
          value: a.activity_id,
          label: `${a.activity_code} — ${a.activity_name}`,
        }))}
      />
      {activityId ? (
        <>
          <div className="flex flex-wrap gap-3">
            <Select
              name="measurement_method"
              label={t("progress.method", { defaultValue: "Method" })}
              value={method}
              onChange={(e) => setMethod(e.target.value as MeasurementMethod)}
              options={[
                { value: "quantity", label: t("progress.methodQuantity", { defaultValue: "Quantity" }) },
                {
                  value: "weighted_milestones",
                  label: t("progress.methodMilestones", { defaultValue: "Weighted milestones" }),
                },
                {
                  value: "evidence_percent",
                  label: t("progress.methodEvidence", { defaultValue: "Evidence %" }),
                },
              ]}
            />
            {method === "quantity" ? (
              <Field name="total_qty" label={t("progress.totalQuantity", { defaultValue: "Total quantity" })}>
                {() => (
                  <Input
                    value={totalQty}
                    onChange={(e) => setTotalQty(e.target.value)}
                    type="number"
                  />
                )}
              </Field>
            ) : null}
          </div>
          <p className="text-xs text-muted-foreground" data-testid="measurement-status">
            {t("progress.status", { defaultValue: "Status" })}:{" "}
            {measurement?.status ?? "…"}
            {measurement?.pending_change_reason
              ? ` — ${measurement.pending_change_reason}`
              : ""}
          </p>
          {measurement?.status === "approved" ? (
            <Input
              value={changeReason}
              onChange={(e) => setChangeReason(e.target.value)}
              placeholder={t("progress.changeReason", { defaultValue: "Reason for method change" })}
            />
          ) : null}
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              variant="secondary"
              loading={saveDraft.isPending}
              disabled={!activityId}
              onClick={() => saveDraft.mutate()}
            >
              {t("common.save")}
            </Button>
            <Button
              size="sm"
              variant="primary"
              loading={approve.isPending}
              disabled={!activityId}
              onClick={() => approve.mutate()}
              data-testid="measurement-approve-btn"
            >
              {t("progress.approveMeasurement", { defaultValue: "Approve measurement" })}
            </Button>
            {measurement?.status === "approved" ? (
              <Button
                size="sm"
                variant="ghost"
                loading={startChange.isPending}
                disabled={!changeReason.trim()}
                onClick={() => startChange.mutate()}
                data-testid="measurement-change-btn"
              >
                {t("progress.requestChange", { defaultValue: "Request method change" })}
              </Button>
            ) : null}
          </div>
        </>
      ) : null}
    </section>
  );
}
