import { useTranslation } from "react-i18next";
import type { ConcreteRow } from "@/app/lib/api/daily-reports";
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
    <div id="summary-section-concrete">
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
      {readOnly ? report?.concrete_logs.map((row) => (
        <ConcreteQcDetails key={row.id} row={row} />
      )) : null}
    </div>
  );
}

export function ConcreteQcDetails({ row }: { row: ConcreteRow }) {
  const { t } = useTranslation();
  const details = row.qc_details;
  if (!details) return null;
  const prefix = "dailyReports.referenceHeader";
  const values = {
    batchingPlant: details.batching_plant,
    truckMixer: details.truck_mixer,
    labSheetNumber: details.lab_sheet_number,
    slump: details.slump,
    result28Day: details.result_28_day_href ? (
      <a href={details.result_28_day_href} className="text-primary underline">{t(`${prefix}.openResult`)}</a>
    ) : null,
  };
  return (
    <details className="py-1">
      <summary className="cursor-pointer text-sm text-primary">
        {t(`${prefix}.concreteDetails`, { description: row.concrete_description })}
      </summary>
      <dl className="mt-2 space-y-1 text-xs">
        {Object.entries(values).map(([field, value]) => (
          <div key={field}>
            <dt className="inline font-medium">{t(`${prefix}.${field}`)}</dt>
            <dd className="ms-1 inline">{value ?? t(`${prefix}.unknown`)}</dd>
          </div>
        ))}
      </dl>
    </details>
  );
}
