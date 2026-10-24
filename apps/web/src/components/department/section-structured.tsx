import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { Trash2 } from "lucide-react";

import { ApiRequestError } from "@/app/lib/api-client";
import {
  createUnitSection,
  deleteUnitSection,
  extractSectionErrors,
  fetchUnitSection,
  type CanonicalUnit,
  type UnitReport,
  type UnitSectionRow,
} from "@/app/lib/api/unit-reports";
import { Button, Field, Input, Select } from "@/components/form";

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
  const [severity, setSeverity] = useState("minor");
  const [action, setAction] = useState("");
  const [kind, setKind] = useState("issue");
  const [due, setDue] = useState("");
  const [error, setError] = useState<string | null>(null);
  const queryKey = ["unit-section", businessId, unit, report.id, section];

  const query = useQuery({
    queryKey,
    queryFn: () => fetchUnitSection(businessId, unit, report.id, section),
  });

  const create = useMutation({
    mutationFn: () => {
      const payload: Record<string, unknown> = { row_number: (query.data?.length ?? 0) + 1 };
      if (fields.includes("text")) payload.text = text;
      if (fields.includes("description")) {
        payload.activity_description = description;
        payload.location = text;
      }
      if (fields.includes("concrete")) {
        payload.concrete_description = description || text;
        payload.volume_m3 = volume;
        payload.sampling_state = "not_sampled";
      }
      if (fields.includes("hse")) {
        payload.text = text;
        payload.severity = severity;
        payload.immediate_action = action;
      }
      if (fields.includes("barrier")) {
        payload.kind = kind;
        payload.text = text;
        payload.due_date = due || null;
      }
      return createUnitSection(businessId, unit, report.id, section, payload);
    },
    onSuccess: async () => {
      setText("");
      setDescription("");
      setVolume("");
      setAction("");
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
    mutationFn: (rowId: string) => deleteUnitSection(businessId, unit, report.id, section, rowId),
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
          <li key={row.id} className="flex items-start justify-between gap-2 rounded border p-2 text-sm">
            <RowSummary row={row} overdueLabel={t("businessDepartment.unitReport.sections.issues.overdue")} />
            {editable ? (
              <Button type="button" variant="ghost" onClick={() => remove.mutate(row.id)} aria-label={t("common.delete", { defaultValue: "Delete" })}>
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
            <Field label={t(titleKey)}>
              <Input value={description} onChange={(event) => setDescription(event.target.value)} />
            </Field>
          ) : null}
          {fields.includes("concrete") ? (
            <Field label={t("businessDepartment.unitReport.sections.concrete.tab")}>
              <Input inputMode="decimal" value={volume} onChange={(event) => setVolume(event.target.value)} required />
            </Field>
          ) : null}
          {fields.includes("barrier") ? (
            <Field label={t("businessDepartment.unitReport.sections.issues.tab")}>
              <Select
                name="issueKind"
                value={kind}
                onChange={(event) => setKind(event.target.value)}
                options={[
                  { value: "issue", label: "issue" },
                  { value: "barrier", label: "barrier" },
                ]}
              />
            </Field>
          ) : null}
          {fields.includes("text") || fields.includes("hse") || fields.includes("barrier") || fields.includes("description") ? (
            <Field label={t(titleKey)}>
              <Input value={text} onChange={(event) => setText(event.target.value)} />
            </Field>
          ) : null}
          {fields.includes("hse") ? (
            <>
              <Field label="severity">
                <Select
                  name="severity"
                  value={severity}
                  onChange={(event) => setSeverity(event.target.value)}
                  options={[
                    { value: "minor", label: "minor" },
                    { value: "moderate", label: "moderate" },
                    { value: "major", label: "major" },
                  ]}
                />
              </Field>
              <Field label="immediate_action">
                <Input value={action} onChange={(event) => setAction(event.target.value)} required />
              </Field>
            </>
          ) : null}
          {fields.includes("barrier") ? (
            <Field label="due_date">
              <Input type="date" value={due} onChange={(event) => setDue(event.target.value)} />
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
