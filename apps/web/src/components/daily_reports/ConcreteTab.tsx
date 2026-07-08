import type { DailyTabProps } from "./ActivityTab";
import type { GridColumn, GridRow } from "./EditableGrid";
import { InlineGridTab } from "./InlineGridTab";

export function ConcreteTab({
  projectId,
  reportId,
  report,
  readOnly,
  onChanged,
  activityOptions,
}: DailyTabProps) {
  const columns: GridColumn[] = [
    { key: "concrete_description", header: "شرح بتن‌ریزی", width: "200px" },
    { key: "volume_m3", header: "حجم (م³)", type: "number", width: "100px" },
    {
      key: "activity_description",
      header: "فعالیت",
      type: "combobox",
      comboOptions: activityOptions,
      refKey: "activity_ref",
      width: "170px",
    },
    { key: "zone", header: "قطعه", width: "90px" },
    { key: "block", header: "بلوک", width: "90px" },
    { key: "floor", header: "طبقه", width: "90px" },
  ];

  return (
    <InlineGridTab
      projectId={projectId}
      reportId={reportId}
      resource="concrete-logs"
      columns={columns}
      serverRows={report?.concrete_logs ?? []}
      emptyRow={() => ({
        concrete_description: "",
        volume_m3: null,
        activity_ref: null,
        activity_description: "",
        zone: "",
        block: "",
        floor: "",
        notes: "",
      })}
      toPayload={(row: GridRow) => ({
        concrete_description: row.concrete_description ?? "",
        volume_m3: row.volume_m3 ?? 0,
        activity_ref: row.activity_ref ?? null,
        zone: row.zone ?? "",
        block: row.block ?? "",
        floor: row.floor ?? "",
        notes: row.notes ?? "",
      })}
      onChanged={onChanged}
      readOnly={readOnly}
    />
  );
}
