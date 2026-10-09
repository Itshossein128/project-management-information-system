import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useParams } from "react-router";
import { useAuth } from "@/app/contexts/auth-context";
import {
  ProjectProvider,
  usePermission,
  useProject,
} from "@/app/contexts/project-context";
import { fetchMembers } from "@/app/lib/api/members";
import {
  createRiskAction,
  createRiskEvent,
  EVENT_TYPE_LABELS,
  fetchRiskEvents,
  fetchRiskMatrix,
  RISK_STATUS_LABELS,
  SEVERITY_LABELS,
  updateRiskEvent,
  type ImpactDimension,
  type RiskEvent,
  type RiskEventType,
  type RiskSeverity,
  type RiskStatus,
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
const IMPACTS: ImpactDimension[] = [
  "schedule",
  "cost",
  "quality",
  "safety",
  "contract",
  "liquidity",
];
const FR_STATUSES: RiskStatus[] = [
  "open",
  "under_review",
  "mitigated",
  "closed",
  "residual",
];

function RiskRegisterContent() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canEdit = has("edit_reports");
  const toast = useToast();
  const qc = useQueryClient();
  const [eventType, setEventType] = useState<string>("risk");
  const [impact, setImpact] = useState<string>("");
  const [search, setSearch] = useState("");
  const [open, setOpen] = useState(false);
  const [ackTarget, setAckTarget] = useState<{
    event: RiskEvent;
    status: RiskStatus;
  } | null>(null);
  const [form, setForm] = useState({
    event_type: "risk" as RiskEventType,
    description: "",
    cause: "",
    consequence: "",
    response: "",
    action_text: "",
    event_date: "",
    due_date: "",
    probability_level: "3",
    impact_severity_level: "3",
    owner: "",
    responsible_party: "",
    impact_on_schedule: true,
    impact_on_cost: false,
    impact_on_quality: false,
    impact_on_safety: false,
    impact_on_contract: false,
    impact_on_liquidity: false,
  });

  const membersQuery = useQuery({
    queryKey: ["members", projectId],
    queryFn: () => fetchMembers(projectId),
    enabled: Boolean(projectId),
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
    queryKey: ["risk-events", projectId, eventType, search, impact],
    queryFn: () =>
      fetchRiskEvents(projectId, {
        event_type: eventType || undefined,
        search: search || undefined,
        impact: impact || undefined,
      }),
    enabled: Boolean(projectId),
  });

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["risk-events", projectId] });
    void qc.invalidateQueries({ queryKey: ["risk-matrix", projectId] });
  };

  const save = useMutation({
    mutationFn: async () => {
      const pLevel = form.probability_level ? Number(form.probability_level) : null;
      const iLevel = form.impact_severity_level
        ? Number(form.impact_severity_level)
        : null;
      const ownerId = form.owner || user?.id || undefined;
      const created = await createRiskEvent(projectId, {
        event_type: form.event_type,
        description: form.description,
        cause: form.cause,
        consequence: form.consequence,
        response: form.response,
        corrective_action: form.action_text,
        event_date: form.event_date || null,
        due_date: form.due_date || null,
        probability_level: pLevel,
        impact_severity_level: iLevel,
        owner: ownerId ?? null,
        responsible_party: form.responsible_party,
        impact_on_schedule: form.impact_on_schedule,
        impact_on_cost: form.impact_on_cost,
        impact_on_quality: form.impact_on_quality,
        impact_on_safety: form.impact_on_safety,
        impact_on_contract: form.impact_on_contract,
        impact_on_liquidity: form.impact_on_liquidity,
      });
      if (form.action_text.trim()) {
        await createRiskAction(projectId, {
          risk_event: created.id,
          description: form.action_text.trim(),
          due_date: form.due_date || null,
          owner: ownerId ?? null,
          status: "open",
        });
      }
      return created;
    },
    onSuccess: () => {
      toast.success(t("pages.riskRegister.saved"));
      setOpen(false);
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const patchStatus = useMutation({
    mutationFn: (args: {
      id: string;
      status: RiskStatus;
      acknowledge_open_actions?: boolean;
    }) =>
      updateRiskEvent(projectId, args.id, {
        status: args.status,
        acknowledge_open_actions: args.acknowledge_open_actions,
      }),
    onSuccess: () => {
      toast.success(t("pages.riskRegister.statusUpdated"));
      setAckTarget(null);
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const onStatusChange = (event: RiskEvent, next: RiskStatus) => {
    if (next === event.status) return;
    if (next === "closed" && (event.open_actions_count ?? 0) > 0) {
      setAckTarget({ event, status: next });
      return;
    }
    patchStatus.mutate({ id: event.id, status: next });
  };

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
  const members = membersQuery.data ?? [];

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("pages.riskRegister.title")}
        subtitle={t("pages.riskRegister.subtitle")}
      />

      <div className="flex flex-wrap items-center gap-3">
        <span className="text-sm text-muted-foreground">
          {t("pages.riskRegister.openInMatrix", { count: matrix?.total_open ?? 0 })}
        </span>
        {canEdit ? (
          <Button
            className="ms-auto"
            size="sm"
            onClick={() => {
              setForm((f) => ({ ...f, owner: user?.id ?? "" }));
              setOpen(true);
            }}
          >
            {t("pages.riskRegister.newEvent")}
          </Button>
        ) : null}
      </div>

      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="px-3 py-2 text-start">{t("pages.riskRegister.probability")}</th>
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
          <option value="">{t("pages.riskRegister.allTypes")}</option>
          {Object.entries(EVENT_TYPE_LABELS).map(([k, v]) => (
            <option key={k} value={k}>
              {v}
            </option>
          ))}
        </select>
        <select
          className="rounded border px-2 py-1 text-sm"
          value={impact}
          onChange={(e) => setImpact(e.target.value)}
        >
          <option value="">{t("pages.riskRegister.allImpacts")}</option>
          {IMPACTS.map((dim) => (
            <option key={dim} value={dim}>
              {t(`pages.riskRegister.impact.${dim}`)}
            </option>
          ))}
        </select>
        <input
          className="rounded border px-2 py-1 text-sm"
          placeholder={t("common.search")}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {rows.length === 0 ? (
        <EmptyState
          title={t("pages.riskRegister.empty")}
          description={t("pages.riskRegister.emptyDescription")}
        />
      ) : (
        <table className="w-full text-sm border rounded-lg">
          <thead className="bg-muted/50">
            <tr>
              {[
                t("pages.riskRegister.colDate"),
                t("pages.riskRegister.colType"),
                t("pages.riskRegister.colDescription"),
                t("pages.riskRegister.colScore"),
                t("pages.riskRegister.colStatus"),
              ].map((h) => (
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
                  {r.composite_score != null
                    ? r.composite_score
                    : r.probability != null
                      ? `${Math.round(Number(r.probability) * 100)}%`
                      : "—"}
                </td>
                <td className="px-3 py-2">
                  {canEdit ? (
                    <select
                      className="rounded border px-2 py-1 text-sm"
                      value={r.status}
                      disabled={patchStatus.isPending}
                      onChange={(e) =>
                        onStatusChange(r, e.target.value as RiskStatus)
                      }
                    >
                      {FR_STATUSES.map((st) => (
                        <option key={st} value={st}>
                          {RISK_STATUS_LABELS[st] ?? st}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <Badge
                      variant={
                        r.status === "closed" || r.status === "resolved"
                          ? "success"
                          : "warning"
                      }
                      label={
                        r.status_label ?? RISK_STATUS_LABELS[r.status] ?? r.status
                      }
                    />
                  )}
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
            {t("common.save")}
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
            label={t("pages.riskRegister.colDate")}
            value={form.event_date}
            onChange={(v) => setForm((f) => ({ ...f, event_date: v }))}
          />
          <JalaliDatePicker
            name="due_date"
            label={t("pages.riskRegister.dueDate")}
            value={form.due_date}
            onChange={(v) => setForm((f) => ({ ...f, due_date: v }))}
          />
          <textarea
            className="w-full rounded border px-2 py-1"
            placeholder={t("pages.riskRegister.colDescription")}
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          />
          <textarea
            className="w-full rounded border px-2 py-1"
            placeholder={t("pages.riskRegister.cause")}
            value={form.cause}
            onChange={(e) => setForm((f) => ({ ...f, cause: e.target.value }))}
          />
          <textarea
            className="w-full rounded border px-2 py-1"
            placeholder={t("pages.riskRegister.consequence")}
            value={form.consequence}
            onChange={(e) => setForm((f) => ({ ...f, consequence: e.target.value }))}
          />
          <textarea
            className="w-full rounded border px-2 py-1"
            placeholder={t("pages.riskRegister.response")}
            value={form.response}
            onChange={(e) => setForm((f) => ({ ...f, response: e.target.value }))}
          />
          <textarea
            className="w-full rounded border px-2 py-1"
            placeholder={t("pages.riskRegister.actionText")}
            value={form.action_text}
            onChange={(e) => setForm((f) => ({ ...f, action_text: e.target.value }))}
          />
          <label className="block text-sm">
            {t("pages.riskRegister.probabilityLevel")}
            <input
              type="number"
              min={1}
              max={5}
              className="mt-1 w-full rounded border px-2 py-1"
              value={form.probability_level}
              onChange={(e) =>
                setForm((f) => ({ ...f, probability_level: e.target.value }))
              }
            />
          </label>
          <label className="block text-sm">
            {t("pages.riskRegister.impactLevel")}
            <input
              type="number"
              min={1}
              max={5}
              className="mt-1 w-full rounded border px-2 py-1"
              value={form.impact_severity_level}
              onChange={(e) =>
                setForm((f) => ({ ...f, impact_severity_level: e.target.value }))
              }
            />
          </label>
          <label className="block text-sm">
            {t("pages.riskRegister.ownerUser")}
            <select
              className="mt-1 w-full rounded border px-2 py-1"
              value={form.owner}
              onChange={(e) => setForm((f) => ({ ...f, owner: e.target.value }))}
            >
              <option value="">{t("pages.riskRegister.selectOwner")}</option>
              {members
                .filter((m) => m.user_id)
                .map((m) => (
                  <option key={m.user_id!} value={m.user_id!}>
                    {m.full_name || m.mobile || m.user_id}
                  </option>
                ))}
            </select>
          </label>
          <input
            className="w-full rounded border px-2 py-1"
            placeholder={t("pages.riskRegister.owner")}
            value={form.responsible_party}
            onChange={(e) =>
              setForm((f) => ({ ...f, responsible_party: e.target.value }))
            }
          />
          <div className="flex flex-wrap gap-3 text-sm">
            {(
              [
                ["impact_on_schedule", "schedule"],
                ["impact_on_cost", "cost"],
                ["impact_on_quality", "quality"],
                ["impact_on_safety", "safety"],
                ["impact_on_contract", "contract"],
                ["impact_on_liquidity", "liquidity"],
              ] as const
            ).map(([key, dim]) => (
              <label key={key} className="inline-flex items-center gap-1">
                <input
                  type="checkbox"
                  checked={form[key]}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, [key]: e.target.checked }))
                  }
                />
                {t(`pages.riskRegister.impact.${dim}`)}
              </label>
            ))}
          </div>
        </div>
      </Drawer>

      <Drawer
        isOpen={Boolean(ackTarget)}
        onClose={() => setAckTarget(null)}
        title={t("pages.riskRegister.closeAcknowledgeTitle")}
        footer={
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => setAckTarget(null)}>
              {t("common.cancel")}
            </Button>
            <Button
              loading={patchStatus.isPending}
              onClick={() => {
                if (!ackTarget) return;
                patchStatus.mutate({
                  id: ackTarget.event.id,
                  status: ackTarget.status,
                  acknowledge_open_actions: true,
                });
              }}
            >
              {t("pages.riskRegister.closeAcknowledgeConfirm")}
            </Button>
          </div>
        }
      >
        <p className="p-4 text-sm text-muted-foreground">
          {t("pages.riskRegister.closeAcknowledgeBody", {
            count: ackTarget?.event.open_actions_count ?? 0,
          })}
        </p>
      </Drawer>
    </div>
  );
}

export default function ProjectRiskRegisterPage() {
  const { t } = useTranslation();
  const { projectId = "" } = useParams();
  return (
    <main className="page-main page-shell mx-auto px-4 py-8">
      <ProjectProvider projectId={projectId}>
        <Breadcrumb
          items={[
            { label: t("pages.riskRegister.projectsCrumb"), href: `/${PATHS.PROJECT}` },
            { label: t("pages.riskRegister.title") },
          ]}
        />
        <RiskRegisterContent />
      </ProjectProvider>
    </main>
  );
}
