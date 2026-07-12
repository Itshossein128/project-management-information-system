import type { DailyTabProps } from "./ActivityTab";
import type { GridColumn, GridRow } from "./EditableGrid";
import { InlineGridTab } from "./InlineGridTab";

export function LaborCampTab({
  projectId,
  reportId,
  report,
  readOnly,
  onChanged,
}: DailyTabProps) {
  const columns: GridColumn[] = [
    { key: "connex_number", header: "شماره کانکس", width: "120px" },
    { key: "subcontractor_name", header: "پیمانکار", width: "160px" },
    { key: "total_residents", header: "کل ساکنین", type: "number", width: "100px" },
    { key: "present_count", header: "حاضر", type: "number", width: "90px" },
    { key: "on_leave_count", header: "مرخصی", type: "number", width: "90px" },
    { key: "capacity", header: "ظرفیت", type: "number", width: "90px" },
    {
      key: "vacancy",
      header: "خالی",
      width: "70px",
      computed: (row) => {
        const cap = Number(row.capacity ?? 0);
        const present = Number(row.present_count ?? 0);
        return String(Math.max(0, cap - present));
      },
    },
  ];

  return (
    <InlineGridTab
      projectId={projectId}
      reportId={reportId}
      resource="labor-camp"
      columns={columns}
      serverRows={report?.labor_camp ?? []}
      emptyRow={() => ({
        connex_number: "",
        subcontractor_name: "",
        total_residents: 0,
        present_count: 0,
        on_leave_count: 0,
        capacity: 0,
      })}
      toPayload={(row: GridRow) => ({
        connex_number: row.connex_number ?? "",
        subcontractor_name: row.subcontractor_name ?? "",
        total_residents: row.total_residents ?? 0,
        present_count: row.present_count ?? 0,
        on_leave_count: row.on_leave_count ?? 0,
        capacity: row.capacity ?? 0,
      })}
      onChanged={onChanged}
      readOnly={readOnly}
    />
  );
}
