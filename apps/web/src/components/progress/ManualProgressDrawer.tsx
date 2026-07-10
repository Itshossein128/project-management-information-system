import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { fetchActivities } from "@/app/lib/api/activities";
import { postManualProgress } from "@/app/lib/api/progress";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

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
  const [reportDate, setReportDate] = useState("");
  const [actualProgress, setActualProgress] = useState("");
  const [cumulativeQuantity, setCumulativeQuantity] = useState("");
  const [notes, setNotes] = useState("");

  const { data: activitiesData } = useQuery({
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
        cumulative_quantity: cumulativeQuantity ? Number(cumulativeQuantity) : undefined,
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

  return (
    <Drawer
      isOpen={open}
      onClose={onClose}
      title="ثبت پیشرفت دستی"
      footer={
        <div className="flex flex-col gap-2">
          <p className="text-xs text-amber-700 dark:text-amber-300">
            پیشرفت دستی وارد شده توسط گزارش روزانه بازنویسی نخواهد شد مگر اینکه گزارش روزانه تأیید شود
          </p>
          <Button
            variant="primary"
            disabled={!activityId || !reportDate || !actualProgress || saveMutation.isPending}
            onClick={() => saveMutation.mutate()}
          >
            ذخیره
          </Button>
        </div>
      }
    >
      <div className="flex flex-col gap-4 p-4">
        <label className="flex flex-col gap-1 text-sm">
          <span>فعالیت</span>
          <select
            className="rounded-md border border-input bg-background px-3 py-2"
            value={activityId}
            onChange={(e) => setActivityId(e.target.value)}
          >
            <option value="">انتخاب فعالیت</option>
            {activities.map((a) => (
              <option key={a.activity_id} value={a.activity_id}>
                {`${a.activity_code} — ${a.activity_name}`}
              </option>
            ))}
          </select>
        </label>

        <JalaliDatePicker
          name="manual_progress_date"
          label="تاریخ"
          value={reportDate}
          onChange={setReportDate}
        />

        <label className="flex flex-col gap-1 text-sm">
          <span>پیشرفت واقعی (٪)</span>
          <input
            type="number"
            min={0}
            max={100}
            className="rounded-md border border-input bg-background px-3 py-2"
            value={actualProgress}
            onChange={(e) => setActualProgress(e.target.value)}
          />
        </label>

        <label className="flex flex-col gap-1 text-sm">
          <span>مقدار تجمعی</span>
          <input
            type="number"
            className="rounded-md border border-input bg-background px-3 py-2"
            value={cumulativeQuantity}
            onChange={(e) => setCumulativeQuantity(e.target.value)}
          />
        </label>

        <label className="flex flex-col gap-1 text-sm">
          <span>یادداشت</span>
          <textarea
            className="min-h-[80px] rounded-md border border-input bg-background px-3 py-2"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </label>
      </div>
    </Drawer>
  );
}
