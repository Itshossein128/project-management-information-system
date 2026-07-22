import { useQuery } from "@tanstack/react-query";
import type { DailyTabProps } from "./ActivityTab";
import type { GridColumn, GridRow } from "./EditableGrid";
import { fetchEquipmentRegistry } from "@/app/lib/api/equipment";
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
  const { data: registry = [] } = useQuery({
    queryKey: ["equipment-registry", projectId],
    queryFn: async () => {
      const res = await fetchEquipmentRegistry(projectId);
      return Array.isArray(res) ? res : res.results;
    },
    enabled: Boolean(projectId),
  });

  const equipmentOptions = registry.map((e) => ({
    value: e.id,
    label: `${e.equipment_code} — ${e.equipment_name}`,
  }));

  const columns: GridColumn[] = [
    {
      key: "equipment_name",
      header: "دستگاه",
      type: equipmentOptions.length > 0 ? "combobox" : undefined,
      comboOptions: equipmentOptions,
      refKey: "equipment",
      width: "150px",
    },
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
    { key: "idle_hours", header: "بیکاری", type: "number", width: "80px" },
    { key: "idle_reason", header: "علت بیکاری", width: "120px" },
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
        equipment_name: e.equipment
          ? findEquipmentLabel(equipmentOptions, e.equipment) || e.equipment_name
          : e.equipment_name,
        activity_description: e.activity_ref
          ? findActivityLabel(activityOptions, e.activity_ref)
          : "",
      }))}
      emptyRow={() => ({
        equipment: null,
        equipment_name: "",
        equipment_ref: "",
        shift: "full",
        status: "active",
        ownership_type: "owned",
        work_start: "",
        work_end: "",
        repair_hours: 0,
        idle_hours: null,
        idle_reason: "",
        activity_ref: null,
        activity_description: "",
        notes: "",
      })}
      toPayload={(row: GridRow) => {
        const matched = registry.find((e) => e.id === row.equipment);
        const name =
          matched?.equipment_name ||
          stripEquipmentLabel(String(row.equipment_name ?? "")) ||
          "";
        return {
          equipment: row.equipment ?? null,
          equipment_name: name,
          equipment_ref: matched?.equipment_code || row.equipment_ref || "",
          shift: row.shift ?? "full",
          status: row.status ?? "active",
          ownership_type: row.ownership_type ?? "owned",
          work_start: row.work_start || null,
          work_end: row.work_end || null,
          repair_hours: row.repair_hours ?? 0,
          idle_hours: row.idle_hours ?? null,
          idle_reason: row.idle_reason ?? "",
          productive_hours: computeProductiveHours(row),
          activity_ref: row.activity_ref ?? null,
          notes: row.notes ?? "",
        };
      }}
      onChanged={onChanged}
      readOnly={readOnly}
    />
  );
}

function findActivityLabel(options: { value: string; label: string }[], id: string) {
  return options.find((o) => o.value === id)?.label ?? "";
}

function findEquipmentLabel(options: { value: string; label: string }[], id: string) {
  return options.find((o) => o.value === id)?.label ?? "";
}

/** "CODE — Name" → "Name" when free-typed without registry match. */
function stripEquipmentLabel(label: string): string {
  const sep = " — ";
  const idx = label.indexOf(sep);
  return idx >= 0 ? label.slice(idx + sep.length) : label;
}
