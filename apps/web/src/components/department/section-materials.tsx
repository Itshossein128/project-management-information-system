import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Pencil, Plus, Trash2, X } from "lucide-react";

import {
  useCreateUnitReportMaterial,
  useDeleteUnitReportMaterial,
  useUnitReportMaterialsQuery,
  useUpdateUnitReportMaterial,
} from "@/app/hooks/queries";
import {
  extractSectionErrors,
  type CanonicalUnit,
  type SectionFieldError,
  type UnitMaterialTransactionType,
  type UnitReport,
  type UnitReportMaterialPayload,
  type UnitReportMaterialRow,
} from "@/app/lib/api/unit-reports";
import { Button, Field, Input, Select } from "@/components/form";
import type { SelectOption } from "@/components/form/Select";

export interface SectionMaterialsProps {
  businessId: string;
  unit: CanonicalUnit;
  report: UnitReport;
}

interface MaterialFormState {
  transaction_type: UnitMaterialTransactionType;
  material_ref: string;
  material_description: string;
  quantity: string;
  unit: string;
  supplier: string;
  warehouse_document_reference: string;
  consumption_location: string;
}

const EMPTY_MATERIAL_FORM: MaterialFormState = {
  transaction_type: "receipt",
  material_ref: "",
  material_description: "",
  quantity: "1.0000",
  unit: "",
  supplier: "",
  warehouse_document_reference: "",
  consumption_location: "",
};

function parseQuantityField(raw: string): number {
  const trimmed = raw.trim();
  if (!trimmed) return 0;
  const num = Number(trimmed);
  if (!Number.isFinite(num)) return 0;
  return num;
}

export function SectionMaterials({
  businessId,
  unit,
  report,
}: SectionMaterialsProps) {
  const { t } = useTranslation();

  const canEdit =
    report.capabilities.can_edit &&
    (report.status === "draft" || report.status === "rejected");

  const materialsQuery = useUnitReportMaterialsQuery(
    businessId,
    unit,
    report.id,
  );
  const rows = materialsQuery.data ?? [];

  const createMutation = useCreateUnitReportMaterial(
    businessId,
    unit,
    report.id,
  );
  const updateMutation = useUpdateUnitReportMaterial(
    businessId,
    unit,
    report.id,
  );
  const deleteMutation = useDeleteUnitReportMaterial(
    businessId,
    unit,
    report.id,
  );

  const [formOpen, setFormOpen] = useState(false);
  const [editingRowId, setEditingRowId] = useState<string | null>(null);
  const [formState, setFormState] = useState<MaterialFormState>(
    EMPTY_MATERIAL_FORM,
  );
  const [fieldErrors, setFieldErrors] = useState<
    Record<string, SectionFieldError[]>
  >({});
  const [bannerError, setBannerError] = useState<{
    code: string | null;
    message: string;
  } | null>(null);

  const transactionOptions: SelectOption[] = useMemo(
    () => [
      {
        value: "receipt",
        label: t(
          "businessDepartment.unitReport.sections.materials.transactionTypes.receipt",
        ),
      },
      {
        value: "consumption",
        label: t(
          "businessDepartment.unitReport.sections.materials.transactionTypes.consumption",
        ),
      },
    ],
    [t],
  );

  const counts = useMemo(() => {
    let receipts = 0;
    let consumptions = 0;
    for (const r of rows) {
      if (r.transaction_type === "receipt") receipts += 1;
      else consumptions += 1;
    }
    return { receipts, consumptions };
  }, [rows]);

  function clearErrorsForField(field: string) {
    setFieldErrors((prev) => {
      if (!prev[field]) return prev;
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }

  function localizeError(err: SectionFieldError): string {
    const sectionKey = `businessDepartment.unitReport.sections.materials.errors.${err.code}`;
    const sectionTranslated = t(sectionKey, { defaultValue: "" });
    if (sectionTranslated && sectionTranslated !== sectionKey) {
      return sectionTranslated;
    }
    const globalKey = `errors.${err.code}`;
    const globalTranslated = t(globalKey, { defaultValue: "" });
    if (globalTranslated && globalTranslated !== globalKey) {
      return globalTranslated;
    }
    return err.message || err.code;
  }

  function renderErrorChip(field: string) {
    const list = fieldErrors[field];
    if (!list || list.length === 0) return null;
    const first = list[0]!;
    return (
      <div
        id={`chip-unitMaterialsError-${field}`}
        data-testid={`materials-error-chip-${field}`}
        data-error-code={first.code}
        role="alert"
        className="mt-1 inline-flex items-center gap-1.5 rounded-md border border-destructive/40 bg-destructive/10 px-2 py-0.5 text-xs font-medium text-destructive"
      >
        <span>{localizeError(first)}</span>
      </div>
    );
  }

  function handleOpenNew() {
    setEditingRowId(null);
    setFormState(EMPTY_MATERIAL_FORM);
    setFieldErrors({});
    setBannerError(null);
    setFormOpen(true);
  }

  function handleStartEdit(row: UnitReportMaterialRow) {
    setEditingRowId(row.id);
    setFormState({
      transaction_type: row.transaction_type ?? "receipt",
      material_ref: row.material_ref ?? "",
      material_description: row.material_description ?? "",
      quantity: row.quantity != null ? String(row.quantity) : "1.0000",
      unit: row.unit ?? "",
      supplier: row.supplier ?? "",
      warehouse_document_reference: row.warehouse_document_reference ?? "",
      consumption_location: row.consumption_location ?? "",
    });
    setFieldErrors({});
    setBannerError(null);
    setFormOpen(true);
  }

  function handleCancelForm() {
    setFormOpen(false);
    setEditingRowId(null);
    setFieldErrors({});
    setBannerError(null);
  }

  async function handleSaveRow(e: React.FormEvent) {
    e.preventDefault();
    setFieldErrors({});
    setBannerError(null);

    const txType = formState.transaction_type;
    const qty = parseQuantityField(formState.quantity);
    const docRef = formState.warehouse_document_reference.trim();
    const location = formState.consumption_location.trim();

    const localErrors: Record<string, SectionFieldError[]> = {};
    if (!txType) {
      localErrors.transaction_type = [
        {
          field: "transaction_type",
          code: "transaction_type_required",
          message: t(
            "businessDepartment.unitReport.sections.materials.errors.transaction_type_required",
          ),
        },
      ];
    }
    if (qty <= 0) {
      localErrors.quantity = [
        {
          field: "quantity",
          code: "quantity_must_be_positive",
          message: t(
            "businessDepartment.unitReport.sections.materials.errors.quantity_must_be_positive",
          ),
        },
      ];
    }
    if (txType === "receipt" && !docRef) {
      localErrors.warehouse_document_reference = [
        {
          field: "warehouse_document_reference",
          code: "receipt_requires_document_reference",
          message: t(
            "businessDepartment.unitReport.sections.materials.errors.receipt_requires_document_reference",
          ),
        },
      ];
    }
    if (txType === "consumption" && !location) {
      localErrors.consumption_location = [
        {
          field: "consumption_location",
          code: "consumption_location_required_for_consumption",
          message: t(
            "businessDepartment.unitReport.sections.materials.errors.consumption_location_required_for_consumption",
          ),
        },
      ];
    }

    if (Object.keys(localErrors).length > 0) {
      setFieldErrors(localErrors);
    }

    const payload: UnitReportMaterialPayload = {
      transaction_type: txType,
      material_ref: formState.material_ref.trim() || null,
      material_description: formState.material_description.trim(),
      quantity: formState.quantity.trim() || "0",
      unit: formState.unit.trim(),
      supplier: formState.supplier.trim(),
      warehouse_document_reference: docRef,
      consumption_location: txType === "consumption" ? location : "",
    };

    try {
      if (editingRowId) {
        await updateMutation.mutateAsync({
          rowId: editingRowId,
          patch: payload,
        });
      } else {
        await createMutation.mutateAsync(payload);
      }
      setFormOpen(false);
      setEditingRowId(null);
      setFormState(EMPTY_MATERIAL_FORM);
    } catch (err) {
      const parsed = extractSectionErrors(err);
      setFieldErrors((prev) => ({ ...prev, ...parsed.fieldErrors }));
      const firstUnbound = parsed.allErrors.find(
        (item) => !item.field || !(item.field in parsed.fieldErrors),
      );
      if (firstUnbound) {
        setBannerError({
          code: firstUnbound.code,
          message: localizeError(firstUnbound),
        });
      } else if (parsed.allErrors.length === 0) {
        setBannerError({
          code: parsed.topCode,
          message: parsed.topMessage,
        });
      }
    }
  }

  async function handleDeleteRow(rowId: string) {
    setBannerError(null);
    try {
      await deleteMutation.mutateAsync(rowId);
      if (editingRowId === rowId) {
        handleCancelForm();
      }
    } catch (err) {
      const parsed = extractSectionErrors(err);
      setBannerError({
        code: parsed.topCode,
        message: parsed.topMessage,
      });
    }
  }

  const isMutating =
    createMutation.isPending ||
    updateMutation.isPending ||
    deleteMutation.isPending;

  return (
    <div
      id="section-unitReportMaterials"
      data-testid="unit-section-materials"
      className="space-y-4 rounded-lg border border-border/70 bg-background p-4"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3
            id="text-unitMaterialsTitle"
            className="text-base font-semibold tracking-tight"
          >
            {t("businessDepartment.unitReport.sections.materials.title")}
          </h3>
          <p className="text-xs text-muted-foreground">
            {t("businessDepartment.unitReport.sections.materials.subtitle")}
          </p>
        </div>

        {canEdit && !formOpen ? (
          <Button
            id="button-addUnitMaterialRow"
            data-testid="add-unit-material-row"
            type="button"
            size="sm"
            onClick={handleOpenNew}
          >
            <Plus className="me-1.5 h-4 w-4" />
            {t("businessDepartment.unitReport.sections.materials.addRow")}
          </Button>
        ) : null}
      </div>

      {bannerError ? (
        <div
          id="alert-unitMaterialsSectionError"
          data-testid="materials-section-banner-error"
          data-error-code={bannerError.code || undefined}
          role="alert"
          className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-xs text-destructive"
        >
          <span>{bannerError.message}</span>
          {bannerError.code ? (
            <span className="ms-1.5 font-mono opacity-75">
              ({bannerError.code})
            </span>
          ) : null}
        </div>
      ) : null}

      {canEdit && formOpen ? (
        <form
          id="form-unitMaterialRow"
          data-testid="unit-material-row-form"
          onSubmit={(e) => void handleSaveRow(e)}
          className="space-y-4 rounded-lg border border-border bg-muted/20 p-4"
          noValidate
        >
          <div className="flex items-center justify-between border-b border-border/60 pb-2">
            <h4 className="text-sm font-semibold">
              {editingRowId
                ? t("businessDepartment.unitReport.sections.materials.editRow")
                : t("businessDepartment.unitReport.sections.materials.addRow")}
            </h4>
            <Button
              id="button-closeUnitMaterialForm"
              type="button"
              size="sm"
              variant="ghost"
              onClick={handleCancelForm}
              aria-label={t("common.cancel")}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <Select
                id="select-unitMaterialTransactionType"
                name="transaction_type"
                label={`${t("businessDepartment.unitReport.sections.materials.fields.transactionType")} *`}
                value={formState.transaction_type}
                options={transactionOptions}
                onChange={(e) => {
                  clearErrorsForField("transaction_type");
                  clearErrorsForField("warehouse_document_reference");
                  clearErrorsForField("consumption_location");
                  setFormState((prev) => ({
                    ...prev,
                    transaction_type: e.target
                      .value as UnitMaterialTransactionType,
                  }));
                }}
              />
              {renderErrorChip("transaction_type")}
            </div>

            <div className="sm:col-span-2">
              <Field
                name="unitMaterialDescription"
                label={`${t("businessDepartment.unitReport.sections.materials.fields.materialDescription")} *`}
                htmlFor="input-unitMaterialDescription"
              >
                {() => (
                  <Input
                    id="input-unitMaterialDescription"
                    name="material_description"
                    dir="auto"
                    value={formState.material_description}
                    onChange={(e) => {
                      clearErrorsForField("material_description");
                      setFormState((prev) => ({
                        ...prev,
                        material_description: e.target.value,
                      }));
                    }}
                    placeholder={t(
                      "businessDepartment.unitReport.sections.materials.fields.materialDescriptionPlaceholder",
                    )}
                  />
                )}
              </Field>
              {renderErrorChip("material_description")}
            </div>

            <div>
              <Field
                name="unitMaterialRef"
                label={t(
                  "businessDepartment.unitReport.sections.materials.fields.materialRef",
                )}
                htmlFor="input-unitMaterialRef"
              >
                {() => (
                  <Input
                    id="input-unitMaterialRef"
                    name="material_ref"
                    dir="ltr"
                    value={formState.material_ref}
                    onChange={(e) => {
                      clearErrorsForField("material_ref");
                      setFormState((prev) => ({
                        ...prev,
                        material_ref: e.target.value,
                      }));
                    }}
                    placeholder={t(
                      "businessDepartment.unitReport.sections.materials.fields.materialRefPlaceholder",
                    )}
                  />
                )}
              </Field>
              {renderErrorChip("material_ref")}
            </div>

            <div>
              <Field
                name="unitMaterialQuantity"
                label={`${t("businessDepartment.unitReport.sections.materials.fields.quantity")} *`}
                htmlFor="input-unitMaterialQuantity"
              >
                {() => (
                  <Input
                    id="input-unitMaterialQuantity"
                    name="quantity"
                    type="number"
                    min={0.0001}
                    step="any"
                    value={formState.quantity}
                    onChange={(e) => {
                      clearErrorsForField("quantity");
                      setFormState((prev) => ({
                        ...prev,
                        quantity: e.target.value,
                      }));
                    }}
                  />
                )}
              </Field>
              {renderErrorChip("quantity")}
            </div>

            <div>
              <Field
                name="unitMaterialUnit"
                label={`${t("businessDepartment.unitReport.sections.materials.fields.unit")} *`}
                htmlFor="input-unitMaterialUnit"
              >
                {() => (
                  <Input
                    id="input-unitMaterialUnit"
                    name="unit"
                    dir="auto"
                    value={formState.unit}
                    onChange={(e) => {
                      clearErrorsForField("unit");
                      setFormState((prev) => ({
                        ...prev,
                        unit: e.target.value,
                      }));
                    }}
                    placeholder={t(
                      "businessDepartment.unitReport.sections.materials.fields.unitPlaceholder",
                    )}
                  />
                )}
              </Field>
              {renderErrorChip("unit")}
            </div>

            {formState.transaction_type === "receipt" ? (
              <div>
                <Field
                  name="unitMaterialSupplier"
                  label={t(
                    "businessDepartment.unitReport.sections.materials.fields.supplier",
                  )}
                  htmlFor="input-unitMaterialSupplier"
                >
                  {() => (
                    <Input
                      id="input-unitMaterialSupplier"
                      name="supplier"
                      dir="auto"
                      value={formState.supplier}
                      onChange={(e) => {
                        clearErrorsForField("supplier");
                        setFormState((prev) => ({
                          ...prev,
                          supplier: e.target.value,
                        }));
                      }}
                      placeholder={t(
                        "businessDepartment.unitReport.sections.materials.fields.supplierPlaceholder",
                      )}
                    />
                  )}
                </Field>
                {renderErrorChip("supplier")}
              </div>
            ) : null}

            <div>
              <Field
                name="unitMaterialWarehouseDocumentReference"
                label={
                  formState.transaction_type === "receipt"
                    ? `${t("businessDepartment.unitReport.sections.materials.fields.warehouseDocumentReference")} *`
                    : t(
                        "businessDepartment.unitReport.sections.materials.fields.warehouseDocumentReference",
                      )
                }
                htmlFor="input-unitMaterialWarehouseDocumentReference"
              >
                {() => (
                  <Input
                    id="input-unitMaterialWarehouseDocumentReference"
                    name="warehouse_document_reference"
                    dir="ltr"
                    value={formState.warehouse_document_reference}
                    onChange={(e) => {
                      clearErrorsForField("warehouse_document_reference");
                      setFormState((prev) => ({
                        ...prev,
                        warehouse_document_reference: e.target.value,
                      }));
                    }}
                    placeholder={t(
                      "businessDepartment.unitReport.sections.materials.fields.warehouseDocumentReferencePlaceholder",
                    )}
                  />
                )}
              </Field>
              {renderErrorChip("warehouse_document_reference")}
            </div>

            {formState.transaction_type === "consumption" ? (
              <div className="sm:col-span-2">
                <Field
                  name="unitMaterialConsumptionLocation"
                  label={`${t("businessDepartment.unitReport.sections.materials.fields.consumptionLocation")} *`}
                  htmlFor="input-unitMaterialConsumptionLocation"
                >
                  {() => (
                    <Input
                      id="input-unitMaterialConsumptionLocation"
                      name="consumption_location"
                      dir="auto"
                      value={formState.consumption_location}
                      onChange={(e) => {
                        clearErrorsForField("consumption_location");
                        setFormState((prev) => ({
                          ...prev,
                          consumption_location: e.target.value,
                        }));
                      }}
                      placeholder={t(
                        "businessDepartment.unitReport.sections.materials.fields.consumptionLocationPlaceholder",
                      )}
                    />
                  )}
                </Field>
                {renderErrorChip("consumption_location")}
              </div>
            ) : null}
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button
              id="button-cancelUnitMaterialRow"
              type="button"
              size="sm"
              variant="ghost"
              onClick={handleCancelForm}
            >
              {t("common.cancel")}
            </Button>
            <Button
              id="button-saveUnitMaterialRow"
              data-testid="save-unit-material-row"
              type="submit"
              size="sm"
              disabled={isMutating}
            >
              {isMutating ? t("common.loading") : t("common.save")}
            </Button>
          </div>
        </form>
      ) : null}

      {materialsQuery.isLoading ? (
        <p className="text-xs text-muted-foreground">{t("common.loading")}</p>
      ) : rows.length === 0 ? (
        <p
          id="text-unitMaterialsEmpty"
          data-testid="unit-materials-empty"
          className="py-4 text-center text-sm text-muted-foreground"
        >
          {t("businessDepartment.unitReport.sections.materials.empty")}
        </p>
      ) : (
        <div
          tabIndex={0}
          role="region"
          aria-labelledby="text-unitMaterialsTitle"
          className="overflow-x-auto rounded-md border border-border"
        >
          <table
            id="table-unitReportMaterials"
            data-testid="unit-materials-table"
            className="w-full min-w-[840px] border-separate border-spacing-0 text-start text-xs"
          >
            <caption className="sr-only">
              {t("businessDepartment.unitReport.sections.materials.title")}
            </caption>
            <thead className="sticky inset-block-start-0 z-10">
              <tr className="border-b bg-muted/40 text-muted-foreground">
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.materials.fields.transactionType",
                  )}
                </th>
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.materials.fields.materialDescription",
                  )}
                </th>
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.materials.fields.quantity",
                  )}
                </th>
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.materials.fields.unit",
                  )}
                </th>
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.materials.fields.supplier",
                  )}
                </th>
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.materials.fields.warehouseDocumentReference",
                  )}
                </th>
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.materials.fields.consumptionLocation",
                  )}
                </th>
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.materials.fields.receiptEvidence",
                  )}
                </th>
                {canEdit ? (
                  <th className="p-2 text-end font-medium">
                    {t("common.actions")}
                  </th>
                ) : null}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const matLabel = row.material_code
                  ? `${row.material_code} — ${row.material_description}`
                  : row.material_description;
                const isReceipt = row.transaction_type === "receipt";
                const evidenceCode =
                  row.receipt_evidence ??
                  (isReceipt
                    ? row.receipt_resolved
                      ? "resolved"
                      : "unresolved_reference"
                    : null);

                return (
                  <tr
                    key={row.id}
                    data-testid={`unit-material-row-${row.id}`}
                    className="border-b last:border-b-0 hover:bg-muted/20"
                  >
                    <td className="p-2">
                      <span
                        data-testid={`unit-material-tx-badge-${row.id}`}
                        className={
                          isReceipt
                            ? "inline-flex items-center rounded-md border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[11px] font-medium text-emerald-700 dark:text-emerald-300"
                            : "inline-flex items-center rounded-md border border-sky-500/30 bg-sky-500/10 px-2 py-0.5 text-[11px] font-medium text-sky-700 dark:text-sky-300"
                        }
                      >
                        {t(
                          `businessDepartment.unitReport.sections.materials.transactionTypes.${row.transaction_type}`,
                        )}
                      </span>
                    </td>
                    <td className="p-2 font-medium" dir="auto">
                      {matLabel}
                    </td>
                    <td className="p-2 font-mono">{row.quantity}</td>
                    <td className="p-2" dir="auto">
                      {row.unit}
                    </td>
                    <td className="p-2" dir="auto">
                      {row.supplier || "—"}
                    </td>
                    <td className="p-2 font-mono" dir="ltr">
                      {row.warehouse_document_reference || "—"}
                    </td>
                    <td className="p-2" dir="auto">
                      {row.consumption_location || "—"}
                    </td>
                    <td className="p-2">
                      {evidenceCode === "resolved" ? (
                        <span
                          data-testid={`unit-material-evidence-${row.id}`}
                          data-evidence="resolved"
                          className="inline-flex items-center rounded-md border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[11px] font-medium text-emerald-700 dark:text-emerald-300"
                        >
                          {t(
                            "businessDepartment.unitReport.sections.materials.evidence.resolved",
                          )}
                        </span>
                      ) : evidenceCode === "unresolved_reference" ? (
                        <span
                          data-testid={`unit-material-evidence-${row.id}`}
                          data-evidence="unresolved_reference"
                          className="inline-flex items-center rounded-md border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 text-[11px] font-medium text-amber-700 dark:text-amber-300"
                        >
                          {t(
                            "businessDepartment.unitReport.sections.materials.evidence.unresolved_reference",
                          )}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    {canEdit ? (
                      <td className="p-2 text-end">
                        <div className="inline-flex items-center gap-1">
                          <Button
                            id={`button-editUnitMaterialRow-${row.id}`}
                            data-testid={`edit-unit-material-row-${row.id}`}
                            type="button"
                            size="sm"
                            variant="ghost"
                            aria-label={t("common.edit")}
                            onClick={() => handleStartEdit(row)}
                          >
                            <Pencil className="h-3.5 w-3.5" />
                          </Button>
                          <Button
                            id={`button-deleteUnitMaterialRow-${row.id}`}
                            data-testid={`delete-unit-material-row-${row.id}`}
                            type="button"
                            size="sm"
                            variant="ghost"
                            aria-label={t("common.delete")}
                            disabled={deleteMutation.isPending}
                            onClick={() => void handleDeleteRow(row.id)}
                          >
                            <Trash2 className="h-3.5 w-3.5 text-destructive" />
                          </Button>
                        </div>
                      </td>
                    ) : null}
                  </tr>
                );
              })}
            </tbody>
            <tfoot>
              <tr
                data-testid="unit-materials-totals-row"
                className="border-t bg-muted/40 font-semibold text-foreground"
              >
                <td className="p-2" colSpan={canEdit ? 9 : 8}>
                  {t(
                    "businessDepartment.unitReport.sections.materials.totalsSummary",
                    {
                      receipts: counts.receipts,
                      consumptions: counts.consumptions,
                    },
                  )}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      )}
    </div>
  );
}
