import type { DailyTabProps } from "./ActivityTab";
import type { GridColumn, GridRow } from "./EditableGrid";
import { InlineGridTab } from "./InlineGridTab";

function toHours(time: unknown): number | null {
  if (typeof time !== "string" || !time.includes(":")) return null;
  const [h, m] = time.split(":").map(Number);
  if (Number.isNaN(h)) return null;
  return h + (m || 0) / 60;
}

export function computeProductiveHours(row: GridRow): number | null {
  const start = toHours(row.work_start);
  const end = toHours(row.work_end);
  if (start == null || end == null) return null;
  let span = end - start;
  if (span < 0) span += 24;
  const repair = Number(row.repair_hours ?? 0) || 0;
  return Math.max(0, Number((span - repair).toFixed(2)));
}

export function EquipmentTab({
  projectId,
  reportId,
  report,
  readOnly,
  onChanged,
  activityOptions,
}: DailyTabProps) {
  const columns: GridColumn[] = [
    { key: "equipment_name", header: "دستگاه", width: "150px" },
    {
      key: "shift",
      header: "شیفت",
      type: "select",
      width: "90px",
      options: [
        { value: "day", label: "روز" },
        { value: "night", label: "شب" },
        { value: "full", label: "تمام روز" },
      ],
    },
    {
      key: "status",
      header: "وضعیت",
      type: "select",
      width: "90px",
      options: [
        { value: "active", label: "فعال" },
        { value: "standby", label: "آماده" },
        { value: "broken", label: "خراب" },
      ],
    },
    {
      key: "ownership_type",
      header: "مالکیت",
      type: "select",
      width: "90px",
      options: [
        { value: "owned", label: "تملیکی" },
        { value: "rented", label: "اجاره‌ای" },
      ],
    },
    { key: "work_start", header: "شروع", type: "time", width: "100px" },
    { key: "work_end", header: "پایان", type: "time", width: "100px" },
    { key: "repair_hours", header: "تعمیرات", type: "number", width: "80px" },
    {
      key: "productive_hours",
      header: "کارکرد",
      width: "80px",
      computed: (row) => {
        const c = computeProductiveHours(row);
        return c == null ? "—" : String(c);
      },
    },
    {
      key: "activity_description",
      header: "فعالیت",
      type: "combobox",
      comboOptions: activityOptions,
      refKey: "activity_ref",
      width: "160px",
    },
  ];

  return (
    <InlineGridTab
      projectId={projectId}
      reportId={reportId}
      resource="equipment"
      columns={columns}
      serverRows={(report?.equipment ?? []).map((e) => ({
        ...e,
        activity_description: e.activity_ref ? findActivityLabel(activityOptions, e.activity_ref) : "",
      }))}
      emptyRow={() => ({
        equipment_name: "",
        shift: "full",
        status: "active",
        ownership_type: "owned",
        work_start: "",
        work_end: "",
        repair_hours: 0,
        activity_ref: null,
        activity_description: "",
        notes: "",
      })}
      toPayload={(row: GridRow) => ({
        equipment_name: row.equipment_name ?? "",
        shift: row.shift ?? "full",
        status: row.status ?? "active",
        ownership_type: row.ownership_type ?? "owned",
        work_start: row.work_start || null,
        work_end: row.work_end || null,
        repair_hours: row.repair_hours ?? 0,
        productive_hours: computeProductiveHours(row),
        activity_ref: row.activity_ref ?? null,
        notes: row.notes ?? "",
      })}
      onChanged={onChanged}
      readOnly={readOnly}
    />
  );
}

function findActivityLabel(options: { value: string; label: string }[], id: string) {
  return options.find((o) => o.value === id)?.label ?? "";
}
