import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Pencil, Plus, Trash2, X } from "lucide-react";

import {
  useCreateUnitReportMachinery,
  useDeleteUnitReportMachinery,
  useEffectiveReportingConfigurationQuery,
  useUnitReportMachineryQuery,
  useUpdateUnitReportMachinery,
} from "@/app/hooks/queries";
import {
  extractSectionErrors,
  type CanonicalUnit,
  type EffectiveStoppageReason,
  type SectionFieldError,
  type UnitReport,
  type UnitReportMachineryPayload,
  type UnitReportMachineryRow,
} from "@/app/lib/api/unit-reports";
import { Button, Field, Input, Select } from "@/components/form";
import { RowSyncStatusBadge } from "./row-sync-status-badge";
import type { SelectOption } from "@/components/form/Select";

export interface SectionMachineryProps {
  businessId: string;
  unit: CanonicalUnit;
  report: UnitReport;
}

interface MachineryFormState {
  row_number: string;
  equipment_type: string;
  equipment_ref: string;
  status_total: string;
  status_active: string;
  status_ready: string;
  status_inactive: string;
  status_under_repair: string;
  operating_hours: string;
  stoppage_hours: string;
  repair_hours: string;
  stoppage_reason_code: string;
}

const DEFAULT_STOPPAGE_REASONS: EffectiveStoppageReason[] = [
  {
    reason_code: "breakdown",
    reason_label: "Breakdown",
    reason_label_fa: "خرابی فنی",
    display_order: 1,
  },
  {
    reason_code: "fuel_shortage",
    reason_label: "Fuel shortage",
    reason_label_fa: "کمبود سوخت",
    display_order: 2,
  },
  {
    reason_code: "operator_absent",
    reason_label: "Operator absent",
    reason_label_fa: "نبود اپراتور",
    display_order: 3,
  },
  {
    reason_code: "weather",
    reason_label: "Adverse weather",
    reason_label_fa: "شرایط نامساعد جوی",
    display_order: 4,
  },
  {
    reason_code: "maintenance",
    reason_label: "Scheduled maintenance",
    reason_label_fa: "سرویس و نگهداری دوره‌ای",
    display_order: 5,
  },
  {
    reason_code: "material_wait",
    reason_label: "Waiting for material / front",
    reason_label_fa: "انتظار مصالح / جبهه کاری",
    display_order: 6,
  },
  {
    reason_code: "site_access",
    reason_label: "Site access blocked",
    reason_label_fa: "محدودیت دسترسی کارگاه",
    display_order: 7,
  },
  {
    reason_code: "other",
    reason_label: "Other",
    reason_label_fa: "سایر",
    display_order: 8,
  },
];

const EMPTY_MACHINERY_FORM: MachineryFormState = {
  row_number: "1",
  equipment_type: "",
  equipment_ref: "",
  status_total: "1",
  status_active: "1",
  status_ready: "0",
  status_inactive: "0",
  status_under_repair: "0",
  operating_hours: "8.00",
  stoppage_hours: "0.00",
  repair_hours: "0.00",
  stoppage_reason_code: "",
};

function parseIntField(raw: string): number {
  const trimmed = raw.trim();
  if (!trimmed) return 0;
  const num = Number(trimmed);
  if (!Number.isFinite(num)) return 0;
  return Math.trunc(num);
}

function parseHoursField(raw: string): number {
  const trimmed = raw.trim();
  if (!trimmed) return 0;
  const num = Number(trimmed);
  if (!Number.isFinite(num)) return 0;
  return num;
}

export function SectionMachinery({
  businessId,
  unit,
  report,
}: SectionMachineryProps) {
  const { t, i18n } = useTranslation();

  const canEdit =
    report.capabilities.can_edit &&
    (report.status === "draft" || report.status === "rejected");

  const machineryQuery = useUnitReportMachineryQuery(
    businessId,
    unit,
    report.id,
  );
  const rows = machineryQuery.data ?? [];

  const effectiveConfigQuery = useEffectiveReportingConfigurationQuery(
    businessId,
    report.report_date,
  );

  const stoppageReasons = useMemo<EffectiveStoppageReason[]>(() => {
    const raw = effectiveConfigQuery.data?.stoppage_reasons;
    if (raw && raw.length > 0) {
      return [...raw].sort(
        (a, b) =>
          (a.display_order ?? 0) - (b.display_order ?? 0) ||
          a.reason_code.localeCompare(b.reason_code),
      );
    }
    return DEFAULT_STOPPAGE_REASONS;
  }, [effectiveConfigQuery.data?.stoppage_reasons]);

  const reasonOptions: SelectOption[] = useMemo(() => {
    const isFa = (i18n.language || "fa").startsWith("fa");
    const opts: SelectOption[] = [
      {
        value: "",
        label: t(
          "businessDepartment.unitReport.sections.machinery.fields.noStoppageReason",
        ),
      },
    ];
    for (const item of stoppageReasons) {
      const label = isFa
        ? item.reason_label_fa || item.reason_label || item.reason_code
        : item.reason_label || item.reason_label_fa || item.reason_code;
      opts.push({
        value: item.reason_code,
        label,
      });
    }
    return opts;
  }, [stoppageReasons, i18n.language, t]);

  const reasonLabelMap = useMemo(() => {
    const isFa = (i18n.language || "fa").startsWith("fa");
    const map = new Map<string, string>();
    for (const item of stoppageReasons) {
      const label = isFa
        ? item.reason_label_fa || item.reason_label || item.reason_code
        : item.reason_label || item.reason_label_fa || item.reason_code;
      map.set(item.reason_code, label);
    }
    return map;
  }, [stoppageReasons, i18n.language]);

  const createMutation = useCreateUnitReportMachinery(
    businessId,
    unit,
    report.id,
  );
  const updateMutation = useUpdateUnitReportMachinery(
    businessId,
    unit,
    report.id,
  );
  const deleteMutation = useDeleteUnitReportMachinery(
    businessId,
    unit,
    report.id,
  );

  const [formOpen, setFormOpen] = useState(false);
  const [editingRowId, setEditingRowId] = useState<string | null>(null);
  const [formState, setFormState] = useState<MachineryFormState>(
    EMPTY_MACHINERY_FORM,
  );
  const [fieldErrors, setFieldErrors] = useState<
    Record<string, SectionFieldError[]>
  >({});
  const [bannerError, setBannerError] = useState<{
    code: string | null;
    message: string;
  } | null>(null);

  const totals = useMemo(() => {
    let statusTotal = 0;
    let statusActive = 0;
    let statusReady = 0;
    let statusInactive = 0;
    let statusUnderRepair = 0;
    let operatingHours = 0;
    let stoppageHours = 0;
    let repairHours = 0;

    for (const r of rows) {
      statusTotal += Number(r.status_total || 0);
      statusActive += Number(r.status_active || 0);
      statusReady += Number(r.status_ready || 0);
      statusInactive += Number(r.status_inactive || 0);
      statusUnderRepair += Number(r.status_under_repair || 0);
      operatingHours += Number(r.operating_hours || 0);
      stoppageHours += Number(r.stoppage_hours || 0);
      repairHours += Number(r.repair_hours || 0);
    }

    return {
      statusTotal,
      statusActive,
      statusReady,
      statusInactive,
      statusUnderRepair,
      operatingHours,
      stoppageHours,
      repairHours,
    };
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
    const sectionKey = `businessDepartment.unitReport.sections.machinery.errors.${err.code}`;
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
        id={`chip-unitMachineryError-${field}`}
        data-testid={`machinery-error-chip-${field}`}
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
    setFormState({
      ...EMPTY_MACHINERY_FORM,
      row_number: String(rows.length + 1),
    });
    setFieldErrors({});
    setBannerError(null);
    setFormOpen(true);
  }

  function handleStartEdit(row: UnitReportMachineryRow) {
    setEditingRowId(row.id);
    setFormState({
      row_number: String(row.row_number ?? 1),
      equipment_type: row.equipment_type ?? "",
      equipment_ref: row.equipment_ref ?? "",
      status_total: String(row.status_total ?? 0),
      status_active: String(row.status_active ?? 0),
      status_ready: String(row.status_ready ?? 0),
      status_inactive: String(row.status_inactive ?? 0),
      status_under_repair: String(row.status_under_repair ?? 0),
      operating_hours:
        row.operating_hours != null ? String(row.operating_hours) : "0.00",
      stoppage_hours:
        row.stoppage_hours != null ? String(row.stoppage_hours) : "0.00",
      repair_hours:
        row.repair_hours != null ? String(row.repair_hours) : "0.00",
      stoppage_reason_code: row.stoppage_reason_code ?? "",
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

    const opHours = parseHoursField(formState.operating_hours);
    const stopHours = parseHoursField(formState.stoppage_hours);
    const repHours = parseHoursField(formState.repair_hours);
    const reasonCode = formState.stoppage_reason_code.trim();

    const localErrors: Record<string, SectionFieldError[]> = {};
    if (opHours + stopHours + repHours > 24) {
      localErrors.operating_hours = [
        {
          field: "operating_hours",
          code: "hours_exceed_day_limit",
          message: t(
            "businessDepartment.unitReport.sections.machinery.errors.hours_exceed_day_limit",
          ),
        },
      ];
    }
    if (stopHours > 0 && !reasonCode) {
      localErrors.stoppage_reason_code = [
        {
          field: "stoppage_reason_code",
          code: "stoppage_reason_required_when_stoppage_gt_zero",
          message: t(
            "businessDepartment.unitReport.sections.machinery.errors.stoppage_reason_required_when_stoppage_gt_zero",
          ),
        },
      ];
    }

    if (Object.keys(localErrors).length > 0) {
      setFieldErrors(localErrors);
    }

    const payload: UnitReportMachineryPayload = {
      row_number: Math.max(1, parseIntField(formState.row_number)),
      equipment_type: formState.equipment_type.trim(),
      equipment_ref: formState.equipment_ref.trim() || null,
      status_total: parseIntField(formState.status_total),
      status_active: parseIntField(formState.status_active),
      status_ready: parseIntField(formState.status_ready),
      status_inactive: parseIntField(formState.status_inactive),
      status_under_repair: parseIntField(formState.status_under_repair),
      operating_hours: formState.operating_hours.trim() || "0.00",
      stoppage_hours: formState.stoppage_hours.trim() || "0.00",
      repair_hours: formState.repair_hours.trim() || "0.00",
      stoppage_reason_code: reasonCode,
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
      setFormState(EMPTY_MACHINERY_FORM);
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
      id="section-unitReportMachinery"
      data-testid="unit-section-machinery"
      className="space-y-4 rounded-lg border border-border/70 bg-background p-4"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3
            id="text-unitMachineryTitle"
            className="text-base font-semibold tracking-tight"
          >
            {t("businessDepartment.unitReport.sections.machinery.title")}
          </h3>
          <p className="text-xs text-muted-foreground">
            {t("businessDepartment.unitReport.sections.machinery.subtitle")}
          </p>
        </div>

        {canEdit && !formOpen ? (
          <Button
            id="button-addUnitMachineryRow"
            data-testid="add-unit-machinery-row"
            type="button"
            size="sm"
            onClick={handleOpenNew}
          >
            <Plus className="me-1.5 h-4 w-4" />
            {t("businessDepartment.unitReport.sections.machinery.addRow")}
          </Button>
        ) : null}
      </div>

      {bannerError ? (
        <div
          id="alert-unitMachinerySectionError"
          data-testid="machinery-section-banner-error"
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
          id="form-unitMachineryRow"
          data-testid="unit-machinery-row-form"
          onSubmit={(e) => void handleSaveRow(e)}
          className="space-y-4 rounded-lg border border-border bg-muted/20 p-4"
          noValidate
        >
          <div className="flex items-center justify-between border-b border-border/60 pb-2">
            <h4 className="text-sm font-semibold">
              {editingRowId
                ? t("businessDepartment.unitReport.sections.machinery.editRow")
                : t("businessDepartment.unitReport.sections.machinery.addRow")}
            </h4>
            <Button
              id="button-closeUnitMachineryForm"
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
              <Field
                name="unitMachineryRowNumber"
                label={t(
                  "businessDepartment.unitReport.sections.machinery.fields.rowNumber",
                )}
                htmlFor="input-unitMachineryRowNumber"
              >
                {() => (
                  <Input
                    id="input-unitMachineryRowNumber"
                    name="row_number"
                    type="number"
                    min={1}
                    step={1}
                    value={formState.row_number}
                    onChange={(e) => {
                      clearErrorsForField("row_number");
                      setFormState((prev) => ({
                        ...prev,
                        row_number: e.target.value,
                      }));
                    }}
                  />
                )}
              </Field>
              {renderErrorChip("row_number")}
            </div>

            <div>
              <Field
                name="unitMachineryEquipmentType"
                label={`${t("businessDepartment.unitReport.sections.machinery.fields.equipmentType")} *`}
                htmlFor="input-unitMachineryEquipmentType"
              >
                {() => (
                  <Input
                    id="input-unitMachineryEquipmentType"
                    name="equipment_type"
                    dir="auto"
                    value={formState.equipment_type}
                    onChange={(e) => {
                      clearErrorsForField("equipment_type");
                      setFormState((prev) => ({
                        ...prev,
                        equipment_type: e.target.value,
                      }));
                    }}
                    placeholder={t(
                      "businessDepartment.unitReport.sections.machinery.fields.equipmentTypePlaceholder",
                    )}
                  />
                )}
              </Field>
              {renderErrorChip("equipment_type")}
            </div>

            <div className="sm:col-span-2">
              <Field
                name="unitMachineryEquipmentRef"
                label={t(
                  "businessDepartment.unitReport.sections.machinery.fields.equipmentRef",
                )}
                htmlFor="input-unitMachineryEquipmentRef"
              >
                {() => (
                  <Input
                    id="input-unitMachineryEquipmentRef"
                    name="equipment_ref"
                    dir="ltr"
                    value={formState.equipment_ref}
                    onChange={(e) => {
                      clearErrorsForField("equipment_ref");
                      setFormState((prev) => ({
                        ...prev,
                        equipment_ref: e.target.value,
                      }));
                    }}
                    placeholder={t(
                      "businessDepartment.unitReport.sections.machinery.fields.equipmentRefPlaceholder",
                    )}
                  />
                )}
              </Field>
              {renderErrorChip("equipment_ref")}
            </div>

            <div>
              <Field
                name="unitMachineryStatusTotal"
                label={t(
                  "businessDepartment.unitReport.sections.machinery.fields.statusTotal",
                )}
                htmlFor="input-unitMachineryStatusTotal"
              >
                {() => (
                  <Input
                    id="input-unitMachineryStatusTotal"
                    name="status_total"
                    type="number"
                    min={0}
                    step={1}
                    value={formState.status_total}
                    onChange={(e) => {
                      clearErrorsForField("status_total");
                      setFormState((prev) => ({
                        ...prev,
                        status_total: e.target.value,
                      }));
                    }}
                  />
                )}
              </Field>
              {renderErrorChip("status_total")}
            </div>

            <div>
              <Field
                name="unitMachineryStatusActive"
                label={t(
                  "businessDepartment.unitReport.sections.machinery.fields.statusActive",
                )}
                htmlFor="input-unitMachineryStatusActive"
              >
                {() => (
                  <Input
                    id="input-unitMachineryStatusActive"
                    name="status_active"
                    type="number"
                    min={0}
                    step={1}
                    value={formState.status_active}
                    onChange={(e) => {
                      clearErrorsForField("status_active");
                      setFormState((prev) => ({
                        ...prev,
                        status_active: e.target.value,
                      }));
                    }}
                  />
                )}
              </Field>
              {renderErrorChip("status_active")}
            </div>

            <div>
              <Field
                name="unitMachineryStatusReady"
                label={t(
                  "businessDepartment.unitReport.sections.machinery.fields.statusReady",
                )}
                htmlFor="input-unitMachineryStatusReady"
              >
                {() => (
                  <Input
                    id="input-unitMachineryStatusReady"
                    name="status_ready"
                    type="number"
                    min={0}
                    step={1}
                    value={formState.status_ready}
                    onChange={(e) => {
                      clearErrorsForField("status_ready");
                      setFormState((prev) => ({
                        ...prev,
                        status_ready: e.target.value,
                      }));
                    }}
                  />
                )}
              </Field>
              {renderErrorChip("status_ready")}
            </div>

            <div>
              <Field
                name="unitMachineryStatusInactive"
                label={t(
                  "businessDepartment.unitReport.sections.machinery.fields.statusInactive",
                )}
                htmlFor="input-unitMachineryStatusInactive"
              >
                {() => (
                  <Input
                    id="input-unitMachineryStatusInactive"
                    name="status_inactive"
                    type="number"
                    min={0}
                    step={1}
                    value={formState.status_inactive}
                    onChange={(e) => {
                      clearErrorsForField("status_inactive");
                      setFormState((prev) => ({
                        ...prev,
                        status_inactive: e.target.value,
                      }));
                    }}
                  />
                )}
              </Field>
              {renderErrorChip("status_inactive")}
            </div>

            <div>
              <Field
                name="unitMachineryStatusUnderRepair"
                label={t(
                  "businessDepartment.unitReport.sections.machinery.fields.statusUnderRepair",
                )}
                htmlFor="input-unitMachineryStatusUnderRepair"
              >
                {() => (
                  <Input
                    id="input-unitMachineryStatusUnderRepair"
                    name="status_under_repair"
                    type="number"
                    min={0}
                    step={1}
                    value={formState.status_under_repair}
                    onChange={(e) => {
                      clearErrorsForField("status_under_repair");
                      setFormState((prev) => ({
                        ...prev,
                        status_under_repair: e.target.value,
                      }));
                    }}
                  />
                )}
              </Field>
              {renderErrorChip("status_under_repair")}
            </div>

            <div>
              <Field
                name="unitMachineryOperatingHours"
                label={t(
                  "businessDepartment.unitReport.sections.machinery.fields.operatingHours",
                )}
                htmlFor="input-unitMachineryOperatingHours"
              >
                {() => (
                  <Input
                    id="input-unitMachineryOperatingHours"
                    name="operating_hours"
                    type="number"
                    min={0}
                    max={24}
                    step="any"
                    value={formState.operating_hours}
                    onChange={(e) => {
                      clearErrorsForField("operating_hours");
                      setFormState((prev) => ({
                        ...prev,
                        operating_hours: e.target.value,
                      }));
                    }}
                  />
                )}
              </Field>
              {renderErrorChip("operating_hours")}
            </div>

            <div>
              <Field
                name="unitMachineryStoppageHours"
                label={t(
                  "businessDepartment.unitReport.sections.machinery.fields.stoppageHours",
                )}
                htmlFor="input-unitMachineryStoppageHours"
              >
                {() => (
                  <Input
                    id="input-unitMachineryStoppageHours"
                    name="stoppage_hours"
                    type="number"
                    min={0}
                    max={24}
                    step="any"
                    value={formState.stoppage_hours}
                    onChange={(e) => {
                      clearErrorsForField("stoppage_hours");
                      clearErrorsForField("operating_hours");
                      setFormState((prev) => ({
                        ...prev,
                        stoppage_hours: e.target.value,
                      }));
                    }}
                  />
                )}
              </Field>
              {renderErrorChip("stoppage_hours")}
            </div>

            <div>
              <Field
                name="unitMachineryRepairHours"
                label={t(
                  "businessDepartment.unitReport.sections.machinery.fields.repairHours",
                )}
                htmlFor="input-unitMachineryRepairHours"
              >
                {() => (
                  <Input
                    id="input-unitMachineryRepairHours"
                    name="repair_hours"
                    type="number"
                    min={0}
                    max={24}
                    step="any"
                    value={formState.repair_hours}
                    onChange={(e) => {
                      clearErrorsForField("repair_hours");
                      clearErrorsForField("operating_hours");
                      setFormState((prev) => ({
                        ...prev,
                        repair_hours: e.target.value,
                      }));
                    }}
                  />
                )}
              </Field>
              {renderErrorChip("repair_hours")}
            </div>

            <div className="sm:col-span-2">
              <Select
                id="select-unitMachineryStoppageReason"
                name="stoppage_reason_code"
                label={
                  parseHoursField(formState.stoppage_hours) > 0
                    ? `${t("businessDepartment.unitReport.sections.machinery.fields.stoppageReason")} *`
                    : t(
                        "businessDepartment.unitReport.sections.machinery.fields.stoppageReason",
                      )
                }
                value={formState.stoppage_reason_code}
                options={reasonOptions}
                onChange={(e) => {
                  clearErrorsForField("stoppage_reason_code");
                  setFormState((prev) => ({
                    ...prev,
                    stoppage_reason_code: e.target.value,
                  }));
                }}
              />
              {renderErrorChip("stoppage_reason_code")}
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button
              id="button-cancelUnitMachineryRow"
              type="button"
              size="sm"
              variant="ghost"
              onClick={handleCancelForm}
            >
              {t("common.cancel")}
            </Button>
            <Button
              id="button-saveUnitMachineryRow"
              data-testid="save-unit-machinery-row"
              type="submit"
              size="sm"
              disabled={isMutating}
            >
              {isMutating ? t("common.loading") : t("common.save")}
            </Button>
          </div>
        </form>
      ) : null}

      {machineryQuery.isLoading ? (
        <p className="text-xs text-muted-foreground">{t("common.loading")}</p>
      ) : rows.length === 0 ? (
        <p
          id="text-unitMachineryEmpty"
          data-testid="unit-machinery-empty"
          className="py-4 text-center text-sm text-muted-foreground"
        >
          {t("businessDepartment.unitReport.sections.machinery.empty")}
        </p>
      ) : (
        <div className="overflow-x-auto rounded-md border border-border">
          <table
            id="table-unitReportMachinery"
            data-testid="unit-machinery-table"
            className="w-full min-w-[960px] text-start text-xs"
          >
            <caption className="sr-only">
              {t("businessDepartment.unitReport.sections.machinery.title")}
            </caption>
            <thead>
              <tr className="border-b bg-muted/40 text-muted-foreground">
                <th className="p-2 text-start font-medium">#</th>
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.machinery.fields.equipmentType",
                  )}
                </th>
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.machinery.fields.equipmentRef",
                  )}
                </th>
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.machinery.fields.statusTotal",
                  )}
                </th>
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.machinery.fields.statusActive",
                  )}
                </th>
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.machinery.fields.statusReady",
                  )}
                </th>
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.machinery.fields.statusInactive",
                  )}
                </th>
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.machinery.fields.statusUnderRepair",
                  )}
                </th>
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.machinery.fields.operatingHours",
                  )}
                </th>
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.machinery.fields.stoppageHours",
                  )}
                </th>
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.machinery.fields.repairHours",
                  )}
                </th>
                <th className="p-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.machinery.fields.stoppageReason",
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
                const isFa = (i18n.language || "fa").startsWith("fa");
                const reasonText = row.stoppage_reason_code
                  ? (isFa
                      ? row.stoppage_reason_label_fa ||
                        row.stoppage_reason_label
                      : row.stoppage_reason_label ||
                        row.stoppage_reason_label_fa) ||
                    reasonLabelMap.get(row.stoppage_reason_code) ||
                    row.stoppage_reason_code
                  : "—";

                const eqIdentityLabel = row.equipment_code
                  ? `${row.equipment_code}${row.equipment_name ? ` — ${row.equipment_name}` : ""}`
                  : row.equipment_ref || "—";

                return (
                  <tr
                    key={row.id}
                    data-testid={`unit-machinery-row-${row.id}`}
                    className="border-b last:border-b-0 hover:bg-muted/20"
                  >
                    <td className="p-2 font-mono">
                      <div className="flex items-center gap-2">
                        <RowSyncStatusBadge
                          status={(row as UnitReportMachineryRow & { sync_status?: string }).sync_status ?? "synced"}
                        />
                        {(row as UnitReportMachineryRow & { field_error?: { field: string; code: string } }).field_error ? (
                          <p role="alert" data-testid="row-field-error" className="text-xs text-destructive">
                            {t("offline.fieldError", (row as unknown as { field_error: { field: string; code: string } }).field_error)}
                          </p>
                        ) : null}
                        <span>{row.row_number}</span>
                      </div>
                    </td>
                    <td className="p-2 font-medium" dir="auto">
                      {row.equipment_type}
                    </td>
                    <td className="p-2 font-mono text-muted-foreground" dir="auto">
                      {eqIdentityLabel}
                    </td>
                    <td className="p-2 font-mono">{row.status_total}</td>
                    <td className="p-2 font-mono">{row.status_active}</td>
                    <td className="p-2 font-mono">{row.status_ready}</td>
                    <td className="p-2 font-mono">{row.status_inactive}</td>
                    <td className="p-2 font-mono">{row.status_under_repair}</td>
                    <td className="p-2 font-mono">
                      {row.operating_hours ?? "0.00"}
                    </td>
                    <td className="p-2 font-mono">
                      {row.stoppage_hours ?? "0.00"}
                    </td>
                    <td className="p-2 font-mono">
                      {row.repair_hours ?? "0.00"}
                    </td>
                    <td className="p-2" dir="auto">
                      {reasonText}
                    </td>
                    {canEdit ? (
                      <td className="p-2 text-end">
                        <div className="inline-flex items-center gap-1">
                          <Button
                            id={`button-editUnitMachineryRow-${row.id}`}
                            data-testid={`edit-unit-machinery-row-${row.id}`}
                            type="button"
                            size="sm"
                            variant="ghost"
                            aria-label={t("common.edit")}
                            onClick={() => handleStartEdit(row)}
                          >
                            <Pencil className="h-3.5 w-3.5" />
                          </Button>
                          <Button
                            id={`button-deleteUnitMachineryRow-${row.id}`}
                            data-testid={`delete-unit-machinery-row-${row.id}`}
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
                data-testid="unit-machinery-totals-row"
                className="border-t bg-muted/40 font-semibold text-foreground"
              >
                <td className="p-2" colSpan={3}>
                  {t(
                    "businessDepartment.unitReport.sections.machinery.totalsLabel",
                  )}
                </td>
                <td className="p-2 font-mono">{totals.statusTotal}</td>
                <td className="p-2 font-mono">{totals.statusActive}</td>
                <td className="p-2 font-mono">{totals.statusReady}</td>
                <td className="p-2 font-mono">{totals.statusInactive}</td>
                <td className="p-2 font-mono">{totals.statusUnderRepair}</td>
                <td className="p-2 font-mono">
                  {totals.operatingHours.toFixed(2)}
                </td>
                <td className="p-2 font-mono">
                  {totals.stoppageHours.toFixed(2)}
                </td>
                <td className="p-2 font-mono">
                  {totals.repairHours.toFixed(2)}
                </td>
                <td className="p-2">—</td>
                {canEdit ? <td className="p-2" /> : null}
              </tr>
            </tfoot>
          </table>
        </div>
      )}
    </div>
  );
}
