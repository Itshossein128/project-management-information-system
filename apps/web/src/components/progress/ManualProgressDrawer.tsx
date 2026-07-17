import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { fetchActivities } from "@/app/lib/api/activities";
import { postManualProgress } from "@/app/lib/api/progress";
import { Field, Input, Select, TextArea } from "@/components/form";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { EmptyState } from "@/components/layout/empty-state";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

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
      toast.success("پیشرفت دستی ثبت شد");
      onSaved();
      onClose();
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const activities = activitiesData?.results ?? [];
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
          <p className="text-xs text-amber-700 dark:text-amber-300">
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
