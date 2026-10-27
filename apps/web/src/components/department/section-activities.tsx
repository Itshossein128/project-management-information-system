import { useMemo, useState, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Pencil, Plus, Trash2, X } from "lucide-react";

import {
  useCreateUnitReportActivity,
  useDeleteUnitReportActivity,
  useUnitReportActivitiesQuery,
  useUpdateUnitReportActivity,
} from "@/app/hooks/queries";
import {
  createActivity,
  fetchActivities,
  type Activity,
} from "@/app/lib/api/activities";
import {
  asList,
  createStakeholder,
  fetchProjectContractors,
} from "@/app/lib/api/central-data";
import {
  extractSectionErrors,
  type CanonicalUnit,
  type SectionFieldError,
  type UnitReport,
  type UnitReportActivityPayload,
  type UnitReportActivityRow,
  uploadUnitReportAttachment,
} from "@/app/lib/api/unit-reports";
import { createWBSNode, fetchWBSFlat } from "@/app/lib/api/wbs";
import { CONSTRUCTION_UNIT_OPTIONS } from "@/app/lib/construction-units";
import { RowSyncStatusBadge } from "./row-sync-status-badge";
import {
  Button,
  CreatableSelect,
  Field as BaseField,
  type FieldProps,
  Input,
  TextArea,
} from "@/components/form";
import type { SelectOption } from "@/components/form/Select";

function Field({ label, name, children, ...props }: Omit<FieldProps, "children" | "name"> & { name?: string; children: ReactNode | (() => ReactNode) }) {
  const resolvedName = name ?? `section-${String(label).replace(/\s+/g, "-")}`;
  return <BaseField {...props} name={resolvedName} label={label}>{typeof children === "function" ? children : () => children}</BaseField>;
}

export interface SectionActivitiesProps {
  businessId: string;
  unit: CanonicalUnit;
  report: UnitReport;
}

interface ActivityFormState {
  activity_ref: string;
  activity_description: string;
  shift: string;
  contractor_ref: string;
  crew_name: string;
  foreman_count: string;
  worker_count: string;
  parcel: string;
  block: string;
  floor: string;
  zone: string;
  quantity: string;
  unit: string;
  notes: string;
}

const EMPTY_ACTIVITY_FORM: ActivityFormState = {
  activity_ref: "",
  activity_description: "",
  shift: "shift_1",
  contractor_ref: "",
  crew_name: "",
  foreman_count: "0",
  worker_count: "1",
  parcel: "",
  block: "",
  floor: "",
  zone: "",
  quantity: "",
  unit: "m3",
  notes: "",
};

const UUID_REGEX =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function parseOptionalInt(raw: string): number | null {
  const trimmed = raw.trim();
  if (!trimmed) return null;
  const num = Number(trimmed);
  if (!Number.isFinite(num) || num < 0) return null;
  return Math.trunc(num);
}

export function SectionActivities({
  businessId,
  unit,
  report,
}: SectionActivitiesProps) {
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const canEdit =
    report.capabilities.can_edit &&
    (report.status === "draft" || report.status === "rejected");

  const activitiesSectionQuery = useUnitReportActivitiesQuery(
    businessId,
    unit,
    report.id,
    Boolean(report.id),
  );
  const rows = activitiesSectionQuery.data ?? [];

  const createMutation = useCreateUnitReportActivity(
    businessId,
    unit,
    report.id,
  );
  const updateMutation = useUpdateUnitReportActivity(
    businessId,
    unit,
    report.id,
  );
  const deleteMutation = useDeleteUnitReportActivity(
    businessId,
    unit,
    report.id,
  );

  // Project WBS activities for searchable creatable select
  const projectActivitiesQuery = useQuery({
    queryKey: ["activities-lite", businessId],
    queryFn: () => fetchActivities(businessId, { per_page: 500 }),
    enabled: Boolean(businessId),
  });

  // Project contractors for searchable creatable select
  const projectContractorsQuery = useQuery({
    queryKey: ["project-contractors", businessId],
    queryFn: async () => asList(await fetchProjectContractors(businessId)),
    enabled: Boolean(businessId),
  });

  const wbsActivityOptions = useMemo<SelectOption[]>(() => {
    const list: Activity[] = projectActivitiesQuery.data?.results ?? [];
    return list
      .filter((a) => a.status === "not_started" || a.status === "in_progress")
      .map((a) => ({
        value: String(a.activity_id),
        label: `${a.activity_code} — ${a.activity_name}`,
      }));
  }, [projectActivitiesQuery.data]);

  const activityById = useMemo(() => {
    const map = new Map<string, Activity>();
    for (const a of projectActivitiesQuery.data?.results ?? []) {
      map.set(String(a.activity_id), a);
    }
    return map;
  }, [projectActivitiesQuery.data]);

  const contractorOptions = useMemo<SelectOption[]>(() => {
    const list = asList(projectContractorsQuery.data);
    return list.map((c) => ({
      value: String(c.id),
      label: c.organization_name
        ? `${c.name} (${c.organization_name})`
        : c.name,
    }));
  }, [projectContractorsQuery.data]);

  const contractorLabelById = useMemo(() => {
    const map = new Map<string, string>();
    for (const c of asList(projectContractorsQuery.data)) {
      map.set(
        String(c.id),
        c.organization_name ? `${c.name} (${c.organization_name})` : c.name,
      );
    }
    return map;
  }, [projectContractorsQuery.data]);

  const shiftOptions = useMemo<SelectOption[]>(
    () => [
      {
        value: "shift_1",
        label: t(
          "businessDepartment.unitReport.sections.activities.shifts.shift_1",
        ),
      },
      {
        value: "shift_2",
        label: t(
          "businessDepartment.unitReport.sections.activities.shifts.shift_2",
        ),
      },
      {
        value: "shift_3",
        label: t(
          "businessDepartment.unitReport.sections.activities.shifts.shift_3",
        ),
      },
    ],
    [t],
  );

  const [form, setForm] = useState<ActivityFormState>(EMPTY_ACTIVITY_FORM);
  const [editingRowId, setEditingRowId] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<
    Record<string, SectionFieldError[]>
  >({});
  const [bannerError, setBannerError] = useState<{
    code: string | null;
    message: string;
  } | null>(null);
  const [attachmentFile, setAttachmentFile] = useState<File | null>(null);
  const [attachmentRowId, setAttachmentRowId] = useState("");
  const [attachmentMessage, setAttachmentMessage] = useState<string | null>(null);
  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!attachmentFile || !attachmentRowId) throw new Error("attachment_selection_required");
      if (!["image/jpeg", "image/png"].includes(attachmentFile.type)) {
        throw new Error("unsupported_file_format");
      }
      if (attachmentFile.size > 10 * 1024 * 1024) throw new Error("file_too_large");
      return uploadUnitReportAttachment(businessId, unit, report.id, {
        file: attachmentFile,
        rowId: attachmentRowId,
      });
    },
    onSuccess: () => {
      setAttachmentFile(null);
      setAttachmentRowId("");
      setAttachmentMessage(t("businessDepartment.unitReport.sections.attachments.saved", "تصویر ثبت شد؛ دریافت فایل به فضای ذخیره‌سازی پیکربندی‌شده وابسته است."));
    },
    onError: (err) => {
      const code = err instanceof Error ? err.message : "upload_failed";
      const parsed = extractSectionErrors(err);
      setAttachmentMessage(t(`businessDepartment.unitReport.sections.attachments.errors.${code}`, {
        defaultValue: parsed.topMessage || code,
      }));
    },
  });

  const computedHeadcount = useMemo(() => {
    const f = parseOptionalInt(form.foreman_count) ?? 0;
    const w = parseOptionalInt(form.worker_count) ?? 0;
    return f + w;
  }, [form.foreman_count, form.worker_count]);

  const translateErrorCode = (code: string, fallback?: string): string => {
    const sectionKey = `businessDepartment.unitReport.sections.activities.errors.${code}`;
    const sectionTranslated = t(sectionKey);
    if (sectionTranslated !== sectionKey) {
      return sectionTranslated;
    }
    const globalKey = `errors.${code}`;
    const globalTranslated = t(globalKey);
    if (globalTranslated !== globalKey) {
      return globalTranslated;
    }
    return fallback || code;
  };

  const clearFieldError = (field: string) => {
    setFieldErrors((prev) => {
      if (!prev[field]) return prev;
      const next = { ...prev };
      delete next[field];
      return next;
    });
  };

  const setFieldValue = <K extends keyof ActivityFormState>(
    field: K,
    value: ActivityFormState[K],
  ) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    clearFieldError(field);
    setBannerError(null);
  };

  const handleSelectWbsActivity = (nextActivityId: string) => {
    const found = activityById.get(nextActivityId);
    setForm((prev) => ({
      ...prev,
      activity_ref: nextActivityId,
      activity_description:
        prev.activity_description.trim() === "" && found
          ? found.activity_name
          : prev.activity_description,
    }));
    clearFieldError("activity_ref");
    setBannerError(null);
  };

  const handleCreateWbsActivityOption = async (
    rawQuery: string,
  ): Promise<SelectOption> => {
    const trimmed = rawQuery.trim();
    if (UUID_REGEX.test(trimmed)) {
      return { value: trimmed, label: trimmed };
    }
    let wbsNodes = await fetchWBSFlat(businessId);
    let wbsId = wbsNodes[0]?.wbs_id;
    if (!wbsId) {
      const createdWbs = await createWBSNode(businessId, {
        wbs_code: "1",
        wbs_name: trimmed,
        status: "active",
      });
      wbsId = createdWbs.wbs_id;
    }
    const code = `ACT-${Date.now().toString().slice(-5)}`;
    const created = await createActivity(businessId, {
      wbs_id: wbsId,
      activity_code: code,
      activity_name: trimmed,
      status: "in_progress",
    });
    await queryClient.invalidateQueries({
      queryKey: ["activities-lite", businessId],
    });
    if (!form.activity_description.trim()) {
      setForm((prev) => ({
        ...prev,
        activity_description: created.activity_name,
      }));
    }
    return {
      value: String(created.activity_id),
      label: `${created.activity_code} — ${created.activity_name}`,
    };
  };

  const handleCreateContractorOption = async (
    rawQuery: string,
  ): Promise<SelectOption> => {
    const trimmed = rawQuery.trim();
    if (UUID_REGEX.test(trimmed)) {
      return { value: trimmed, label: trimmed };
    }
    const created = await createStakeholder(businessId, {
      name: trimmed,
      role: "contractor",
      status: "active",
    });
    await queryClient.invalidateQueries({
      queryKey: ["project-contractors", businessId],
    });
    return {
      value: String(created.id),
      label: created.name,
    };
  };

  const resetForm = () => {
    setForm(EMPTY_ACTIVITY_FORM);
    setEditingRowId(null);
    setFieldErrors({});
    setBannerError(null);
  };

  const startEditRow = (row: UnitReportActivityRow) => {
    setEditingRowId(row.id);
    setFieldErrors({});
    setBannerError(null);
    setForm({
      activity_ref: row.activity_ref ?? "",
      activity_description: row.activity_description ?? "",
      shift: row.shift ?? "shift_1",
      contractor_ref: row.contractor_ref ?? "",
      crew_name: row.crew_name ?? "",
      foreman_count:
        row.foreman_count != null ? String(row.foreman_count) : "0",
      worker_count: row.worker_count != null ? String(row.worker_count) : "0",
      parcel: row.parcel ?? "",
      block: row.block ?? "",
      floor: row.floor ?? "",
      zone: row.zone ?? "",
      quantity: row.quantity != null ? String(row.quantity) : "",
      unit: row.unit ?? "",
      notes: row.notes ?? "",
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canEdit) return;

    setFieldErrors({});
    setBannerError(null);

    const payload: UnitReportActivityPayload = {
      activity_ref: form.activity_ref.trim() || null,
      activity_description: form.activity_description.trim(),
      shift: form.shift.trim(),
      contractor_ref: form.contractor_ref.trim() || null,
      crew_name: form.crew_name.trim(),
      foreman_count: parseOptionalInt(form.foreman_count),
      worker_count: parseOptionalInt(form.worker_count),
      parcel: form.parcel.trim() || null,
      block: form.block.trim() || null,
      floor: form.floor.trim() || null,
      zone: form.zone.trim() || null,
      quantity: form.quantity.trim() !== "" ? form.quantity.trim() : null,
      unit: form.unit.trim() || null,
      notes: form.notes.trim(),
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
      resetForm();
    } catch (err) {
      const parsed = extractSectionErrors(err);
      setFieldErrors(parsed.fieldErrors);
      const topCode = parsed.topCode ?? parsed.allErrors[0]?.code ?? null;
      const topMessage = topCode
        ? translateErrorCode(topCode, parsed.topMessage)
        : parsed.topMessage;
      setBannerError({ code: topCode, message: topMessage });
    }
  };

  const handleDeleteRow = async (rowId: string) => {
    if (!canEdit) return;
    setBannerError(null);
    try {
      await deleteMutation.mutateAsync(rowId);
      if (editingRowId === rowId) {
        resetForm();
      }
    } catch (err) {
      const parsed = extractSectionErrors(err);
      const topCode = parsed.topCode ?? parsed.allErrors[0]?.code ?? null;
      setBannerError({
        code: topCode,
        message: topCode
          ? translateErrorCode(topCode, parsed.topMessage)
          : parsed.topMessage,
      });
    }
  };

  const renderFieldErrorChip = (field: string) => {
    const errs = fieldErrors[field];
    if (!errs || errs.length === 0) return null;
    const first = errs[0]!;
    return (
      <div
        id={`chip-unitActivityError-${field}`}
        data-testid={`activity-error-chip-${field}`}
        data-error-code={first.code}
        role="alert"
        className="mt-1 inline-flex items-center gap-1.5 rounded-md border border-destructive/40 bg-destructive/10 px-2.5 py-1 text-xs font-medium text-destructive"
      >
        <span>{translateErrorCode(first.code, first.message)}</span>
      </div>
    );
  };

  const formatShiftLabel = (shiftValue: string): string => {
    const key = `businessDepartment.unitReport.sections.activities.shifts.${shiftValue}`;
    const translated = t(key);
    return translated !== key ? translated : shiftValue;
  };

  const isSaving = createMutation.isPending || updateMutation.isPending;

  return (
    <div
      id="section-unitReportActivities"
      data-testid="unit-section-activities"
      className="space-y-4 rounded-lg border border-border/80 bg-background p-4"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3
            id="text-unitSectionActivitiesTitle"
            className="text-base font-semibold"
          >
            {t("businessDepartment.unitReport.sections.activities.title")}
          </h3>
          <p className="text-xs text-muted-foreground">
            {t("businessDepartment.unitReport.sections.activities.subtitle")}
          </p>
        </div>
        <span
          id="badge-unitActivitiesCount"
          className="rounded-full bg-muted px-2.5 py-0.5 text-xs font-medium text-muted-foreground"
        >
          {t("businessDepartment.unitReport.sections.activities.rowCount", {
            count: rows.length,
          })}
        </span>
      </div>

      {bannerError ? (
        <div
          id="alert-unitActivitySectionError"
          data-testid="activity-section-error-banner"
          data-error-code={bannerError.code || undefined}
          role="alert"
          className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive"
        >
          <div className="flex items-center justify-between gap-2">
            <span>{bannerError.message}</span>
            {bannerError.code ? (
              <span className="font-mono text-xs opacity-75">
                ({bannerError.code})
              </span>
            ) : null}
          </div>
        </div>
      ) : null}

      {canEdit ? (
        <form
          id="form-unitReportActivityRow"
          data-testid="unit-activity-row-form"
          noValidate
          onSubmit={(e) => void handleSubmit(e)}
          className="space-y-4 rounded-lg border border-border/60 bg-muted/15 p-4"
        >
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {/* WBS Activity (searchable creatable select with Add inside open menu) */}
            <div id="container-unitActivityRef" className="sm:col-span-2">
              <CreatableSelect
                id="select-unitActivityRef"
                name="unitActivityRef"
                label={t(
                  "businessDepartment.unitReport.sections.activities.fields.activityRef",
                )}
                value={form.activity_ref}
                onChange={handleSelectWbsActivity}
                options={wbsActivityOptions}
                onCreateOption={handleCreateWbsActivityOption}
                placeholder={t(
                  "businessDepartment.unitReport.sections.activities.fields.activityRefPlaceholder",
                )}
                searchPlaceholder={t(
                  "businessDepartment.unitReport.sections.activities.fields.activityRefSearch",
                )}
                addLabel={t(
                  "businessDepartment.unitReport.sections.activities.fields.activityRefAdd",
                )}
                required
              />
              {renderFieldErrorChip("activity_ref")}
            </div>

            {/* Activity Description */}
            <div
              id="container-unitActivityDescription"
              className="sm:col-span-2"
            >
              <Field
                name="unitActivityDescription"
                label={t(
                  "businessDepartment.unitReport.sections.activities.fields.activityDescription",
                )}
                htmlFor="input-unitActivityDescription"
              >
                {() => (
                  <Input
                    id="input-unitActivityDescription"
                    name="unitActivityDescription"
                    dir="auto"
                    value={form.activity_description}
                    onChange={(e) =>
                      setFieldValue("activity_description", e.target.value)
                    }
                    placeholder={t(
                      "businessDepartment.unitReport.sections.activities.fields.activityDescriptionPlaceholder",
                    )}
                    required
                  />
                )}
              </Field>
              {renderFieldErrorChip("activity_description")}
            </div>

            {/* Shift (searchable creatable select) */}
            <div id="container-unitActivityShift">
              <CreatableSelect
                id="select-unitActivityShift"
                name="unitActivityShift"
                label={t(
                  "businessDepartment.unitReport.sections.activities.fields.shift",
                )}
                value={form.shift}
                onChange={(next) => setFieldValue("shift", next)}
                options={shiftOptions}
                placeholder={t(
                  "businessDepartment.unitReport.sections.activities.fields.shiftPlaceholder",
                )}
                required
              />
              {renderFieldErrorChip("shift")}
            </div>

            {/* Contractor (searchable creatable select with Add inside open menu) */}
            <div id="container-unitActivityContractor">
              <CreatableSelect
                id="select-unitActivityContractor"
                name="unitActivityContractor"
                label={t(
                  "businessDepartment.unitReport.sections.activities.fields.contractor",
                )}
                value={form.contractor_ref}
                onChange={(next) => setFieldValue("contractor_ref", next)}
                options={contractorOptions}
                onCreateOption={handleCreateContractorOption}
                placeholder={t(
                  "businessDepartment.unitReport.sections.activities.fields.contractorPlaceholder",
                )}
                searchPlaceholder={t(
                  "businessDepartment.unitReport.sections.activities.fields.contractorSearch",
                )}
                addLabel={t(
                  "businessDepartment.unitReport.sections.activities.fields.contractorAdd",
                )}
                required
              />
              {renderFieldErrorChip("contractor_ref")}
            </div>

            {/* Crew Name (separate from contractor) */}
            <div id="container-unitActivityCrewName">
              <Field
                name="unitActivityCrewName"
                label={t(
                  "businessDepartment.unitReport.sections.activities.fields.crewName",
                )}
                htmlFor="input-unitActivityCrewName"
              >
                {() => (
                  <Input
                    id="input-unitActivityCrewName"
                    name="unitActivityCrewName"
                    dir="auto"
                    value={form.crew_name}
                    onChange={(e) => setFieldValue("crew_name", e.target.value)}
                    placeholder={t(
                      "businessDepartment.unitReport.sections.activities.fields.crewNamePlaceholder",
                    )}
                  />
                )}
              </Field>
              {renderFieldErrorChip("crew_name")}
            </div>

            {/* Foreman + Worker + Derived Headcount */}
            <div
              id="container-unitActivityHeadcounts"
              className="grid grid-cols-3 gap-2"
            >
              <Field
                name="unitActivityForemanCount"
                label={t(
                  "businessDepartment.unitReport.sections.activities.fields.foremanCount",
                )}
                htmlFor="input-unitActivityForemanCount"
              >
                {() => (
                  <Input
                    id="input-unitActivityForemanCount"
                    name="unitActivityForemanCount"
                    type="number"
                    min={0}
                    step={1}
                    value={form.foreman_count}
                    onChange={(e) =>
                      setFieldValue("foreman_count", e.target.value)
                    }
                  />
                )}
              </Field>
              <Field
                name="unitActivityWorkerCount"
                label={t(
                  "businessDepartment.unitReport.sections.activities.fields.workerCount",
                )}
                htmlFor="input-unitActivityWorkerCount"
              >
                {() => (
                  <Input
                    id="input-unitActivityWorkerCount"
                    name="unitActivityWorkerCount"
                    type="number"
                    min={0}
                    step={1}
                    value={form.worker_count}
                    onChange={(e) =>
                      setFieldValue("worker_count", e.target.value)
                    }
                  />
                )}
              </Field>
              <div className="flex flex-col justify-end">
                <span className="mb-1 text-xs text-muted-foreground">
                  {t(
                    "businessDepartment.unitReport.sections.activities.fields.headcount",
                  )}
                </span>
                <div
                  id="text-unitActivityHeadcount"
                  data-testid="unit-activity-headcount"
                  className="flex h-9 items-center rounded-md border border-border bg-muted/40 px-3 font-mono text-sm font-semibold"
                >
                  {computedHeadcount}
                </div>
              </div>
            </div>

            {/* Parcel */}
            <div id="container-unitActivityParcel">
              <Field
                name="unitActivityParcel"
                label={t(
                  "businessDepartment.unitReport.sections.activities.fields.parcel",
                )}
                htmlFor="input-unitActivityParcel"
              >
                {() => (
                  <Input
                    id="input-unitActivityParcel"
                    name="unitActivityParcel"
                    dir="auto"
                    value={form.parcel}
                    onChange={(e) => setFieldValue("parcel", e.target.value)}
                  />
                )}
              </Field>
            </div>

            {/* Block */}
            <div id="container-unitActivityBlock">
              <Field
                name="unitActivityBlock"
                label={t(
                  "businessDepartment.unitReport.sections.activities.fields.block",
                )}
                htmlFor="input-unitActivityBlock"
              >
                {() => (
                  <Input
                    id="input-unitActivityBlock"
                    name="unitActivityBlock"
                    dir="auto"
                    value={form.block}
                    onChange={(e) => setFieldValue("block", e.target.value)}
                  />
                )}
              </Field>
            </div>

            {/* Floor */}
            <div id="container-unitActivityFloor">
              <Field
                name="unitActivityFloor"
                label={t(
                  "businessDepartment.unitReport.sections.activities.fields.floor",
                )}
                htmlFor="input-unitActivityFloor"
              >
                {() => (
                  <Input
                    id="input-unitActivityFloor"
                    name="unitActivityFloor"
                    dir="auto"
                    value={form.floor}
                    onChange={(e) => setFieldValue("floor", e.target.value)}
                  />
                )}
              </Field>
            </div>

            {/* Location / Zone */}
            <div id="container-unitActivityZone">
              <Field
                name="unitActivityZone"
                label={t(
                  "businessDepartment.unitReport.sections.activities.fields.location",
                )}
                htmlFor="input-unitActivityZone"
              >
                {() => (
                  <Input
                    id="input-unitActivityZone"
                    name="unitActivityZone"
                    dir="auto"
                    value={form.zone}
                    onChange={(e) => setFieldValue("zone", e.target.value)}
                  />
                )}
              </Field>
            </div>

            {/* Completed Quantity */}
            <div id="container-unitActivityQuantity">
              <Field
                name="unitActivityQuantity"
                label={t(
                  "businessDepartment.unitReport.sections.activities.fields.quantity",
                )}
                htmlFor="input-unitActivityQuantity"
              >
                {() => (
                  <Input
                    id="input-unitActivityQuantity"
                    name="unitActivityQuantity"
                    type="number"
                    step="any"
                    value={form.quantity}
                    onChange={(e) => setFieldValue("quantity", e.target.value)}
                    required
                  />
                )}
              </Field>
              {renderFieldErrorChip("quantity")}
            </div>

            {/* Unit */}
            <div id="container-unitActivityUnit">
              <CreatableSelect
                id="select-unitActivityUnit"
                name="unitActivityUnit"
                label={t(
                  "businessDepartment.unitReport.sections.activities.fields.unit",
                )}
                value={form.unit}
                onChange={(next) => setFieldValue("unit", next)}
                options={CONSTRUCTION_UNIT_OPTIONS}
                placeholder={t(
                  "businessDepartment.activityLog.fields.unitPlaceholder",
                )}
                addPlaceholder={t(
                  "businessDepartment.activityLog.fields.unitCustomPlaceholder",
                )}
                addLabel={t("businessDepartment.activityLog.fields.unitAdd")}
                required
              />
              {renderFieldErrorChip("unit")}
            </div>

            {/* Notes */}
            <div id="container-unitActivityNotes" className="sm:col-span-2">
              <TextArea
                id="input-unitActivityNotes"
                name="unitActivityNotes"
                dir="auto"
                rows={1}
                label={t(
                  "businessDepartment.unitReport.sections.activities.fields.notes",
                )}
                value={form.notes}
                onChange={(e) => setFieldValue("notes", e.target.value)}
              />
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-end gap-2 border-t border-border/60 pt-3">
            {editingRowId ? (
              <Button
                id="button-cancelEditUnitActivityRow"
                type="button"
                size="sm"
                variant="ghost"
                onClick={resetForm}
              >
                <X className="size-4" aria-hidden />
                {t("common.cancel")}
              </Button>
            ) : null}
            <Button
              id="button-saveUnitActivityRow"
              data-testid="save-unit-activity-row-btn"
              type="submit"
              size="sm"
              disabled={isSaving}
            >
              <Plus className="size-4" aria-hidden />
              {isSaving
                ? t("common.loading")
                : editingRowId
                  ? t(
                      "businessDepartment.unitReport.sections.activities.updateRow",
                    )
                  : t(
                      "businessDepartment.unitReport.sections.activities.addRow",
                    )}
            </Button>
          </div>
        </form>
      ) : null}

      {/* Activity rows table */}
      <div className="overflow-x-auto rounded-md border border-border">
        <table
          id="table-unitReportActivities"
          data-testid="unit-activities-table"
          className="w-full min-w-[820px] text-start text-xs sm:text-sm"
        >
          <caption className="sr-only">
            {t("businessDepartment.unitReport.sections.activities.title")}
          </caption>
          <thead>
            <tr className="border-b bg-muted/40 text-muted-foreground">
              <th className="p-2 text-start font-medium">#</th>
              <th className="p-2 text-start font-medium">
                {t(
                  "businessDepartment.unitReport.sections.activities.columns.wbsActivity",
                )}
              </th>
              <th className="p-2 text-start font-medium">
                {t(
                  "businessDepartment.unitReport.sections.activities.columns.description",
                )}
              </th>
              <th className="p-2 text-start font-medium">
                {t(
                  "businessDepartment.unitReport.sections.activities.columns.shift",
                )}
              </th>
              <th
                data-testid="col-header-contractor"
                className="p-2 text-start font-medium"
              >
                {t(
                  "businessDepartment.unitReport.sections.activities.columns.contractor",
                )}
              </th>
              <th
                data-testid="col-header-crew"
                className="p-2 text-start font-medium"
              >
                {t(
                  "businessDepartment.unitReport.sections.activities.columns.crewName",
                )}
              </th>
              <th className="p-2 text-start font-medium">
                {t(
                  "businessDepartment.unitReport.sections.activities.columns.headcount",
                )}
              </th>
              <th className="p-2 text-start font-medium">
                {t(
                  "businessDepartment.unitReport.sections.activities.columns.parcel",
                )}
              </th>
              <th className="p-2 text-start font-medium">
                {t(
                  "businessDepartment.unitReport.sections.activities.columns.blockFloorZone",
                )}
              </th>
              <th className="p-2 text-start font-medium">
                {t(
                  "businessDepartment.unitReport.sections.activities.columns.quantity",
                )}
              </th>
              <th className="p-2 text-start font-medium">
                {t(
                  "businessDepartment.unitReport.sections.activities.columns.unit",
                )}
              </th>
              <th className="p-2 text-start font-medium">
                {t(
                  "businessDepartment.unitReport.sections.activities.columns.notes",
                )}
              </th>
              <th className="p-2 text-start font-medium">
                {t("common.status", "وضعیت")}
              </th>
              {canEdit ? (
                <th className="p-2 text-end font-medium">
                  {t("common.actions")}
                </th>
              ) : null}
            </tr>
          </thead>
          <tbody>
            {activitiesSectionQuery.isLoading ? (
              <tr>
                <td
                  colSpan={canEdit ? 14 : 13}
                  className="p-4 text-center text-muted-foreground"
                >
                  {t("common.loading")}
                </td>
              </tr>
            ) : rows.length === 0 ? (
              <tr>
                <td
                  id="text-unitActivitiesEmpty"
                  colSpan={canEdit ? 14 : 13}
                  className="p-4 text-center text-muted-foreground"
                >
                  {t("businessDepartment.unitReport.sections.activities.empty")}
                </td>
              </tr>
            ) : (
              rows.map((row) => {
                const wbsAct = activityById.get(row.activity_ref);
                const wbsLabel =
                  row.activity_code && row.activity_name
                    ? `${row.activity_code} — ${row.activity_name}`
                    : wbsAct
                      ? `${wbsAct.activity_code} — ${wbsAct.activity_name}`
                      : row.activity_ref || "—";
                const contractorLabel =
                  row.contractor_name ||
                  contractorLabelById.get(row.contractor_ref) ||
                  row.contractor_ref ||
                  "—";
                const locationJoined = [row.block, row.floor, row.zone]
                  .filter(Boolean)
                  .join(" / ");

                return (
                  <tr
                    key={row.id}
                    id={`row-unitActivity-${row.id}`}
                    data-testid="unit-activity-row"
                    className="border-b last:border-b-0 hover:bg-muted/20"
                  >
                    <td className="p-2 font-mono">{row.row_number}</td>
                    <td className="p-2" dir="auto">
                      {wbsLabel}
                    </td>
                    <td className="p-2" dir="auto">
                      {row.activity_description || "—"}
                    </td>
                    <td className="p-2">{formatShiftLabel(row.shift)}</td>
                    <td
                      data-testid="cell-activity-contractor"
                      className="p-2"
                      dir="auto"
                    >
                      {contractorLabel}
                    </td>
                    <td
                      data-testid="cell-activity-crew"
                      className="p-2"
                      dir="auto"
                    >
                      {row.crew_name || "—"}
                    </td>
                    <td className="p-2 font-mono">
                      {row.headcount ?? "—"}
                    </td>
                    <td className="p-2" dir="auto">
                      {row.parcel || "—"}
                    </td>
                    <td className="p-2" dir="auto">
                      {locationJoined || "—"}
                    </td>
                    <td className="p-2 font-mono">{row.quantity ?? "—"}</td>
                    <td className="p-2" dir="auto">
                      {row.unit || "—"}
                    </td>
                    <td className="p-2" dir="auto">
                      {row.notes || "—"}
                    </td>
                    <td className="p-2">
                      <RowSyncStatusBadge
                        status={(row as { sync_status?: string; _offline?: boolean }).sync_status ?? ((row as { _offline?: boolean })._offline ? "pending" : "synced")}
                      />
                      {(row as { field_error?: { field: string; code: string } }).field_error ? (
                        <p role="alert" data-testid="row-field-error" className="mt-1 text-xs text-destructive">
                          {t("offline.fieldError", (row as unknown as { field_error: { field: string; code: string } }).field_error)}
                        </p>
                      ) : null}
                    </td>
                    {canEdit ? (
                      <td className="p-2 text-end">
                        <div className="inline-flex items-center gap-1">
                          <Button
                            id={`button-editUnitActivity-${row.id}`}
                            type="button"
                            size="sm"
                            variant="ghost"
                            onClick={() => startEditRow(row)}
                            aria-label={t("common.edit")}
                          >
                            <Pencil className="size-3.5" aria-hidden />
                          </Button>
                          <Button
                            id={`button-deleteUnitActivity-${row.id}`}
                            type="button"
                            size="sm"
                            variant="ghost"
                            disabled={deleteMutation.isPending}
                            onClick={() => void handleDeleteRow(row.id)}
                            aria-label={t("common.delete")}
                          >
                            <Trash2
                              className="size-3.5 text-destructive"
                              aria-hidden
                            />
                          </Button>
                        </div>
                      </td>
                    ) : null}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
      {canEdit && rows.length > 0 ? (
        <form
          className="grid gap-3 rounded-lg border border-border/60 bg-muted/15 p-3 sm:grid-cols-3"
          onSubmit={(event) => { event.preventDefault(); uploadMutation.mutate(); }}
          data-testid="unit-activity-attachment-form"
        >
          <Field label={t("businessDepartment.unitReport.sections.attachments.activity", "فعالیت") }>
            <select
              className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
              value={attachmentRowId}
              onChange={(event) => setAttachmentRowId(event.target.value)}
              required
            >
              <option value="">{t("businessDepartment.unitReport.sections.attachments.selectActivity", "انتخاب فعالیت")}</option>
              {rows.map((row) => <option key={row.id} value={row.id}>{row.activity_description}</option>)}
            </select>
          </Field>
          <Field label={t("businessDepartment.unitReport.sections.attachments.label")}>
            <Input
              type="file"
              accept="image/jpeg,image/png"
              onChange={(event) => setAttachmentFile(event.target.files?.[0] ?? null)}
              required
            />
          </Field>
          <div className="flex flex-col justify-end gap-1">
            <Button type="submit" disabled={uploadMutation.isPending}>
              {t("businessDepartment.unitReport.sections.attachments.upload", "بارگذاری تصویر")}
            </Button>
            <span className="text-xs text-muted-foreground">{t("businessDepartment.unitReport.sections.attachments.hint")}</span>
          </div>
          {attachmentMessage ? <p className="text-xs sm:col-span-3" role="status">{attachmentMessage}</p> : null}
        </form>
      ) : null}
    </div>
  );
}
