import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { fetchActivities } from "@/app/lib/api/activities";
import {
  fetchActivityMeasurement,
  postManualProgress,
} from "@/app/lib/api/progress";
import { fetchWBSFlat } from "@/app/lib/api/wbs";
import { Field, Input, Select, TextArea } from "@/components/form";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { EmptyState } from "@/components/layout/empty-state";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";
import { MeasurementEditor } from "@/components/progress/MeasurementEditor";
import { isIncompleteWorkPackage } from "@/components/wbs/wbs-package-meta-warning";

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

export function ManualProgressDrawer({
  projectId,
  open,
  onClose,
  onSaved,
}: {
  projectId: string;
  open: boolean;
  onClose: () => void;
  onSaved: () => void;
}) {
  const { t } = useTranslation();
  const toast = useToast();
  const [activityId, setActivityId] = useState("");
  const [reportDate, setReportDate] = useState(todayIso());
  const [actualProgress, setActualProgress] = useState("");
  const [cumulativeQuantity, setCumulativeQuantity] = useState("");
  const [notes, setNotes] = useState("");

  useEffect(() => {
    if (!open) return;
    setActivityId("");
    setReportDate(todayIso());
    setActualProgress("");
    setCumulativeQuantity("");
    setNotes("");
  }, [open]);

  const { data: activitiesData, isLoading } = useQuery({
    queryKey: ["activities", projectId, "manual-progress"],
    queryFn: () => fetchActivities(projectId, { page: 1, per_page: 200 }),
    enabled: open,
  });

  const { data: wbsFlat = [] } = useQuery({
    queryKey: ["wbs-flat", projectId],
    queryFn: () => fetchWBSFlat(projectId),
    enabled: open,
  });

  const { data: measurement } = useQuery({
    queryKey: ["activity-measurement", projectId, activityId],
    queryFn: () => fetchActivityMeasurement(projectId, activityId),
    enabled: open && Boolean(activityId),
    retry: false,
  });

  const saveMutation = useMutation({
    mutationFn: () =>
      postManualProgress(projectId, {
        activity_id: activityId,
        report_date: reportDate,
        actual_progress: Number(actualProgress),
        cumulative_quantity: cumulativeQuantity
          ? Number(cumulativeQuantity)
          : undefined,
        notes,
      }),
    onSuccess: () => {
      toast.success(t("progressReports.manualSaved", { defaultValue: "پیشرفت دستی ثبت شد" }));
      onSaved();
      onClose();
    },
    onError: (err: Error) => {
      const msg = err.message;
      if (msg.includes("progress_exceeds_100") || msg.includes("100")) {
        toast.error(t("progress.errors.exceeds100"));
      } else if (msg.includes("measurement_not_approved")) {
        toast.error(t("progress.errors.measurementNotApproved"));
      } else {
        toast.error(msg);
      }
    },
  });

  const activities = activitiesData?.results ?? [];
  const selectedActivity = activities.find((a) => a.activity_id === activityId);
  const selectedWbs = selectedActivity
    ? wbsFlat.find((w) => w.wbs_id === selectedActivity.wbs_id)
    : undefined;
  const showPackageMetaWarn = Boolean(
    selectedWbs && isIncompleteWorkPackage(selectedWbs),
  );
  const progressNum = actualProgress === "" ? NaN : Number(actualProgress);
  const progressOutOfRange =
    actualProgress !== "" &&
    (Number.isNaN(progressNum) || progressNum < 0 || progressNum > 100);
  const canSave =
    Boolean(activityId) &&
    Boolean(reportDate) &&
    actualProgress !== "" &&
    !progressOutOfRange &&
    !saveMutation.isPending;

  return (
    <Drawer
      isOpen={open}
      onClose={onClose}
      title="ثبت پیشرفت دستی"
      footer={
        <div className="flex flex-col gap-2">
          <p className="text-xs text-warning-700 dark:text-warning-300">
            پیشرفت دستی وارد شده توسط گزارش روزانه بازنویسی نخواهد شد مگر اینکه
            گزارش روزانه تأیید شود
          </p>
          <Button
            variant="primary"
            loading={saveMutation.isPending}
            disabled={!canSave}
            onClick={() => saveMutation.mutate()}
          >
            ذخیره
          </Button>
        </div>
      }
    >
      <div className="flex flex-col gap-4 p-4">
        {isLoading ? (
          <p className="text-sm text-muted-foreground">در حال بارگذاری فعالیت‌ها…</p>
        ) : activities.length === 0 ? (
          <EmptyState
            title="فعالیتی وجود ندارد"
            description="ابتدا حداقل یک فعالیت در پروژه تعریف کنید."
            className="py-8"
          />
        ) : (
          <Select
            name="manual_progress_activity"
            label="فعالیت"
            value={activityId || undefined}
            placeholder="انتخاب فعالیت"
            onChange={(e) => setActivityId(e.target.value)}
            options={activities.map((a) => ({
              value: a.activity_id,
              label: `${a.activity_code} — ${a.activity_name}`,
            }))}
          />
        )}

        {showPackageMetaWarn ? (
          <p
            className="rounded-md border border-warning-200 bg-warning-50 px-3 py-2 text-sm text-warning-900 dark:border-warning-800 dark:bg-warning-950/40 dark:text-warning-100"
            data-testid="progress-wbs-meta-warning"
          >
            {t("wbs.packageMetaSingle")}
          </p>
        ) : null}

        {activityId ? <MeasurementEditor projectId={projectId} activityId={activityId} /> : null}

        {activityId && measurement && measurement.status !== "approved" ? (
          <p
            className="rounded-md border border-warning-200 bg-warning-50 px-3 py-2 text-sm text-warning-900 dark:border-warning-800 dark:bg-warning-950/40 dark:text-warning-100"
            data-testid="measurement-not-approved-warning"
          >
            {t("progress.errors.measurementNotApproved")}
          </p>
        ) : null}

        <p className="text-xs text-muted-foreground">{t("progress.photoNotApproval")}</p>

        <JalaliDatePicker
          name="manual_progress_date"
          label="تاریخ"
          value={reportDate}
          onChange={setReportDate}
          required
        />

        <Field
          name="actual_progress"
          label="پیشرفت واقعی (٪)"
          htmlFor="manual-progress-pct"
          error={
            progressOutOfRange ? "مقدار باید بین ۰ تا ۱۰۰ باشد" : undefined
          }
          helpText="۰ تا ۱۰۰"
        >
          {() => (
            <Input
              id="manual-progress-pct"
              type="number"
              min={0}
              max={100}
              value={actualProgress}
              aria-invalid={progressOutOfRange || undefined}
              onChange={(e) => setActualProgress(e.target.value)}
            />
          )}
        </Field>

        <Field
          name="cumulative_quantity"
          label="مقدار تجمعی"
          htmlFor="manual-progress-qty"
        >
          {() => (
            <Input
              id="manual-progress-qty"
              type="number"
              value={cumulativeQuantity}
              onChange={(e) => setCumulativeQuantity(e.target.value)}
            />
          )}
        </Field>

        <TextArea
          name="manual_progress_notes"
          label="یادداشت"
          rows={3}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
      </div>
    </Drawer>
  );
}
