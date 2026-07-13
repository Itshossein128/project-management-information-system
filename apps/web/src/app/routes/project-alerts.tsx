import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import {
  acknowledgeAlert,
  ALERT_TYPE_LABELS,
  createAlertRule,
  fetchAlertRules,
  fetchAlerts,
  updateAlertRule,
  type AlertLogEntry,
  type AlertRule,
} from "@/app/lib/api/alerts";
import { LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

type Tab = "active" | "rules";

function groupByType(entries: AlertLogEntry[]) {
  const map = new Map<string, AlertLogEntry[]>();
  for (const e of entries) {
    const t = e.alert_type || "other";
    if (!map.has(t)) map.set(t, []);
    map.get(t)!.push(e);
  }
  return map;
}

function AlertCenterContent() {
  const { projectId, project, isLoading } = useProject();
  const qc = useQueryClient();
  const toast = useToast();
  const { has } = usePermission(projectId);
  const canManage = has("edit_project");

  const [tab, setTab] = useState<Tab>("active");
  const [ruleDrawer, setRuleDrawer] = useState(false);
  const [ruleForm, setRuleForm] = useState({
    alert_type: "budget_overrun",
    name: "تجاوز از بودجه",
    threshold_value: 90,
    notify_roles: "project_manager",
    cooldown_hours: 48,
  });

  const { data: alerts, isLoading: loadingAlerts } = useQuery({
    queryKey: ["alerts", projectId],
    queryFn: () => fetchAlerts(projectId, { acknowledged: "false" }),
  });

  const { data: rules, isLoading: loadingRules } = useQuery({
    queryKey: ["alert-rules", projectId],
    queryFn: () => fetchAlertRules(projectId),
    enabled: tab === "rules" && canManage,
  });

  const ack = useMutation({
    mutationFn: (id: string) => acknowledgeAlert(projectId, id),
    onSuccess: () => {
      toast.success("هشدار علامت‌گذاری شد");
      void qc.invalidateQueries({ queryKey: ["alerts", projectId] });
      void qc.invalidateQueries({ queryKey: ["alerts-active", projectId] });
    },
  });

  const ackAll = useMutation({
    mutationFn: async () => {
      for (const e of alerts?.results ?? []) {
        if (!e.acknowledged_at) await acknowledgeAlert(projectId, e.id);
      }
    },
    onSuccess: () => {
      toast.success("همه هشدارها علامت‌گذاری شدند");
      void qc.invalidateQueries({ queryKey: ["alerts", projectId] });
    },
  });

  const toggleRule = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      updateAlertRule(projectId, id, { is_active }),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["alert-rules", projectId] }),
  });

  const createRule = useMutation({
    mutationFn: () => createAlertRule(projectId, ruleForm),
    onSuccess: () => {
      toast.success("قانون ایجاد شد");
      setRuleDrawer(false);
      void qc.invalidateQueries({ queryKey: ["alert-rules", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (isLoading || loadingAlerts) return <LoadingSkeleton rows={10} />;
  if (!project) return <p>پروژه یافت نشد</p>;

  const grouped = groupByType(alerts?.results ?? []);

  return (
    <div className="space-y-6">
      <PageHeader title="هشدارها" subtitle={project.project_name} />

      <div className="flex flex-wrap gap-2">
        <Button variant={tab === "active" ? "primary" : "secondary"} size="sm" onClick={() => setTab("active")}>
          هشدارهای فعال
        </Button>
        {canManage ? (
          <Button variant={tab === "rules" ? "primary" : "secondary"} size="sm" onClick={() => setTab("rules")}>
            قوانین هشدار
          </Button>
        ) : null}
      </div>

      {tab === "active" ? (
        <div className="space-y-4">
          <div className="flex justify-end">
            {(alerts?.results?.length ?? 0) > 0 ? (
              <Button variant="secondary" size="sm" onClick={() => ackAll.mutate()} disabled={ackAll.isPending}>
                علامت‌گذاری همه
              </Button>
            ) : null}
          </div>
          {grouped.size === 0 ? (
            <p className="rounded-lg border p-8 text-center text-muted-foreground">هشدار فعالی وجود ندارد.</p>
          ) : (
            Array.from(grouped.entries()).map(([type, items]) => (
              <div key={type} className="rounded-lg border">
                <div className="border-b bg-muted/40 px-4 py-2 font-medium">
                  {ALERT_TYPE_LABELS[type] ?? type}
                </div>
                <ul className="divide-y">
                  {items.map((item) => (
                    <li key={item.id} className="flex flex-wrap items-start justify-between gap-3 px-4 py-3">
                      <div>
                        <p className="text-sm">{item.message}</p>
                        <p className="mt-1 text-xs text-muted-foreground">{new Date(item.fired_at).toLocaleString("fa-IR")}</p>
                      </div>
                      <Button variant="secondary" size="sm" onClick={() => ack.mutate(item.id)}>
                        رفع شد
                      </Button>
                    </li>
                  ))}
                </ul>
              </div>
            ))
          )}
        </div>
      ) : null}

      {tab === "rules" && canManage ? (
        <div className="space-y-4">
          <div className="flex justify-end">
            <Button variant="primary" onClick={() => setRuleDrawer(true)}>افزودن قانون هشدار</Button>
          </div>
          {loadingRules ? <LoadingSkeleton rows={6} /> : (
            <div className="overflow-x-auto rounded-lg border">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    {["نام", "نوع", "آستانه", "گیرندگان", "وضعیت", "عملیات"].map((h) => (
                      <th key={h} className="px-3 py-2 text-start">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(rules?.results ?? []).map((r: AlertRule) => (
                    <tr key={r.id} className="border-t">
                      <td className="px-3 py-2">
                        {r.is_system ? "🔒 " : ""}{r.name}
                      </td>
                      <td className="px-3 py-2">{ALERT_TYPE_LABELS[r.alert_type] ?? r.alert_type}</td>
                      <td className="px-3 py-2">{r.threshold_value ?? "—"}</td>
                      <td className="px-3 py-2">{r.notify_roles}</td>
                      <td className="px-3 py-2">
                        <label className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={r.is_active}
                            onChange={(e) => toggleRule.mutate({ id: r.id, is_active: e.target.checked })}
                          />
                          فعال
                        </label>
                      </td>
                      <td className="px-3 py-2">{r.is_system ? "—" : "قابل حذف"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ) : null}

      <Drawer
        isOpen={ruleDrawer}
        onClose={() => setRuleDrawer(false)}
        title="افزودن قانون هشدار"
        footer={<Button variant="primary" onClick={() => createRule.mutate()} disabled={createRule.isPending}>ذخیره</Button>}
      >
        <div className="space-y-3">
          <select
            className="w-full rounded border px-3 py-2 text-sm"
            value={ruleForm.alert_type}
            onChange={(e) => {
              const t = e.target.value;
              setRuleForm({ ...ruleForm, alert_type: t, name: ALERT_TYPE_LABELS[t] ?? t });
            }}
          >
            {Object.entries(ALERT_TYPE_LABELS).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
          <input className="w-full rounded border px-3 py-2 text-sm" value={ruleForm.name} onChange={(e) => setRuleForm({ ...ruleForm, name: e.target.value })} />
          <input type="number" className="w-full rounded border px-3 py-2 text-sm" value={ruleForm.threshold_value} onChange={(e) => setRuleForm({ ...ruleForm, threshold_value: Number(e.target.value) })} />
          <input className="w-full rounded border px-3 py-2 text-sm" placeholder="نقش‌ها (comma-separated)" value={ruleForm.notify_roles} onChange={(e) => setRuleForm({ ...ruleForm, notify_roles: e.target.value })} />
          <input type="number" className="w-full rounded border px-3 py-2 text-sm" value={ruleForm.cooldown_hours} onChange={(e) => setRuleForm({ ...ruleForm, cooldown_hours: Number(e.target.value) })} />
        </div>
      </Drawer>
    </div>
  );
}

export default function ProjectAlertsPage() {
  const { projectId = "" } = useParams();
  return (
    <ProjectProvider projectId={projectId}>
      <AlertCenterContent />
    </ProjectProvider>
  );
}
