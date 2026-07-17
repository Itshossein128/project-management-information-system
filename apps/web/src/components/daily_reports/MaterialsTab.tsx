import type { DailyTabProps } from "./ActivityTab";
import type { GridColumn, GridRow } from "./EditableGrid";
import { InlineGridTab } from "./InlineGridTab";

export function MaterialsTab({
  projectId,
  reportId,
  report,
  readOnly,
  onChanged,
  activityOptions,
}: DailyTabProps) {
  const columns: GridColumn[] = [
    { key: "material_description", header: "شرح مصالح", width: "200px" },
    {
      key: "transaction_type",
      header: "نوع",
      type: "select",
      width: "110px",
      options: [
        { value: "receipt", label: "وارده" },
        { value: "issue", label: "مصرف شده" },
        { value: "waste", label: "ضایعات" },
      ],
    },
    { key: "quantity", header: "مقدار", type: "number", width: "100px" },
    { key: "unit_cost", header: "فی واحد", type: "number", width: "100px" },
    { key: "unit", header: "واحد", width: "90px" },
    {
      key: "activity_description",
      header: "فعالیت",
      type: "combobox",
      comboOptions: activityOptions,
      refKey: "activity_ref",
      width: "170px",
    },
  ];

  return (
    <InlineGridTab
      projectId={projectId}
      reportId={reportId}
      resource="materials"
      columns={columns}
      serverRows={report?.materials ?? []}
      emptyRow={() => ({
        material_description: "",
        transaction_type: "issue",
        quantity: null,
        unit_cost: null,
        unit: "",
        activity_ref: null,
        activity_description: "",
        notes: "",
      })}
      toPayload={(row: GridRow) => ({
        material_description: row.material_description ?? "",
        transaction_type: row.transaction_type ?? "issue",
        quantity: row.quantity ?? 0,
        unit_cost: row.unit_cost ?? null,
        unit: row.unit ?? "",
        activity_ref: row.activity_ref ?? null,
        notes: row.notes ?? "",
      })}
      onChanged={onChanged}
      readOnly={readOnly}
    />
  );
}
