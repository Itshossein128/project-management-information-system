import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import {
  createActivity,
  fetchWeightSummary,
  updateActivity,
  type Activity,
  type ActivityPayload,
  type ActivityStatus,
} from "@/app/lib/api/activities";
import { fetchMembers } from "@/app/lib/api/members";
import { fetchWBSFlat } from "@/app/lib/api/wbs";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { Input } from "@/components/form";
import { Label } from "@/components/ui/label";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { cn } from "@/app/lib/utils";

const STATUS_OPTIONS: { value: ActivityStatus; label: string }[] = [
  { value: "not_started", label: "شروع نشده" },
  { value: "in_progress", label: "در حال اجرا" },
  { value: "suspended", label: "متوقف" },
  { value: "completed", label: "تکمیل شده" },
];

function weightToPercent(weight: string | null | undefined): string {
  if (weight == null || weight === "") return "";
  return String(Math.round(parseFloat(weight) * 10000) / 100);
}

function percentToWeight(percent: string): number | null {
  if (percent.trim() === "") return null;
  const n = parseFloat(percent);
  if (Number.isNaN(n)) return null;
  return n / 100;
}

function calcDuration(start: string | null, finish: string | null): number | null {
  if (!start || !finish) return null;
  const s = new Date(start);
  const f = new Date(finish);
  const diff = Math.round((f.getTime() - s.getTime()) / 86400000) + 1;
  return diff > 0 ? diff : null;
}

export interface ActivityDrawerProps {
  projectId: string;
  isOpen: boolean;
  onClose: () => void;
  activity: Activity | null;
  onSaved: () => void;
  onError: (message: string) => void;
}

export function ActivityDrawer({
  projectId,
  isOpen,
  onClose,
  activity,
  onSaved,
  onError,
}: ActivityDrawerProps) {
  const isEdit = Boolean(activity);

  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [unit, setUnit] = useState("");
  const [quantity, setQuantity] = useState("");
  const [weightPct, setWeightPct] = useState("");
  const [description, setDescription] = useState("");
  const [plannedStart, setPlannedStart] = useState("");
  const [plannedFinish, setPlannedFinish] = useState("");
  const [actualStart, setActualStart] = useState("");
  const [actualFinish, setActualFinish] = useState("");
  const [responsibleId, setResponsibleId] = useState("");
  const [wbsId, setWbsId] = useState("");
  const [status, setStatus] = useState<ActivityStatus>("not_started");
  const [saving, setSaving] = useState(false);
  const [wbsSearch, setWbsSearch] = useState("");

  const { data: wbsFlat = [] } = useQuery({
    queryKey: ["wbs-flat", projectId],
    queryFn: () => fetchWBSFlat(projectId),
    enabled: isOpen,
  });

  const { data: members = [] } = useQuery({
    queryKey: ["members", projectId],
    queryFn: () => fetchMembers(projectId),
    enabled: isOpen,
  });

  const { data: weightSummary, refetch: refetchWeight } = useQuery({
    queryKey: ["activity-weight-summary", projectId],
    queryFn: () => fetchWeightSummary(projectId),
    enabled: isOpen,
  });

  useEffect(() => {
    if (!isOpen) return;
    if (activity) {
      setCode(activity.activity_code);
      setName(activity.activity_name);
      setUnit(activity.unit_name ?? "");
      setQuantity(activity.total_quantity ?? "");
      setWeightPct(weightToPercent(activity.weight));
      setDescription(activity.description ?? "");
      setPlannedStart(activity.planned_start ?? "");
      setPlannedFinish(activity.planned_finish ?? "");
      setActualStart(activity.actual_start ?? "");
      setActualFinish(activity.actual_finish ?? "");
      setResponsibleId(activity.responsible_id ?? "");
      setWbsId(activity.wbs_id);
      setStatus(activity.status);
    } else {
      setCode("");
      setName("");
      setUnit("");
      setQuantity("");
      setWeightPct("");
      setDescription("");
      setPlannedStart("");
      setPlannedFinish("");
      setActualStart("");
      setActualFinish("");
      setResponsibleId("");
      setWbsId(wbsFlat[0]?.wbs_id ?? "");
      setStatus("not_started");
    }
    setWbsSearch("");
  }, [isOpen, activity, wbsFlat]);

  const filteredWbs = useMemo(() => {
    const q = wbsSearch.trim().toLowerCase();
    if (!q) return wbsFlat;
    return wbsFlat.filter(
      (n) => n.wbs_code.toLowerCase().includes(q) || n.wbs_name.toLowerCase().includes(q),
    );
  }, [wbsFlat, wbsSearch]);

  const plannedDuration = calcDuration(plannedStart || null, plannedFinish || null);

  const weightBarColor = weightSummary
    ? weightSummary.is_balanced
      ? "bg-emerald-500"
      : weightSummary.total_weight < 0.99 || weightSummary.total_weight > 1.01
        ? "bg-red-500"
        : "bg-amber-500"
    : "bg-muted";

  async function handleSave() {
    if (!code.trim() || !name.trim() || !wbsId) {
      onError("کد، نام و WBS الزامی هستند.");
      return;
    }
    const payload: ActivityPayload = {
      activity_code: code.trim(),
      activity_name: name.trim(),
      wbs_id: wbsId,
      total_quantity: quantity ? quantity : null,
      weight: percentToWeight(weightPct),
      planned_start: plannedStart || null,
      planned_finish: plannedFinish || null,
      actual_start: actualStart || null,
      actual_finish: actualFinish || null,
      responsible_id: responsibleId || null,
      status,
      description,
    };
    setSaving(true);
    try {
      if (isEdit && activity) {
        await updateActivity(projectId, activity.activity_id, payload);
      } else {
        await createActivity(projectId, payload);
      }
      await refetchWeight();
      onSaved();
    } catch (e) {
      onError(e instanceof Error ? e.message : "خطا در ذخیره فعالیت");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? "ویرایش فعالیت" : "افزودن فعالیت"}
      footer={
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose}>لغو</Button>
          <Button onClick={() => void handleSave()} disabled={saving}>
            {saving ? "در حال ذخیره…" : "ذخیره"}
          </Button>
        </div>
      }
    >
      <div className="space-y-6">
        <section className="space-y-3">
          <h3 className="text-sm font-semibold text-muted-foreground">اطلاعات پایه</h3>
          <div className="space-y-2">
            <Label htmlFor="act-code">کد فعالیت</Label>
            <Input id="act-code" value={code} onChange={(e) => setCode(e.target.value)} className="font-mono" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="act-name">نام فعالیت</Label>
            <Input id="act-name" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label htmlFor="act-unit">واحد</Label>
              <Input id="act-unit" value={unit} onChange={(e) => setUnit(e.target.value)} placeholder="—" disabled />
            </div>
            <div className="space-y-2">
              <Label htmlFor="act-qty">مقدار کل</Label>
              <Input id="act-qty" value={quantity} onChange={(e) => setQuantity(e.target.value)} />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="act-weight">وزن (%)</Label>
            <Input
              id="act-weight"
              value={weightPct}
              onChange={(e) => setWeightPct(e.target.value)}
              placeholder="مثلاً 12.5"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="act-desc">توضیحات</Label>
            <textarea
              id="act-desc"
              className="min-h-20 w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
        </section>

        <section className="space-y-3">
          <h3 className="text-sm font-semibold text-muted-foreground">زمان‌بندی</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label>شروع برنامه</Label>
              <JalaliDatePicker name="planned_start" value={plannedStart} onChange={setPlannedStart} />
            </div>
            <div className="space-y-2">
              <Label>پایان برنامه</Label>
              <JalaliDatePicker name="planned_finish" value={plannedFinish} onChange={setPlannedFinish} />
            </div>
          </div>
          <p className="text-sm text-muted-foreground">
            مدت برنامه: {plannedDuration != null ? `${plannedDuration} روز` : "—"}
          </p>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label>شروع واقعی</Label>
              <JalaliDatePicker name="actual_start" value={actualStart} onChange={setActualStart} />
            </div>
            <div className="space-y-2">
              <Label>پایان واقعی</Label>
              <JalaliDatePicker name="actual_finish" value={actualFinish} onChange={setActualFinish} />
            </div>
          </div>
        </section>

        <section className="space-y-3">
          <h3 className="text-sm font-semibold text-muted-foreground">مسئول</h3>
          <select
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            value={responsibleId}
            onChange={(e) => setResponsibleId(e.target.value)}
          >
            <option value="">—</option>
            {members.filter((m) => m.user_id).map((m) => (
              <option key={m.user_id!} value={m.user_id!}>{m.full_name}</option>
            ))}
          </select>
        </section>

        <section className="space-y-3">
          <h3 className="text-sm font-semibold text-muted-foreground">WBS</h3>
          <Input
            placeholder="جستجوی WBS…"
            value={wbsSearch}
            onChange={(e) => setWbsSearch(e.target.value)}
          />
          <select
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            value={wbsId}
            onChange={(e) => setWbsId(e.target.value)}
          >
            {filteredWbs.map((n) => (
              <option key={n.wbs_id} value={n.wbs_id}>
                {"—".repeat(Math.max(0, n.depth - 1))} {n.wbs_code} — {n.wbs_name}
              </option>
            ))}
          </select>
        </section>

        <section className="space-y-2">
          <h3 className="text-sm font-semibold text-muted-foreground">وضعیت</h3>
          <select
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            value={status}
            onChange={(e) => setStatus(e.target.value as ActivityStatus)}
          >
            {STATUS_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </section>

        {weightSummary ? (
          <div className="rounded-lg border border-border p-3">
            <div className="mb-2 flex justify-between text-xs text-muted-foreground">
              <span>مجموع وزن فعالیت‌ها</span>
              <span>{Math.round(weightSummary.total_weight * 1000) / 10}٪</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-muted">
              <div
                className={cn("h-full transition-all", weightBarColor)}
                style={{ width: `${Math.min(100, weightSummary.total_weight * 100)}%` }}
              />
            </div>
            {weightSummary.warning ? (
              <p className="mt-2 text-xs text-amber-700 dark:text-amber-400">{weightSummary.warning}</p>
            ) : null}
          </div>
        ) : null}
      </div>
    </Drawer>
  );
}
