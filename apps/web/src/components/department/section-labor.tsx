import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Pencil, Plus, Trash2, X } from "lucide-react";

import {
  useCreateUnitReportLabor,
  useDeleteUnitReportLabor,
  useEffectiveReportingConfigurationQuery,
  useUnitReportLaborQuery,
  useUpdateUnitReportLabor,
} from "@/app/hooks/queries";
import {
  asList,
  createStakeholder,
  fetchProjectContractors,
} from "@/app/lib/api/central-data";
import {
  extractSectionErrors,
  type CanonicalUnit,
  type EffectiveLaborTitle,
  type SectionFieldError,
  type UnitLaborCategory,
  type UnitReport,
  type UnitReportLaborPayload,
  type UnitReportLaborRow,
} from "@/app/lib/api/unit-reports";
import {
  Button,
  CreatableSelect,
  Field,
  Input,
  Select,
} from "@/components/form";
import type { SelectOption } from "@/components/form/Select";

export interface SectionLaborProps {
  businessId: string;
  unit: CanonicalUnit;
  report: UnitReport;
}

interface LaborFormState {
  labor_category: UnitLaborCategory;
  job_title: string;
  present_count: string;
  leave_count: string;
  overtime_hours: string;
  contractor_ref: string;
}

const EMPTY_LABOR_FORM: LaborFormState = {
  labor_category: "direct",
  job_title: "",
  present_count: "1",
  leave_count: "0",
  overtime_hours: "0",
  contractor_ref: "",
};

const UUID_REGEX =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function parseCountInput(raw: string): number {
  const trimmed = raw.trim();
  if (!trimmed) return 0;
  const num = Number(trimmed);
  if (!Number.isFinite(num)) return 0;
  return Math.trunc(num);
}

export function SectionLabor({
  businessId,
  unit,
  report,
}: SectionLaborProps) {
  const { t, i18n } = useTranslation();
  const queryClient = useQueryClient();

  const canEdit =
    report.capabilities.can_edit &&
    (report.status === "draft" || report.status === "rejected");

  const laborQuery = useUnitReportLaborQuery(businessId, unit, report.id);
  const rows = laborQuery.data ?? [];

  const effectiveConfigQuery = useEffectiveReportingConfigurationQuery(
    businessId,
    report.report_date,
  );
  const catalogTitles = useMemo<EffectiveLaborTitle[]>(() => {
    const raw = effectiveConfigQuery.data?.labor_titles ?? [];
    return [...raw].sort(
      (a, b) =>
        (a.display_order ?? 0) - (b.display_order ?? 0) ||
        a.title_code.localeCompare(b.title_code),
    );
  }, [effectiveConfigQuery.data?.labor_titles]);

  const standardShiftHours = useMemo(() => {
    const raw =
      effectiveConfigQuery.data?.man_hours_rule?.parameters
        ?.standard_shift_hours;
    const parsed = Number(raw);
    return Number.isFinite(parsed) && parsed > 0 ? parsed : 8;
  }, [effectiveConfigQuery.data?.man_hours_rule]);

  const projectContractorsQuery = useQuery({
    queryKey: ["project-contractors", businessId],
    queryFn: async () => asList(await fetchProjectContractors(businessId)),
    enabled: Boolean(businessId),
  });

  const createMutation = useCreateUnitReportLabor(businessId, unit, report.id);
  const updateMutation = useUpdateUnitReportLabor(businessId, unit, report.id);
  const deleteMutation = useDeleteUnitReportLabor(businessId, unit, report.id);

  const [formOpen, setFormOpen] = useState(false);
  const [editingRowId, setEditingRowId] = useState<string | null>(null);
  const [formState, setFormState] = useState<LaborFormState>(EMPTY_LABOR_FORM);
  const [fieldErrors, setFieldErrors] = useState<
    Record<string, SectionFieldError[]>
  >({});
  const [bannerError, setBannerError] = useState<{
    code: string | null;
    message: string;
  } | null>(null);

  const categoryOptions: SelectOption[] = useMemo(
    () => [
      {
        value: "direct",
        label: t("businessDepartment.unitReport.sections.labor.categories.direct"),
      },
      {
        value: "indirect",
        label: t("businessDepartment.unitReport.sections.labor.categories.indirect"),
      },
    ],
    [t],
  );

  const titleOptions: SelectOption[] = useMemo(() => {
    const filtered = catalogTitles.filter(
      (item) => item.category === formState.labor_category,
    );
    const isFa = (i18n.language || "fa").startsWith("fa");
    return filtered.map((item) => {
      const label = isFa
        ? item.title_label_fa || item.title_label || item.title_code
        : item.title_label || item.title_label_fa || item.title_code;
      return {
        value: label,
        label: `${item.display_order}. ${label}`,
      };
    });
  }, [catalogTitles, formState.labor_category, i18n.language]);

  const contractorOptions: SelectOption[] = useMemo(() => {
    const list = projectContractorsQuery.data ?? [];
    return list.map((c) => ({
      value: String(c.id),
      label: c.name,
    }));
  }, [projectContractorsQuery.data]);

  const contractorMap = useMemo(() => {
    const map = new Map<string, string>();
    for (const c of projectContractorsQuery.data ?? []) {
      map.set(String(c.id), c.name);
    }
    return map;
  }, [projectContractorsQuery.data]);

  const totals = useMemo(() => {
    let indirectPresent = 0;
    let indirectLeave = 0;
    let indirectOvertime = 0;
    let indirectManHours = 0;
    let directPresent = 0;
    let directLeave = 0;
    let directOvertime = 0;
    let directManHours = 0;

    for (const r of rows) {
      const present = Number(r.present_count || 0);
      const leave = Number(r.leave_count || 0);
      const overtime = Number(r.overtime_hours || 0);
      const mh = present * standardShiftHours + overtime;
      if (r.labor_category === "indirect") {
        indirectPresent += present;
        indirectLeave += leave;
        indirectOvertime += overtime;
        indirectManHours += mh;
      } else {
        directPresent += present;
        directLeave += leave;
        directOvertime += overtime;
        directManHours += mh;
      }
    }

    return {
      indirectPresent,
      indirectLeave,
      indirectOvertime,
      indirectManHours,
      directPresent,
      directLeave,
      directOvertime,
      directManHours,
      overallPresent: indirectPresent + directPresent,
      overallLeave: indirectLeave + directLeave,
      overallOvertime: indirectOvertime + directOvertime,
      overallManHours: indirectManHours + directManHours,
    };
  }, [rows, standardShiftHours]);

  function clearErrorsForField(field: string) {
    setFieldErrors((prev) => {
      if (!prev[field]) return prev;
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }

  function localizeError(err: SectionFieldError): string {
    const sectionKey = `businessDepartment.unitReport.sections.labor.errors.${err.code}`;
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
        id={`chip-unitLaborError-${field}`}
        data-testid={`labor-error-chip-${field}`}
        data-error-code={first.code}
        role="alert"
        className="mt-1 inline-flex items-center gap-1.5 rounded-md border border-destructive/40 bg-destructive/10 px-2 py-0.5 text-xs font-medium text-destructive"
      >
        <span>{localizeError(first)}</span>
      </div>
    );
  }

  async function handleCreateContractorOption(
    rawInput: string,
  ): Promise<SelectOption | undefined> {
    const trimmed = rawInput.trim();
    if (!trimmed) return undefined;
    if (UUID_REGEX.test(trimmed)) {
      return { value: trimmed, label: trimmed };
    }
    const created = await createStakeholder(businessId, {
      name: trimmed,
      role: "contractor",
    });
    await queryClient.invalidateQueries({
      queryKey: ["project-contractors", businessId],
    });
    return {
      value: String(created.id),
      label: created.name,
    };
  }

  function handleOpenNew() {
    setEditingRowId(null);
    const defaultCategory: UnitLaborCategory = "direct";
    const firstTitle = catalogTitles.find((t) => t.category === defaultCategory);
    const isFa = (i18n.language || "fa").startsWith("fa");
    const defaultTitleLabel = firstTitle
      ? isFa
        ? firstTitle.title_label_fa || firstTitle.title_label
        : firstTitle.title_label || firstTitle.title_label_fa
      : "";
    setFormState({
      ...EMPTY_LABOR_FORM,
      labor_category: defaultCategory,
      job_title: defaultTitleLabel,
    });
    setFieldErrors({});
    setBannerError(null);
    setFormOpen(true);
  }

  function handleStartEdit(row: UnitReportLaborRow) {
    setEditingRowId(row.id);
    setFormState({
      labor_category: row.labor_category,
      job_title: row.job_title ?? "",
      present_count: String(row.present_count ?? 0),
      leave_count: String(row.leave_count ?? 0),
      overtime_hours: String(row.overtime_hours ?? "0"),
      contractor_ref: row.contractor_ref ?? "",
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

    const payload: UnitReportLaborPayload = {
      labor_category: formState.labor_category,
      job_title: formState.job_title.trim(),
      present_count: parseCountInput(formState.present_count),
      leave_count: parseCountInput(formState.leave_count),
      overtime_hours: formState.overtime_hours.trim() || "0",
      contractor_ref: formState.contractor_ref.trim() || null,
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
      setFormState(EMPTY_LABOR_FORM);
    } catch (err) {
      const parsed = extractSectionErrors(err);
      setFieldErrors(parsed.fieldErrors);
      if (Object.keys(parsed.fieldErrors).length === 0 || parsed.topCode) {
        const bannerMsg = parsed.topCode
          ? localizeError({
              field: null,
              code: parsed.topCode,
              message: parsed.topMessage,
            })
          : parsed.topMessage;
        setBannerError({
          code: parsed.topCode,
          message: bannerMsg,
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

  const isSaving = createMutation.isPending || updateMutation.isPending;

  return (
    <section
      id="section-unitReportLabor"
      data-testid="unit-section-labor"
      aria-label={t("businessDepartment.unitReport.sections.labor.title")}
      className="space-y-4 rounded-xl border border-border bg-card/40 p-4"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h4 className="text-sm font-semibold text-foreground">
            {t("businessDepartment.unitReport.sections.labor.title")}
          </h4>
          <p className="text-xs text-muted-foreground">
            {t("businessDepartment.unitReport.sections.labor.subtitle")}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span
            id="badge-unitLaborCount"
            className="rounded-full bg-muted px-2.5 py-0.5 text-xs font-medium text-muted-foreground"
          >
            {t("businessDepartment.unitReport.sections.labor.rowCount", {
              count: rows.length,
            })}
          </span>
          {canEdit && !formOpen ? (
            <Button
              id="button-openUnitLaborForm"
              data-testid="add-unit-labor-row-button"
              type="button"
              size="sm"
              onClick={handleOpenNew}
            >
              <Plus className="me-1 size-4" />
              {t("businessDepartment.unitReport.sections.labor.addRow")}
            </Button>
          ) : null}
        </div>
      </div>

      {bannerError ? (
        <div
          id="alert-unitLaborSectionError"
          data-testid="labor-section-error-banner"
          data-error-code={bannerError.code ?? ""}
          role="alert"
          className="rounded-lg border border-destructive/40 bg-destructive/10 px-3 py-2 text-xs font-medium text-destructive"
        >
          {bannerError.message}
        </div>
      ) : null}

      {canEdit && formOpen ? (
        <form
          id="form-unitReportLabor"
          data-testid="unit-labor-row-form"
          onSubmit={(e) => void handleSaveRow(e)}
          className="space-y-4 rounded-lg border border-border bg-background p-4 shadow-xs"
          noValidate
        >
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {/* 1. Labor category */}
            <div>
              <Select
                id="select-unitLaborCategory"
                name="unitLaborCategory"
                label={t(
                  "businessDepartment.unitReport.sections.labor.fields.category",
                )}
                options={categoryOptions}
                value={formState.labor_category}
                onChange={(e) => {
                  const nextCat =
                    (e.target.value as UnitLaborCategory) || "direct";
                  clearErrorsForField("labor_category");
                  setFormState((prev) => ({
                    ...prev,
                    labor_category: nextCat,
                  }));
                }}
              />
              {renderErrorChip("labor_category")}
            </div>

            {/* 2. Catalog-constrained job title */}
            <div>
              <CreatableSelect
                id="select-unitLaborJobTitle"
                name="unitLaborJobTitle"
                label={t(
                  "businessDepartment.unitReport.sections.labor.fields.jobTitle",
                )}
                required
                options={titleOptions}
                value={formState.job_title}
                onChange={(val) => {
                  clearErrorsForField("job_title");
                  setFormState((prev) => ({ ...prev, job_title: val }));
                }}
                placeholder={t(
                  "businessDepartment.unitReport.sections.labor.fields.jobTitlePlaceholder",
                )}
                searchPlaceholder={t(
                  "businessDepartment.unitReport.sections.labor.fields.jobTitleSearch",
                )}
                addLabel={t(
                  "businessDepartment.unitReport.sections.labor.fields.jobTitleAdd",
                )}
              />
              {renderErrorChip("job_title")}
            </div>

            {/* 3. Optional project-scoped contractor */}
            <div>
              <CreatableSelect
                id="select-unitLaborContractor"
                name="unitLaborContractor"
                label={t(
                  "businessDepartment.unitReport.sections.labor.fields.contractor",
                )}
                options={contractorOptions}
                value={formState.contractor_ref}
                onChange={(val) => {
                  clearErrorsForField("contractor_ref");
                  setFormState((prev) => ({ ...prev, contractor_ref: val }));
                }}
                onCreateOption={handleCreateContractorOption}
                placeholder={t(
                  "businessDepartment.unitReport.sections.labor.fields.contractorPlaceholder",
                )}
                searchPlaceholder={t(
                  "businessDepartment.unitReport.sections.labor.fields.contractorSearch",
                )}
                addLabel={t(
                  "businessDepartment.unitReport.sections.labor.fields.contractorAdd",
                )}
              />
              {renderErrorChip("contractor_ref")}
            </div>

            {/* 4. Present count */}
            <div>
              <Field
                name="unitLaborPresentCount"
                label={t(
                  "businessDepartment.unitReport.sections.labor.fields.presentCount",
                )}
                htmlFor="input-unitLaborPresentCount"
              >
                {() => (
                  <Input
                    id="input-unitLaborPresentCount"
                    name="unitLaborPresentCount"
                    type="number"
                    step={1}
                    required
                    value={formState.present_count}
                    onChange={(e) => {
                      clearErrorsForField("present_count");
                      setFormState((prev) => ({
                        ...prev,
                        present_count: e.target.value,
                      }));
                    }}
                  />
                )}
              </Field>
              {renderErrorChip("present_count")}
            </div>

            {/* 5. Leave / absence count */}
            <div>
              <Field
                name="unitLaborLeaveCount"
                label={t(
                  "businessDepartment.unitReport.sections.labor.fields.leaveCount",
                )}
                htmlFor="input-unitLaborLeaveCount"
              >
                {() => (
                  <Input
                    id="input-unitLaborLeaveCount"
                    name="unitLaborLeaveCount"
                    type="number"
                    step={1}
                    value={formState.leave_count}
                    onChange={(e) => {
                      clearErrorsForField("leave_count");
                      setFormState((prev) => ({
                        ...prev,
                        leave_count: e.target.value,
                      }));
                    }}
                  />
                )}
              </Field>
              {renderErrorChip("leave_count")}
            </div>

            {/* 6. Overtime hours */}
            <div>
              <Field
                name="unitLaborOvertimeHours"
                label={t(
                  "businessDepartment.unitReport.sections.labor.fields.overtimeHours",
                )}
                htmlFor="input-unitLaborOvertimeHours"
              >
                {() => (
                  <Input
                    id="input-unitLaborOvertimeHours"
                    name="unitLaborOvertimeHours"
                    type="number"
                    step="0.25"
                    min="0"
                    value={formState.overtime_hours}
                    onChange={(e) => {
                      clearErrorsForField("overtime_hours");
                      setFormState((prev) => ({
                        ...prev,
                        overtime_hours: e.target.value,
                      }));
                    }}
                  />
                )}
              </Field>
              {renderErrorChip("overtime_hours")}
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <Button
              id="button-cancelUnitLaborRow"
              type="button"
              variant="outline"
              size="sm"
              onClick={handleCancelForm}
              disabled={isSaving}
            >
              <X className="me-1 size-4" />
              {t("common.cancel")}
            </Button>
            <Button
              id="button-saveUnitLaborRow"
              data-testid="save-unit-labor-row-button"
              type="submit"
              size="sm"
              disabled={isSaving}
            >
              {isSaving
                ? t("common.loading")
                : editingRowId
                  ? t("businessDepartment.unitReport.sections.labor.updateRow")
                  : t("common.save")}
            </Button>
          </div>
        </form>
      ) : null}

      {laborQuery.isLoading ? (
        <div className="py-4 text-xs text-muted-foreground">
          {t("common.loading")}
        </div>
      ) : rows.length === 0 ? (
        <p
          id="text-unitLaborEmpty"
          data-testid="unit-labor-empty"
          className="py-4 text-center text-xs text-muted-foreground"
        >
          {t("businessDepartment.unitReport.sections.labor.empty")}
        </p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border">
          <table
            id="table-unitReportLabor"
            data-testid="unit-labor-table"
            className="w-full text-xs"
          >
            <thead className="bg-muted/60 text-muted-foreground">
              <tr className="border-b border-border text-start">
                <th className="px-2.5 py-2 text-start font-medium">#</th>
                <th className="px-2.5 py-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.labor.columns.category",
                  )}
                </th>
                <th className="px-2.5 py-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.labor.columns.jobTitle",
                  )}
                </th>
                <th className="px-2.5 py-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.labor.columns.presentCount",
                  )}
                </th>
                <th className="px-2.5 py-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.labor.columns.leaveCount",
                  )}
                </th>
                <th className="px-2.5 py-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.labor.columns.overtimeHours",
                  )}
                </th>
                <th className="px-2.5 py-2 text-start font-medium">
                  {t(
                    "businessDepartment.unitReport.sections.labor.columns.contractor",
                  )}
                </th>
                {canEdit ? (
                  <th className="px-2.5 py-2 text-end font-medium">
                    {t("common.actions")}
                  </th>
                ) : null}
              </tr>
            </thead>
            <tbody className="divide-y divide-border bg-background">
              {rows.map((row, idx) => {
                const contractorDisplay =
                  row.contractor_name ||
                  (row.contractor_ref
                    ? contractorMap.get(String(row.contractor_ref))
                    : null) ||
                  "—";
                const categoryLabel =
                  row.labor_category === "indirect"
                    ? t(
                        "businessDepartment.unitReport.sections.labor.categories.indirect",
                      )
                    : t(
                        "businessDepartment.unitReport.sections.labor.categories.direct",
                      );

                return (
                  <tr
                    key={row.id}
                    data-testid={`unit-labor-row-${idx + 1}`}
                    className="hover:bg-muted/30"
                  >
                    <td className="px-2.5 py-2 font-mono text-muted-foreground">
                      {row.display_order || idx + 1}
                    </td>
                    <td className="px-2.5 py-2">{categoryLabel}</td>
                    <td className="px-2.5 py-2 font-medium">{row.job_title}</td>
                    <td className="px-2.5 py-2 font-mono">
                      {row.present_count}
                    </td>
                    <td className="px-2.5 py-2 font-mono">{row.leave_count}</td>
                    <td className="px-2.5 py-2 font-mono">
                      {row.overtime_hours}
                    </td>
                    <td className="px-2.5 py-2">{contractorDisplay}</td>
                    {canEdit ? (
                      <td className="px-2.5 py-2 text-end">
                        <div className="inline-flex items-center gap-1">
                          <Button
                            id={`button-editUnitLabor-${row.id}`}
                            type="button"
                            variant="ghost"
                            size="icon"
                            className="size-7"
                            onClick={() => handleStartEdit(row)}
                            aria-label={t(
                              "businessDepartment.unitReport.actionEdit",
                            )}
                          >
                            <Pencil className="size-3.5" />
                          </Button>
                          <Button
                            id={`button-deleteUnitLabor-${row.id}`}
                            type="button"
                            variant="ghost"
                            size="icon"
                            className="size-7 text-destructive"
                            disabled={deleteMutation.isPending}
                            onClick={() => void handleDeleteRow(row.id)}
                            aria-label={t(
                              "businessDepartment.unitReport.actionDelete",
                            )}
                          >
                            <Trash2 className="size-3.5" />
                          </Button>
                        </div>
                      </td>
                    ) : null}
                  </tr>
                );
              })}
            </tbody>
            <tfoot
              data-testid="unit-labor-totals-footer"
              className="border-t border-border bg-muted/40 font-medium text-foreground"
            >
              <tr>
                <td colSpan={3} className="px-2.5 py-1.5 text-start">
                  {t(
                    "businessDepartment.unitReport.sections.labor.totals.indirect",
                  )}
                </td>
                <td className="px-2.5 py-1.5 font-mono">
                  {totals.indirectPresent}
                </td>
                <td className="px-2.5 py-1.5 font-mono">
                  {totals.indirectLeave}
                </td>
                <td className="px-2.5 py-1.5 font-mono">
                  {totals.indirectOvertime.toFixed(2)}
                </td>
                <td colSpan={canEdit ? 2 : 1} className="px-2.5 py-1.5 font-mono">
                  {totals.indirectManHours.toFixed(2)} h
                </td>
              </tr>
              <tr>
                <td colSpan={3} className="px-2.5 py-1.5 text-start">
                  {t(
                    "businessDepartment.unitReport.sections.labor.totals.direct",
                  )}
                </td>
                <td className="px-2.5 py-1.5 font-mono">
                  {totals.directPresent}
                </td>
                <td className="px-2.5 py-1.5 font-mono">
                  {totals.directLeave}
                </td>
                <td className="px-2.5 py-1.5 font-mono">
                  {totals.directOvertime.toFixed(2)}
                </td>
                <td colSpan={canEdit ? 2 : 1} className="px-2.5 py-1.5 font-mono">
                  {totals.directManHours.toFixed(2)} h
                </td>
              </tr>
              <tr className="border-t border-border font-semibold">
                <td colSpan={3} className="px-2.5 py-1.5 text-start">
                  {t(
                    "businessDepartment.unitReport.sections.labor.totals.overall",
                  )}
                </td>
                <td className="px-2.5 py-1.5 font-mono">
                  {totals.overallPresent}
                </td>
                <td className="px-2.5 py-1.5 font-mono">
                  {totals.overallLeave}
                </td>
                <td className="px-2.5 py-1.5 font-mono">
                  {totals.overallOvertime.toFixed(2)}
                </td>
                <td colSpan={canEdit ? 2 : 1} className="px-2.5 py-1.5 font-mono">
                  {totals.overallManHours.toFixed(2)} h
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      )}
    </section>
  );
}
