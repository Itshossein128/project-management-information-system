import type { DailyReportDetail } from "@/app/lib/api/daily-reports";
import type { GridColumn, GridRow } from "./EditableGrid";
import { InlineGridTab } from "./InlineGridTab";

export interface TabRefData {
  activityOptions: { value: string; label: string }[];
  subcontractorOptions: { value: string; label: string }[];
}

export interface DailyTabProps extends TabRefData {
  projectId: string;
  reportId: string | null;
  report: DailyReportDetail | null;
  readOnly?: boolean;
  onChanged: () => void;
}

const SHIFT_OPTIONS = [
  { value: "shift_1", label: "ش۱" },
  { value: "shift_2", label: "ش۲" },
  { value: "shift_3", label: "ش۳" },
];

export function ActivityTab({
  projectId,
  reportId,
  report,
  readOnly,
  onChanged,
  activityOptions,
  subcontractorOptions,
}: DailyTabProps) {
  const columns: GridColumn[] = [
    {
      key: "activity_description",
      header: "شرح فعالیت",
      type: "combobox",
      comboOptions: activityOptions,
      refKey: "activity_ref",
      width: "220px",
      placeholder: "جستجو یا متن آزاد",
    },
    { key: "shift", header: "شیفت", type: "select", options: SHIFT_OPTIONS, width: "80px" },
    {
      key: "subcontractor_name",
      header: "پیمانکار",
      type: "combobox",
      comboOptions: subcontractorOptions,
      refKey: "subcontractor_ref",
      width: "150px",
    },
    { key: "headcount", header: "نفر", type: "number", width: "70px" },
    { key: "zone", header: "قطعه", width: "90px" },
    { key: "block", header: "بلوک", width: "90px" },
    { key: "floor", header: "طبقه", width: "90px" },
    { key: "quantity", header: "مقدار", type: "number", width: "90px" },
    { key: "quantity_measured", header: "اندازه‌گیری شده", type: "checkbox", width: "60px" },
    { key: "unit", header: "واحد", width: "80px" },
  ];

  return (
    <InlineGridTab
      projectId={projectId}
      reportId={reportId}
      resource="activities"
      columns={columns}
      serverRows={report?.activities ?? []}
      emptyRow={() => ({
        activity_description: "",
        activity_ref: null,
        shift: "shift_1",
        subcontractor_name: "",
        subcontractor_ref: null,
        headcount: null,
        zone: "",
        block: "",
        floor: "",
        quantity: null,
        quantity_measured: true,
        unit: "",
      })}
      toPayload={(row: GridRow) => ({
        activity_description: row.activity_description ?? "",
        activity_ref: row.activity_ref ?? null,
        shift: row.shift ?? "shift_1",
        subcontractor_name: row.subcontractor_name ?? "",
        subcontractor_ref: row.subcontractor_ref ?? null,
        headcount: row.headcount ?? null,
        zone: row.zone ?? "",
        block: row.block ?? "",
        floor: row.floor ?? "",
        quantity: row.quantity_measured ? row.quantity ?? null : null,
        quantity_measured: row.quantity_measured ?? true,
        unit: row.unit ?? "",
      })}
      onChanged={onChanged}
      readOnly={readOnly}
    />
  );
}
