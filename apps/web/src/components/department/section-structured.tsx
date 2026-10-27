import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { Trash2 } from "lucide-react";

import { ApiRequestError } from "@/app/lib/api-client";
import { getLocalSnapshot, getOperationsForReport } from "@/app/lib/offlineDB";
import { getStoredActorId, requireStoredActorId } from "@/app/lib/auth-storage";
import { queueUnitReportOperation } from "@/app/lib/offlineWrite";
import { reconcileServerWithLocalSnapshot } from "@/app/lib/offlineHydration";
import { RowSyncStatusBadge } from "./row-sync-status-badge";
import {
  createUnitSection,
  deleteUnitSection,
  extractSectionErrors,
  fetchUnitSection,
  type CanonicalUnit,
  type UnitReport,
  type UnitSectionRow,
} from "@/app/lib/api/unit-reports";
import { Button, Field as BaseField, Input, Select, type FieldProps } from "@/components/form";

function Field({ label, name, children, ...props }: Omit<FieldProps, "children" | "name"> & { name?: string; children: ReactNode | (() => ReactNode) }) {
  const resolvedName = name ?? `section-${String(label).replace(/\s+/g, "-")}`;
  return <BaseField {...props} name={resolvedName} label={label}>{typeof children === "function" ? children : () => children}</BaseField>;
}

export interface StructuredSectionProps {
  businessId: string;
  unit: CanonicalUnit;
  report: UnitReport;
  section: string;
  titleKey: string;
  emptyKey: string;
  addKey: string;
  fields: Array<"text" | "description" | "concrete" | "hse" | "barrier">;
}

export function StructuredSection({
  businessId,
  unit,
  report,
  section,
  titleKey,
  emptyKey,
  addKey,
  fields,
}: StructuredSectionProps) {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const editable = report.status === "draft" || report.status === "rejected";
  const [text, setText] = useState("");
  const [description, setDescription] = useState("");
  const [volume, setVolume] = useState("");
  const [location, setLocation] = useState("");
  const [quantity, setQuantity] = useState("");
  const [unitName, setUnitName] = useState("");
  const [notes, setNotes] = useState("");
  const [structuralElement, setStructuralElement] = useState("");
  const [parcel, setParcel] = useState("");
  const [zone, setZone] = useState("");
  const [block, setBlock] = useState("");
  const [floor, setFloor] = useState("");
  const [batchingPlant, setBatchingPlant] = useState("");
  const [deliveryNote, setDeliveryNote] = useState("");
  const [labSampleCode, setLabSampleCode] = useState("");
  const [samplingState, setSamplingState] = useState("not_sampled");
  const [testSheetCount, setTestSheetCount] = useState("");
  const [severity, setSeverity] = useState("minor");
  const [action, setAction] = useState("");
  const [kind, setKind] = useState("issue");
  const [ownerUser, setOwnerUser] = useState("");
  const [due, setDue] = useState("");
  const [error, setError] = useState<string | null>(null);
  const queryKey = ["unit-section", businessId, unit, report.id, section];

  const query = useQuery({
    networkMode: "always",
    queryKey,
    queryFn: async () => {
      const scopedSnapshot = async () => {
        const actor = getStoredActorId();
        if (!actor) return undefined;
        const snapshot = await getLocalSnapshot(report.id);
        return snapshot?.actor_id === actor && snapshot.project_id === String(businessId) && snapshot.unit === unit ? snapshot : undefined;
      };
      const applyLocal = async (rows: UnitSectionRow[]) => {
        const local = await scopedSnapshot();
        if (!local) return rows;
        return reconcileServerWithLocalSnapshot({}, rows, local, section, await getOperationsForReport(local.local_report_id)).rows as UnitSectionRow[];
      };
      const isOffline = typeof navigator !== "undefined" && !navigator.onLine;
      if (isOffline) {
        const local = await scopedSnapshot();
        const base = (local?.base_rows?.[section] ?? []) as UnitSectionRow[];
        return applyLocal(base);
      }
      try {
        const rows = await fetchUnitSection(businessId, unit, report.id, section);
        return applyLocal(rows);
      } catch (err) {
        const local = await scopedSnapshot();
        if (local) {
          const base = (local.base_rows?.[section] ?? []) as UnitSectionRow[];
          return applyLocal(base);
        }
        throw err;
      }
    },
  });

  const create = useMutation({
    networkMode: "always",
    mutationFn: async () => {
      const payload: Record<string, unknown> = { row_number: (query.data?.length ?? 0) + 1 };
      if (fields.includes("text")) payload.text = text;
      if (fields.includes("description")) {
        payload.activity_description = description;
        payload.location = location;
        payload.quantity = quantity || null;
        payload.unit = unitName || null;
        payload.notes = notes;
      }
      if (fields.includes("concrete")) {
        payload.concrete_description = description || text;
        payload.volume_m3 = volume;
        payload.structural_element = structuralElement;
        payload.parcel = parcel || null;
        payload.zone = zone || null;
        payload.block = block || null;
        payload.floor = floor || null;
        payload.batching_plant = batchingPlant;
        payload.truck_delivery_note_number = deliveryNote;
        payload.lab_sample_code = labSampleCode;
        payload.sampling_state = samplingState;
        payload.test_sheet_count = testSheetCount || null;
        payload.notes = notes;
      }
      if (fields.includes("hse")) {
        payload.text = text;
        payload.severity = severity;
        payload.immediate_action = action;
      }
      if (fields.includes("barrier")) {
        payload.kind = kind;
        payload.text = text;
        payload.owner_user = ownerUser || null;
        payload.due_date = due || null;
      }
      if (!navigator.onLine) {
        return queueUnitReportOperation({ actorId: requireStoredActorId(), projectId: String(businessId), unit,
          reportDate: report.report_date, localReportId: report.id, operationKind: "create", targetType: section, payload });
      }
      return createUnitSection(businessId, unit, report.id, section, payload);
    },
    onSuccess: async () => {
      setText("");
      setDescription("");
      setVolume("");
      setLocation("");
      setQuantity("");
      setUnitName("");
      setNotes("");
      setStructuralElement("");
      setParcel("");
      setZone("");
      setBlock("");
      setFloor("");
      setBatchingPlant("");
      setDeliveryNote("");
      setLabSampleCode("");
      setSamplingState("not_sampled");
      setTestSheetCount("");
      setAction("");
      setOwnerUser("");
      setError(null);
      await qc.invalidateQueries({ queryKey });
    },
    onError: (err) => {
      const parsed = extractSectionErrors(err);
      const code = parsed.allErrors[0]?.code;
      setError(
        code
          ? t(`businessDepartment.unitReport.sections.${sectionKey(section)}.errors.${code}`, {
              defaultValue: parsed.topMessage || (err instanceof ApiRequestError ? err.message : ""),
            })
          : parsed.topMessage,
      );
    },
  });

  const remove = useMutation({
    networkMode: "always",
    mutationFn: async (row: UnitSectionRow & { client_id?: string }) => {
      if (!navigator.onLine) {
        await queueUnitReportOperation({ actorId: requireStoredActorId(), projectId: String(businessId), unit,
        reportDate: report.report_date, localReportId: report.id, operationKind: "delete", targetType: section,
        clientId: row.client_id, targetServerId: row.id || null, payload: {} });
        return;
      }
      await deleteUnitSection(businessId, unit, report.id, section, row.id);
    },
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey });
    },
  });

  const rows = query.data ?? [];

  return (
    <section className="space-y-3" data-testid={`unit-section-${section}`}>
      <h3 className="text-sm font-semibold">{t(titleKey)}</h3>
      {rows.length === 0 ? <p className="text-sm text-muted-foreground">{t(emptyKey)}</p> : null}
      <ul className="space-y-2">
        {rows.map((row) => (
          <li key={row.id || (row as UnitSectionRow & { client_id?: string }).client_id} className="flex items-start justify-between gap-2 rounded border p-2 text-sm">
            <div className="flex min-w-0 flex-1 items-start gap-2">
              <RowSyncStatusBadge
                status={(row as UnitSectionRow & { sync_status?: string }).sync_status ?? "synced"}
              />
              {(row as UnitSectionRow & { field_error?: { field: string; code: string } }).field_error ? (
                <p role="alert" data-testid="row-field-error" className="text-xs text-destructive">
                  {t("offline.fieldError", (row as unknown as { field_error: { field: string; code: string } }).field_error)}
                </p>
              ) : null}
              <RowSummary row={row} overdueLabel={t("businessDepartment.unitReport.sections.issues.overdue")} />
            </div>
            {editable ? (
              <Button type="button" variant="ghost" onClick={() => remove.mutate(row)} aria-label={t("common.delete", { defaultValue: "Delete" })}>
                <Trash2 className="size-4" />
              </Button>
            ) : null}
          </li>
        ))}
      </ul>
      {editable ? (
        <form
          className="grid gap-2 sm:grid-cols-2"
          onSubmit={(event) => {
            event.preventDefault();
            create.mutate();
          }}
        >
          {fields.includes("concrete") || fields.includes("description") ? (
            <Field label={t("businessDepartment.unitReport.sections.fields.description", "شرح") }>
              <Input value={description} onChange={(event) => setDescription(event.target.value)} required />
            </Field>
          ) : null}
          {fields.includes("concrete") ? (
            <Field label={t("businessDepartment.unitReport.sections.concrete.fields.volume", "حجم (مترمکعب)")}>
              <Input inputMode="decimal" value={volume} onChange={(event) => setVolume(event.target.value)} required />
            </Field>
          ) : null}
          {fields.includes("description") ? (
            <>
              <Field label={t("businessDepartment.unitReport.sections.fields.location", "محل") }><Input value={location} onChange={(event) => setLocation(event.target.value)} /></Field>
              <Field label={t("businessDepartment.unitReport.sections.fields.quantity", "مقدار") }><Input inputMode="decimal" value={quantity} onChange={(event) => setQuantity(event.target.value)} /></Field>
              <Field label={t("businessDepartment.unitReport.sections.fields.unit", "واحد") }><Input value={unitName} onChange={(event) => setUnitName(event.target.value)} /></Field>
              <Field label={t("businessDepartment.unitReport.sections.fields.notes", "توضیحات") }><Input value={notes} onChange={(event) => setNotes(event.target.value)} /></Field>
            </>
          ) : null}
          {fields.includes("concrete") ? (
            <>
              <Field label={t("businessDepartment.unitReport.sections.concrete.fields.structuralElement", "عضو سازه‌ای") }><Input value={structuralElement} onChange={(event) => setStructuralElement(event.target.value)} /></Field>
              <Field label={t("businessDepartment.unitReport.sections.fields.parcel", "پارسل") }><Input value={parcel} onChange={(event) => setParcel(event.target.value)} /></Field>
              <Field label={t("businessDepartment.unitReport.sections.fields.location", "زون") }><Input value={zone} onChange={(event) => setZone(event.target.value)} /></Field>
              <Field label={t("businessDepartment.unitReport.sections.fields.block", "بلوک") }><Input value={block} onChange={(event) => setBlock(event.target.value)} /></Field>
              <Field label={t("businessDepartment.unitReport.sections.fields.floor", "طبقه") }><Input value={floor} onChange={(event) => setFloor(event.target.value)} /></Field>
              <Field label={t("businessDepartment.unitReport.sections.concrete.fields.batchingPlant", "بچینگ") }><Input value={batchingPlant} onChange={(event) => setBatchingPlant(event.target.value)} /></Field>
              <Field label={t("businessDepartment.unitReport.sections.concrete.fields.deliveryNote", "شماره حواله") }><Input value={deliveryNote} onChange={(event) => setDeliveryNote(event.target.value)} /></Field>
              <Field label={t("businessDepartment.unitReport.sections.concrete.fields.samplingState", "وضعیت نمونه‌گیری") }>
                <Select name="samplingState" value={samplingState} onChange={(event) => setSamplingState(event.target.value)} options={[
                  { value: "not_sampled", label: t("businessDepartment.unitReport.sections.concrete.samplingNotTaken", "نمونه‌گیری نشده") },
                  { value: "sampling_declared", label: t("businessDepartment.unitReport.sections.concrete.sampling", "نمونه‌گیری اعلام شده") },
                ]} />
              </Field>
              {samplingState === "sampling_declared" ? <>
                <Field label={t("businessDepartment.unitReport.sections.concrete.fields.labSampleCode", "کد نمونه آزمایشگاه") }><Input value={labSampleCode} onChange={(event) => setLabSampleCode(event.target.value)} required /></Field>
                <Field label={t("businessDepartment.unitReport.sections.concrete.fields.testSheetCount", "تعداد برگه آزمایش") }><Input inputMode="numeric" value={testSheetCount} onChange={(event) => setTestSheetCount(event.target.value)} required /></Field>
              </> : null}
              <Field label={t("businessDepartment.unitReport.sections.fields.notes", "توضیحات") }><Input value={notes} onChange={(event) => setNotes(event.target.value)} /></Field>
            </>
          ) : null}
          {fields.includes("barrier") ? (
            <Field label={t("businessDepartment.unitReport.sections.issues.tab")}>
              <Select
                name="issueKind"
                value={kind}
                onChange={(event) => setKind(event.target.value)}
                options={[
                  { value: "issue", label: t("businessDepartment.unitReport.sections.issues.kindIssue", "مسئله") },
                  { value: "barrier", label: t("businessDepartment.unitReport.sections.issues.kindBarrier", "مانع") },
                ]}
              />
            </Field>
          ) : null}
          {fields.includes("text") || fields.includes("hse") || fields.includes("barrier") ? (
            <Field label={t(titleKey)}>
              <Input value={text} onChange={(event) => setText(event.target.value)} required />
            </Field>
          ) : null}
          {fields.includes("hse") ? (
            <>
              <Field label={t("businessDepartment.unitReport.sections.hse.severity", "شدت") }>
                <Select
                  name="severity"
                  value={severity}
                  onChange={(event) => setSeverity(event.target.value)}
                  options={[
                    { value: "minor", label: t("businessDepartment.unitReport.sections.hse.minor", "جزئی") },
                    { value: "moderate", label: t("businessDepartment.unitReport.sections.hse.moderate", "متوسط") },
                    { value: "major", label: t("businessDepartment.unitReport.sections.hse.major", "عمده") },
                  ]}
                />
              </Field>
              <Field label={t("businessDepartment.unitReport.sections.hse.immediateAction", "اقدام فوری") }>
                <Input value={action} onChange={(event) => setAction(event.target.value)} required />
              </Field>
            </>
          ) : null}
          {fields.includes("barrier") ? (
            <Field label={t("businessDepartment.unitReport.sections.issues.dueDate", "تاریخ سررسید") }>
              <Input type="date" value={due} onChange={(event) => setDue(event.target.value)} />
            </Field>
          ) : null}
          {fields.includes("barrier") ? (
            <Field label={t("businessDepartment.unitReport.sections.issues.owner", "شناسه مسئول پیگیری") }>
              <Input value={ownerUser} onChange={(event) => setOwnerUser(event.target.value)} required={kind === "barrier"} />
            </Field>
          ) : null}
          {error ? (
            <p className="text-xs text-destructive sm:col-span-2" role="alert">
              {error}
            </p>
          ) : null}
          <div>
            <Button type="submit" disabled={create.isPending}>
              {t(addKey)}
            </Button>
          </div>
        </form>
      ) : null}
    </section>
  );
}

function sectionKey(section: string): string {
  if (section === "general-activities") return "general";
  if (section === "hse-incidents") return "hse";
  if (section === "concrete") return "concrete";
  if (section === "issues") return "issues";
  return "visits";
}

function RowSummary({ row, overdueLabel }: { row: UnitSectionRow; overdueLabel: string }) {
  const label =
    row.activity_description ||
    row.concrete_description ||
    row.text ||
    row.volume_m3 ||
    row.id;
  const overdue = row.due_date ? row.due_date < new Date().toISOString().slice(0, 10) : false;
  return (
    <div>
      <p>{label}</p>
      {row.severity ? <p className="text-xs">{row.severity}</p> : null}
      {overdue ? <p className="text-xs text-destructive">{overdueLabel}</p> : null}
    </div>
  );
}
