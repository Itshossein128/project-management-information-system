import type { DailyTabProps } from "./ActivityTab";
import type { GridColumn, GridRow } from "./EditableGrid";
import { InlineGridTab } from "./InlineGridTab";

export function IncidentsTab({
  projectId,
  reportId,
  report,
  readOnly,
  onChanged,
}: DailyTabProps) {
  const columns: GridColumn[] = [
    {
      key: "incident_type",
      header: "نوع",
      type: "select",
      width: "130px",
      options: [
        { value: "safety", label: "ایمنی" },
        { value: "quality", label: "کیفیت" },
        { value: "environmental", label: "زیست‌محیطی" },
        { value: "stoppage", label: "توقف کار" },
        { value: "visitor", label: "بازدید" },
      ],
    },
    { key: "description", header: "شرح", width: "260px" },
    { key: "corrective_action", header: "اقدام اصلاحی", width: "220px" },
  ];

  return (
    <InlineGridTab
      projectId={projectId}
      reportId={reportId}
      resource="incidents"
      columns={columns}
      serverRows={report?.incidents ?? []}
      emptyRow={() => ({ incident_type: "safety", description: "", corrective_action: "" })}
      toPayload={(row: GridRow) => ({
        incident_type: row.incident_type ?? "safety",
        description: row.description ?? "",
        corrective_action: row.corrective_action ?? "",
      })}
      onChanged={onChanged}
      readOnly={readOnly}
    />
  );
}
