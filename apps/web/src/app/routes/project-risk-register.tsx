import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useParams } from "react-router";
import {
  ProjectProvider,
  usePermission,
  useProject,
} from "@/app/contexts/project-context";
import {
  createRiskEvent,
  EVENT_TYPE_LABELS,
  fetchRiskEvents,
  fetchRiskMatrix,
  SEVERITY_LABELS,
  type RiskEventType,
  type RiskSeverity,
} from "@/app/lib/api/risk-events";
import { PATHS } from "@/app/routeVars";
import { EmptyState } from "@/components/layout/empty-state";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Badge } from "@/components/ui/badge";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";

const SEVERITIES: RiskSeverity[] = ["low", "medium", "high", "critical"];

function RiskRegisterContent() {
  const { t } = useTranslation();

  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canEdit = has("edit_reports");
  const toast = useToast();
  const qc = useQueryClient();
  const [eventType, setEventType] = useState<string>("");
  const [search, setSearch] = useState("");
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    event_type: "risk" as RiskEventType,
    description: "",
    event_date: "",
    probability: "0.5",
    severity: "medium" as RiskSeverity,
    responsible_party: "",
  });

  const {
    data: matrix,
    isLoading: mLoading,
    isError: mError,
    refetch: refetchMatrix,
  } = useQuery({
    queryKey: ["risk-matrix", projectId],
    queryFn: () => fetchRiskMatrix(projectId),
    enabled: Boolean(projectId),
  });

  const {
    data: events,
    isLoading: eLoading,
    isError: eError,
    refetch: refetchEvents,
  } = useQuery({
    queryKey: ["risk-events", projectId, eventType, search],
    queryFn: () =>
      fetchRiskEvents(projectId, {
        event_type: eventType || undefined,
        search: search || undefined,
      }),
    enabled: Boolean(projectId),
  });

  const save = useMutation({
    mutationFn: () =>
      createRiskEvent(projectId, {
        event_type: form.event_type,
        description: form.description,
        event_date: form.event_date || null,
        probability: Number(form.probability),
        severity: form.severity,
        responsible_party: form.responsible_party,
        status: "open",
      }),
    onSuccess: () => {
      toast.success("ثبت شد");
      setOpen(false);
      void qc.invalidateQueries({ queryKey: ["risk-events", projectId] });
      void qc.invalidateQueries({ queryKey: ["risk-matrix", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const maxCount = useMemo(() => {
    if (!matrix) return 1;
    return Math.max(1, ...matrix.matrix.flatMap((r) => r.cells.map((c) => c.count)));
  }, [matrix]);

  if (isLoading || mLoading || eLoading) return <LoadingSkeleton rows={8} />;
  if (!project) return <EmptyState title={t("common.projectNotFound")} />;
  if (mError || eError) {
    return (
      <QueryErrorState
        onRetry={() => {
          void refetchMatrix();
          void refetchEvents();
        }}
      />
    );
  }

  const rows = events?.results ?? [];

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("pages.riskRegister.title")}
        subtitle={t("pages.riskRegister.subtitle")}
      />

      <div className="flex flex-wrap items-center gap-3">
        <span className="text-sm text-muted-foreground">
          رویدادهای باز در ماتریس: {matrix?.total_open ?? 0}
        </span>
        {canEdit ? (
          <Button className="ms-auto" size="sm" onClick={() => setOpen(true)}>
            رویداد جدید
          </Button>
        ) : null}
      </div>

      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="px-3 py-2 text-start">احتمال</th>
              {SEVERITIES.map((s) => (
                <th key={s} className="px-3 py-2 text-center">
                  {SEVERITY_LABELS[s]}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(matrix?.matrix ?? []).map((row) => (
              <tr key={row.probability_bucket} className="border-t">
                <td className="px-3 py-2 font-medium">{row.probability_bucket}%</td>
                {SEVERITIES.map((sev) => {
                  const cell = row.cells.find((c) => c.severity === sev);
                  const count = cell?.count ?? 0;
                  const intensity = count / maxCount;
                  return (
                    <td key={sev} className="px-3 py-2 text-center">
                      <span
                        className="inline-flex min-w-10 justify-center rounded px-2 py-1"
                        style={{
                          background:
                            count === 0
                              ? "transparent"
                              : `color-mix(in srgb, var(--destructive) ${Math.round(intensity * 70)}%, transparent)`,
                        }}
                      >
                        {count}
                      </span>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex flex-wrap gap-2">
        <select
          className="rounded border px-2 py-1 text-sm"
          value={eventType}
          onChange={(e) => setEventType(e.target.value)}
        >
          <option value="">همه انواع</option>
          {Object.entries(EVENT_TYPE_LABELS).map(([k, v]) => (
            <option key={k} value={k}>
              {v}
            </option>
          ))}
        </select>
        <input
          className="rounded border px-2 py-1 text-sm"
          placeholder="جستجو..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {rows.length === 0 ? (
        <EmptyState title={t("pages.riskRegister.empty")} description={t("pages.riskRegister.emptyDescription")} />
      ) : (
        <table className="w-full text-sm border rounded-lg">
          <thead className="bg-muted/50">
            <tr>
              {["تاریخ", "نوع", "شرح", "احتمال", "شدت", "وضعیت"].map((h) => (
                <th key={h} className="px-3 py-2 text-start">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className="border-t">
                <td className="px-3 py-2">{r.event_date ?? "—"}</td>
                <td className="px-3 py-2">
                  <Badge
                    variant="info"
                    label={EVENT_TYPE_LABELS[r.event_type] ?? r.event_type}
                  />
                </td>
                <td className="px-3 py-2">{r.description}</td>
                <td className="px-3 py-2">
                  {r.probability != null ? `${Math.round(Number(r.probability) * 100)}%` : "—"}
                </td>
                <td className="px-3 py-2">
                  {r.severity ? SEVERITY_LABELS[r.severity as RiskSeverity] : "—"}
                </td>
                <td className="px-3 py-2">
                  <Badge
                    variant={r.status === "resolved" ? "success" : "warning"}
                    label={r.status_label ?? r.status}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <Drawer
        isOpen={open}
        onClose={() => setOpen(false)}
        title={t("pages.riskRegister.newEvent")}
        footer={
          <Button onClick={() => save.mutate()} loading={save.isPending}>
            ذخیره
          </Button>
        }
      >
        <div className="space-y-3 p-4">
          <select
            className="w-full rounded border px-2 py-1"
            value={form.event_type}
            onChange={(e) =>
              setForm((f) => ({ ...f, event_type: e.target.value as RiskEventType }))
            }
          >
            {Object.entries(EVENT_TYPE_LABELS).map(([k, v]) => (
              <option key={k} value={k}>
                {v}
              </option>
            ))}
          </select>
          <JalaliDatePicker
            name="event_date"
            label="تاریخ"
            value={form.event_date}
            onChange={(v) => setForm((f) => ({ ...f, event_date: v }))}
          />
          <textarea
            className="w-full rounded border px-2 py-1"
            placeholder="شرح"
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          />
          <input
            className="w-full rounded border px-2 py-1"
            placeholder="احتمال (۰ تا ۱)"
            value={form.probability}
            onChange={(e) => setForm((f) => ({ ...f, probability: e.target.value }))}
          />
          <select
            className="w-full rounded border px-2 py-1"
            value={form.severity}
            onChange={(e) =>
              setForm((f) => ({ ...f, severity: e.target.value as RiskSeverity }))
            }
          >
            {SEVERITIES.map((s) => (
              <option key={s} value={s}>
                {SEVERITY_LABELS[s]}
              </option>
            ))}
          </select>
          <input
            className="w-full rounded border px-2 py-1"
            placeholder="مسئول"
            value={form.responsible_party}
            onChange={(e) => setForm((f) => ({ ...f, responsible_party: e.target.value }))}
          />
        </div>
      </Drawer>
    </div>
  );
}

export default function ProjectRiskRegisterPage() {
  const { t, i18n } = useTranslation();
  const { projectId = "" } = useParams();
  return (
    <main className="page-main page-shell mx-auto px-4 py-8">
      <ProjectProvider projectId={projectId}>
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "ریسک و تأخیر" },
          ]}
        />
        <RiskRegisterContent />
      </ProjectProvider>
    </main>
  );
}
