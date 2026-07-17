import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bell } from "lucide-react";
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
import { Checkbox, Field, Input, Select } from "@/components/form";
import { EmptyState } from "@/components/layout/empty-state";
import { LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
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

  const {
    data: alerts,
    isLoading: loadingAlerts,
    isError: alertsError,
    refetch: refetchAlerts,
  } = useQuery({
    queryKey: ["alerts", projectId],
    queryFn: () => fetchAlerts(projectId, { acknowledged: "false" }),
  });

  const {
    data: rules,
    isLoading: loadingRules,
    isError: rulesError,
    refetch: refetchRules,
  } = useQuery({
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
  if (!project) {
    return <EmptyState title="پروژه یافت نشد" />;
  }
  if (alertsError) {
    return <QueryErrorState onRetry={() => void refetchAlerts()} />;
  }

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
            <EmptyState
              icon={<Bell />}
              title="هشدار فعالی وجود ندارد"
              description="وقتی آستانه‌ای رد شود، هشدارها اینجا نمایش داده می‌شوند."
            />
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
          {loadingRules ? (
            <LoadingSkeleton rows={6} />
          ) : rulesError ? (
            <QueryErrorState onRetry={() => void refetchRules()} />
          ) : (rules?.results?.length ?? 0) === 0 ? (
            <EmptyState
              title="قانونی تعریف نشده"
              description="اولین قانون هشدار را اضافه کنید."
              action={
                <Button variant="primary" onClick={() => setRuleDrawer(true)}>
                  افزودن قانون هشدار
                </Button>
              }
            />
          ) : (
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
                        <Checkbox
                          name={`rule-active-${r.id}`}
                          label="فعال"
                          checked={r.is_active}
                          onChange={(e) => {
                            const checked = Boolean(
                              (e.target as unknown as { value: boolean }).value,
                            );
                            toggleRule.mutate({ id: r.id, is_active: checked });
                          }}
                        />
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
        footer={
          <Button
            variant="primary"
            loading={createRule.isPending}
            onClick={() => createRule.mutate()}
            disabled={createRule.isPending || !ruleForm.name.trim()}
          >
            ذخیره
          </Button>
        }
      >
        <div className="space-y-4">
          <Select
            name="alert_type"
            label="نوع هشدار"
            value={ruleForm.alert_type}
            onChange={(e) => {
              const t = e.target.value;
              setRuleForm({ ...ruleForm, alert_type: t, name: ALERT_TYPE_LABELS[t] ?? t });
            }}
            options={Object.entries(ALERT_TYPE_LABELS).map(([k, v]) => ({
              value: k,
              label: v,
            }))}
          />
          <Field name="rule_name" label="نام" htmlFor="alert-rule-name">
            {() => (
              <Input
                id="alert-rule-name"
                name="rule_name"
                value={ruleForm.name}
                onChange={(e) => setRuleForm({ ...ruleForm, name: e.target.value })}
              />
            )}
          </Field>
          <Field name="threshold_value" label="آستانه" htmlFor="alert-rule-threshold">
            {() => (
              <Input
                id="alert-rule-threshold"
                name="threshold_value"
                type="number"
                value={ruleForm.threshold_value}
                onChange={(e) =>
                  setRuleForm({ ...ruleForm, threshold_value: Number(e.target.value) })
                }
              />
            )}
          </Field>
          <Field
            name="notify_roles"
            label="نقش‌های گیرنده"
            helpText="با ویرگول جدا کنید"
            htmlFor="alert-rule-roles"
          >
            {() => (
              <Input
                id="alert-rule-roles"
                name="notify_roles"
                value={ruleForm.notify_roles}
                onChange={(e) => setRuleForm({ ...ruleForm, notify_roles: e.target.value })}
                placeholder="project_manager, site_engineer"
              />
            )}
          </Field>
          <Field name="cooldown_hours" label="فاصله تکرار (ساعت)" htmlFor="alert-rule-cooldown">
            {() => (
              <Input
                id="alert-rule-cooldown"
                name="cooldown_hours"
                type="number"
                value={ruleForm.cooldown_hours}
                onChange={(e) =>
                  setRuleForm({ ...ruleForm, cooldown_hours: Number(e.target.value) })
                }
              />
            )}
          </Field>
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
