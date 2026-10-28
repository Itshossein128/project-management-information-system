import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { fetchActivities } from "@/app/lib/api/activities";
import { apiJson } from "@/app/lib/api-client";
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
import { Plus, Trash2, CheckCircle2, AlertCircle } from "lucide-react";

interface MilestoneItem {
  name: string;
  weight: number;
}

interface UnitItem {
  id: string;
  unit_name: string;
  unit_symbol: string;
}

export function MeasurementEditor({
  projectId,
  activityId: initialActivityId,
}: {
  projectId: string;
  activityId?: string;
}) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const [activityId, setActivityId] = useState(initialActivityId ?? "");

  useEffect(() => {
    if (initialActivityId !== undefined) {
      setActivityId(initialActivityId);
    }
  }, [initialActivityId]);

  const [method, setMethod] = useState<MeasurementMethod>("quantity_based");
  const [totalQty, setTotalQty] = useState("");
  const [unitId, setUnitId] = useState("");
  const [milestones, setMilestones] = useState<MilestoneItem[]>([]);
  const [evidenceRules, setEvidenceRules] = useState("");
  const [changeReason, setChangeReason] = useState("");

  const { data: activitiesData } = useQuery({
    queryKey: ["activities", projectId, "measurement-editor"],
    queryFn: () => fetchActivities(projectId, { page: 1, per_page: 200 }),
    enabled: !initialActivityId,
  });

  const { data: units = [] } = useQuery({
    queryKey: ["measurement-units"],
    queryFn: () => apiJson<UnitItem[]>("/v1/measurement-units/"),
  });

  const { data: measurement } = useQuery({
    queryKey: ["activity-measurement", projectId, activityId],
    queryFn: () => fetchActivityMeasurement(projectId, activityId),
    enabled: Boolean(activityId),
    retry: false,
  });

  useEffect(() => {
    if (!measurement) return;
    const m = measurement.method;
    if (m === "quantity") {
      setMethod("quantity_based");
    } else if (m === "evidence_percent") {
      setMethod("evidence_based");
    } else {
      setMethod(m);
    }
    setTotalQty(
      measurement.total_quantity != null ? String(measurement.total_quantity) : "",
    );
    setUnitId(measurement.unit_id ?? "");
    setMilestones(measurement.milestones ?? []);
    setEvidenceRules(measurement.evidence_rules ?? "");
  }, [measurement]);

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["activity-measurement", projectId, activityId] });
    void qc.invalidateQueries({ queryKey: ["progress-activities", projectId] });
  };

  const currentWeightSum = milestones.reduce((sum, item) => sum + (Number(item.weight) || 0), 0);
  const isMilestoneBalanced = Math.abs(currentWeightSum - 1.0) <= 0.0001 || Math.abs(currentWeightSum - 100) <= 0.01;

  const handleAddMilestone = () => {
    setMilestones([...milestones, { name: "", weight: 0.25 }]);
  };

  const handleRemoveMilestone = (index: number) => {
    setMilestones(milestones.filter((_, i) => i !== index));
  };

  const handleMilestoneChange = (index: number, field: "name" | "weight", value: string | number) => {
    const updated = [...milestones];
    if (field === "weight") {
      const num = Number(value);
      // Support entering either fraction (0.25) or percentage (25)
      updated[index] = { ...updated[index], weight: num > 1 ? num / 100 : num };
    } else {
      updated[index] = { ...updated[index], name: String(value) };
    }
    setMilestones(updated);
  };

  const saveDraft = useMutation({
    mutationFn: () =>
      updateActivityMeasurement(projectId, activityId, {
        method,
        total_quantity: totalQty === "" ? null : Number(totalQty),
        unit_id: unitId || null,
        milestones,
        evidence_rules: evidenceRules,
      }),
    onSuccess: () => {
      toast.success(t("common.save", { defaultValue: "Saved" }));
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
      toast.success(t("progress.measurementApproved", { defaultValue: "روش اندازه‌گیری تأیید شد" }));
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
        unit_id: unitId || null,
        milestones,
        evidence_rules: evidenceRules,
      }),
    onSuccess: () => {
      toast.success(t("progress.measurementChangeStarted", { defaultValue: "درخواست تغییر ارسال شد" }));
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const activities = activitiesData?.results ?? [];

  return (
    <section
      className="space-y-4 rounded-xl border border-border bg-card p-4"
      data-testid="measurement-editor"
    >
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold">
          {t("progress.measurementTitle", { defaultValue: "روش اندازه‌گیری پیشرفت فیزیکی" })}
        </h2>
        {activityId ? (
          <span className="text-xs px-2 py-0.5 rounded-full border border-border bg-muted text-muted-foreground" data-testid="measurement-status">
            {measurement?.status === "approved" ? "تأیید شده (Approved)" : "پیش‌نویس (Draft)"}
          </span>
        ) : null}
      </div>

      {!initialActivityId ? (
        <Select
          name="measurement_activity"
          label={t("progress.selectActivity", { defaultValue: "Activity" })}
          value={activityId || undefined}
          placeholder="انتخاب فعالیت…"
          onChange={(e) => setActivityId(e.target.value)}
          options={activities.map((a) => ({
            value: a.activity_id,
            label: `${a.activity_code} — ${a.activity_name}`,
          }))}
        />
      ) : null}

      {activityId ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Select
              name="measurement_method"
              label={t("progress.method", { defaultValue: "روش اندازه‌گیری" })}
              value={method}
              onChange={(e) => setMethod(e.target.value as MeasurementMethod)}
              options={[
                {
                  value: "quantity_based",
                  label: "مقدارمحور (Quantity-based Units Complete)",
                },
                {
                  value: "weighted_milestones",
                  label: "نقاط عطف وزنی (Weighted Milestones)",
                },
                {
                  value: "evidence_based",
                  label: "مستندمحور (Evidence-based Rules)",
                },
              ]}
            />

            {(method === "quantity_based" || method === "quantity") ? (
              <>
                <Field name="total_qty" label={t("progress.totalQuantity", { defaultValue: "حجم کل برآوردی (Total Quantity)" })}>
                  {() => (
                    <Input
                      value={totalQty}
                      onChange={(e) => setTotalQty(e.target.value)}
                      type="number"
                      placeholder="مثال: 1500"
                    />
                  )}
                </Field>

                <Select
                  name="unit_id"
                  label={t("progress.unit", { defaultValue: "واحد سنجش (Unit)" })}
                  value={unitId || undefined}
                  placeholder="انتخاب واحد…"
                  onChange={(e) => setUnitId(e.target.value)}
                  options={units.map((u) => ({
                    value: u.id,
                    label: `${u.unit_name} (${u.unit_symbol || "—"})`,
                  }))}
                />
              </>
            ) : null}
          </div>

          {method === "weighted_milestones" ? (
            <div className="space-y-3 rounded-lg border border-border p-3 bg-muted/20">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">نقاط عطف و اوزان درصدی (Milestones)</span>
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full font-medium ${
                      isMilestoneBalanced
                        ? "bg-success-100 text-success-800 dark:bg-success-950/40 dark:text-success-300"
                        : "bg-danger-100 text-danger-800 dark:bg-danger-950/40 dark:text-danger-300"
                    }`}
                  >
                    {isMilestoneBalanced ? (
                      <CheckCircle2 className="size-3.5" />
                    ) : (
                      <AlertCircle className="size-3.5" />
                    )}
                    مجموع اوزان: {(currentWeightSum <= 1 ? currentWeightSum * 100 : currentWeightSum).toFixed(1)}٪ (الزام: ۱۰۰٪)
                  </span>
                  <Button size="xs" variant="secondary" onClick={handleAddMilestone} type="button">
                    <Plus className="size-3.5 mr-1" />
                    افزودن عطف
                  </Button>
                </div>
              </div>

              {milestones.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-2">
                  هیچ نقطه عطفی ثبت نشده است. روی «افزودن عطف» کلیک کنید.
                </p>
              ) : (
                <div className="space-y-2">
                  {milestones.map((m, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <Input
                        placeholder={`عنوان عطف ${idx + 1}`}
                        value={m.name}
                        onChange={(e) => handleMilestoneChange(idx, "name", e.target.value)}
                        className="flex-1"
                      />
                      <div className="w-28 flex items-center gap-1">
                        <Input
                          type="number"
                          step="0.01"
                          placeholder="وزن"
                          value={m.weight != null ? (m.weight <= 1 ? (m.weight * 100).toFixed(1) : m.weight) : ""}
                          onChange={(e) => handleMilestoneChange(idx, "weight", e.target.value)}
                        />
                        <span className="text-xs text-muted-foreground">٪</span>
                      </div>
                      <Button
                        size="xs"
                        variant="ghost"
                        onClick={() => handleRemoveMilestone(idx)}
                        className="text-danger-600 hover:text-danger-700"
                        type="button"
                      >
                        <Trash2 className="size-3.5" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : null}

          {(method === "evidence_based" || method === "evidence_percent") ? (
            <div className="space-y-2">
              <label className="text-sm font-medium">قوانین و مستندات فنی لازم برای تأیید پیشرفت (Evidence Rules)</label>
              <textarea
                value={evidenceRules}
                onChange={(e) => setEvidenceRules(e.target.value)}
                placeholder="قوانین مهندسی، چک‌لیست‌های تحویل و آزمون‌های الزامی را وارد کنید…"
                className="w-full min-h-[80px] rounded-md border border-border bg-background p-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
            </div>
          ) : null}

          {measurement?.pending_change_reason ? (
            <p className="text-xs text-warning-700 dark:text-warning-400">
              دلیل تغییر در انتظار: {measurement.pending_change_reason}
            </p>
          ) : null}

          {measurement?.status === "approved" ? (
            <Input
              value={changeReason}
              onChange={(e) => setChangeReason(e.target.value)}
              placeholder={t("progress.changeReason", { defaultValue: "دلیل تغییر روش اندازه‌گیری (الزامی برای تغییر)" })}
            />
          ) : null}

          <div className="flex flex-wrap items-center gap-2 pt-2">
            <Button
              size="sm"
              variant="secondary"
              loading={saveDraft.isPending}
              disabled={!activityId}
              onClick={() => saveDraft.mutate()}
            >
              {t("common.save", { defaultValue: "ذخیره پیش‌نویس" })}
            </Button>
            <Button
              size="sm"
              variant="primary"
              loading={approve.isPending}
              disabled={!activityId || (method === "weighted_milestones" && !isMilestoneBalanced)}
              onClick={() => approve.mutate()}
              data-testid="measurement-approve-btn"
            >
              {t("progress.approveMeasurement", { defaultValue: "تأیید نهایی روش اندازه‌گیری" })}
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
                {t("progress.requestChange", { defaultValue: "درخواست تغییر روش" })}
              </Button>
            ) : null}
          </div>
        </>
      ) : null}
    </section>
  );
}
