import { useQuery } from "@tanstack/react-query";
import { fetchMaterialReconciliation } from "@/app/lib/api/daily-reports";
import type { DailyTabProps } from "./ActivityTab";
import type { GridColumn, GridRow } from "./EditableGrid";
import { InlineGridTab } from "./InlineGridTab";

const STATUS_LABEL: Record<string, string> = {
  match: "مطابق",
  mismatch: "مغایرت",
  insufficient_data: "داده ناکافی",
};

export function MaterialsTab({
  projectId,
  reportId,
  report,
  readOnly,
  onChanged,
  activityOptions,
}: DailyTabProps) {
  const reconciliation = useQuery({
    queryKey: ["daily-report-materials-reconciliation", projectId, reportId],
    queryFn: () => fetchMaterialReconciliation(projectId, reportId!),
    enabled: Boolean(projectId && reportId),
  });

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
        { value: "return", label: "برگشتی" },
        { value: "waste", label: "ضایعات" },
      ],
    },
    { key: "quantity", header: "مقدار", type: "number", width: "100px" },
    { key: "unit_cost", header: "فی واحد", type: "number", width: "100px" },
    { key: "unit", header: "واحد", width: "90px" },
    { key: "consumption_location", header: "محل مصرف", width: "120px" },
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
    <div className="space-y-3">
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
          consumption_location: "",
          activity_ref: null,
          activity_description: "",
          notes: "",
        })}
        toPayload={(row: GridRow) => ({
          material_description: row.material_description ?? "",
          transaction_type: row.transaction_type ?? "issue",
          quantity: row.quantity ?? null,
          unit_cost: row.unit_cost ?? null,
          unit: row.unit ?? "",
          consumption_location: row.consumption_location ?? "",
          activity_ref: row.activity_ref ?? null,
          notes: row.notes ?? "",
        })}
        onChanged={() => {
          onChanged();
          void reconciliation.refetch();
        }}
        readOnly={readOnly}
      />

      {reportId ? (
        <div
          className="rounded-lg border border-border bg-muted/20 p-3 text-sm"
          data-testid="materials-reconciliation-panel"
        >
          <div className="mb-2 flex items-center justify-between gap-2">
            <p className="font-medium">تطبیق مصرف با موجودی (مشورتی)</p>
            <button
              type="button"
              className="rounded border border-border px-2 py-0.5 text-xs hover:bg-muted/40"
              onClick={() => void reconciliation.refetch()}
            >
              به‌روزرسانی
            </button>
          </div>
          {reconciliation.isLoading ? (
            <p className="text-muted-foreground">در حال بارگذاری…</p>
          ) : reconciliation.isError ? (
            <p className="text-danger-700">خطا در دریافت تطبیق</p>
          ) : (reconciliation.data?.items.length ?? 0) === 0 ? (
            <p className="text-muted-foreground">ردیفی برای تطبیق مصرف ثبت نشده است.</p>
          ) : (
            <ul className="space-y-1">
              {reconciliation.data!.items.map((item) => (
                <li
                  key={item.material_entry_id}
                  className="flex flex-wrap items-center gap-2 rounded border border-border/60 bg-card px-2 py-1"
                >
                  <span className="font-medium">{STATUS_LABEL[item.status] ?? item.status}</span>
                  <span className="text-muted-foreground">
                    مصرف {item.consumed_qty}
                    {item.available_balance != null ? ` · موجودی ${item.available_balance}` : ""}
                  </span>
                </li>
              ))}
            </ul>
          )}
          <p className="mt-2 text-xs text-muted-foreground">
            این هشدار مانع ذخیره یا ارسال گزارش نمی‌شود.
          </p>
        </div>
      ) : null}
    </div>
  );
}
