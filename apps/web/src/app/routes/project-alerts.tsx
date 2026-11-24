import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertTriangle,
  Bell,
  BellRing,
  Check,
  CheckCheck,
  Clock,
  Lock,
  Plus,
  SlidersHorizontal,
  Trash2,
} from "lucide-react";
import { useState } from "react";
import { useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import {
  acknowledgeAlert,
  ALERT_TYPE_LABELS,
  createAlertRule,
  deleteAlertRule,
  fetchAlertRules,
  fetchAlerts,
  updateAlertRule,
  type AlertLogEntry,
  type AlertRule,
} from "@/app/lib/api/alerts";
import { formatRoleLabel } from "@/app/lib/role-labels";
import { Field, Input, Select } from "@/components/form";
import { EmptyState } from "@/components/layout/empty-state";
import { LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Badge } from "@/components/ui/badge";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/components/ui/toast";
import { ProductTourButton } from "@/components/tour/ProductTourButton";
import { useProductTour } from "@/components/tour/useProductTour";

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
  const { t, i18n } = useTranslation();

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

  const { startTour } = useProductTour({
    tourId: "project-alerts",
    steps: [
      {
        element: "[data-tour='alerts-tabs']",
        popover: {
          title: t("tour.projectAlerts.step1Title"),
          description: t("tour.projectAlerts.step1Desc"),
        },
        onHighlight: () => setTab("active"),
      },
      {
        element: "[data-tour='alerts-active-list']",
        popover: {
          title: t("tour.projectAlerts.step2Title"),
          description: t("tour.projectAlerts.step2Desc"),
        },
        onHighlight: () => setTab("active"),
      },
      {
        element: "[data-tour='alerts-acknowledge']",
        popover: {
          title: t("tour.projectAlerts.step3Title"),
          description: t("tour.projectAlerts.step3Desc"),
        },
      },
      {
        element: "[data-tour='notification-bell']",
        popover: {
          title: t("tour.projectAlerts.step4Title"),
          description: t("tour.projectAlerts.step4Desc"),
          side: "bottom",
          align: "end",
        },
      },
      {
        // Opens the rules tab so its table is visible while this step is read.
        // Steps cannot target the rules markup directly: useProductTour drops
        // steps whose element is unmounted when the tour starts.
        element: "[data-tour='alerts-rules-tab']",
        popover: {
          title: t("tour.projectAlerts.step5Title"),
          description: t("tour.projectAlerts.step5Desc"),
        },
        onHighlight: () => setTab("rules"),
      },
    ],
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

  const deleteRule = useMutation({
    mutationFn: (id: string) => deleteAlertRule(projectId, id),
    onSuccess: () => {
      toast.success("قانون حذف شد");
      void qc.invalidateQueries({ queryKey: ["alert-rules", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (isLoading || loadingAlerts) return <LoadingSkeleton rows={10} />;
  if (!project) {
    return <EmptyState title={t("common.projectNotFound")} />;
  }
  if (alertsError) {
    return <QueryErrorState onRetry={() => void refetchAlerts()} />;
  }

  const activeAlerts = alerts?.results ?? [];
  const grouped = groupByType(activeAlerts);
  const ruleList = rules?.results ?? [];

  const formatThreshold = (value: number | null) => {
    if (value === null || value === undefined || String(value) === "") return "—";
    const n = Number(value);
    return Number.isFinite(n)
      ? n.toLocaleString("fa-IR", { maximumFractionDigits: 2 })
      : String(value);
  };

  const splitRoles = (roles: string) =>
    (roles ?? "")
      .split(",")
      .map((r) => r.trim())
      .filter(Boolean);

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("pages.alerts.title")}
        subtitle={project.project_name}
        actions={<ProductTourButton onClick={startTour} />}
      />

      <Tabs
        value={tab}
        onValueChange={(v) => setTab(v as Tab)}
        dir={i18n.dir()}
        className="w-full gap-4"
      >
        <div className="flex flex-wrap items-center justify-between gap-3">
          <TabsList className="h-10" data-tour="alerts-tabs">
            <TabsTrigger value="active" className="gap-2 px-4">
              <BellRing />
              هشدارهای فعال
              {activeAlerts.length > 0 ? (
                <span className="rounded-full bg-danger-100 px-1.5 text-xs font-semibold text-danger-800 tabular-nums dark:bg-danger-900/40 dark:text-danger-300">
                  {activeAlerts.length.toLocaleString("fa-IR")}
                </span>
              ) : null}
            </TabsTrigger>
            {canManage ? (
              <TabsTrigger value="rules" className="gap-2 px-4" data-tour="alerts-rules-tab">
                <SlidersHorizontal />
                قوانین هشدار
              </TabsTrigger>
            ) : null}
          </TabsList>

          {tab === "active" && activeAlerts.length > 0 ? (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => ackAll.mutate()}
              loading={ackAll.isPending}
            >
              <CheckCheck className="size-4" />
              علامت‌گذاری همه
            </Button>
          ) : null}
          {tab === "rules" && canManage && ruleList.length > 0 ? (
            <Button variant="primary" size="sm" onClick={() => setRuleDrawer(true)}>
              <Plus className="size-4" />
              افزودن قانون هشدار
            </Button>
          ) : null}
        </div>

        <TabsContent value="active" className="mt-0">
          <div className="space-y-4" data-tour="alerts-active-list">
            {grouped.size === 0 ? (
              <EmptyState
                icon={<Bell />}
                title="هشدار فعالی وجود ندارد"
                description="وقتی آستانه‌ای رد شود، هشدارها اینجا نمایش داده می‌شوند."
                className="bg-card"
              />
            ) : (
              Array.from(grouped.entries()).map(([type, items], groupIdx) => (
                <section
                  key={type}
                  className="overflow-hidden rounded-xl border border-border/80 bg-card shadow-[var(--shadow-card)]"
                >
                  <header className="flex items-center justify-between gap-3 border-b border-border/80 bg-muted/40 px-4 py-3">
                    <div className="flex items-center gap-2.5">
                      <span className="flex size-8 items-center justify-center rounded-lg bg-warning-100 text-warning-700 dark:bg-warning-900/40 dark:text-warning-300">
                        <AlertTriangle className="size-4" />
                      </span>
                      <h2 className="text-sm font-semibold text-foreground">
                        {ALERT_TYPE_LABELS[type] ?? type}
                      </h2>
                    </div>
                    <Badge
                      variant="warning"
                      label={`${items.length.toLocaleString("fa-IR")} هشدار`}
                    />
                  </header>
                  <ul className="divide-y divide-border/70">
                    {items.map((item, itemIdx) => (
                      <li
                        key={item.id}
                        className="flex flex-col gap-3 px-4 py-3.5 transition-colors hover:bg-muted/30 sm:flex-row sm:items-center sm:justify-between"
                      >
                        <div className="min-w-0 space-y-1">
                          <p className="text-sm leading-6 text-foreground">{item.message}</p>
                          <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
                            <Clock className="size-3.5" />
                            <span className="tabular-nums">
                              {new Date(item.fired_at).toLocaleString("fa-IR")}
                            </span>
                          </p>
                        </div>
                        <Button
                          variant="secondary"
                          size="sm"
                          className="shrink-0 self-end sm:self-auto"
                          onClick={() => ack.mutate(item.id)}
                          loading={ack.isPending && ack.variables === item.id}
                          {...(groupIdx === 0 && itemIdx === 0
                            ? { "data-tour": "alerts-acknowledge" }
                            : {})}
                        >
                          <Check className="size-4" />
                          رفع شد
                        </Button>
                      </li>
                    ))}
                  </ul>
                </section>
              ))
            )}
          </div>
        </TabsContent>

        {canManage ? (
          <TabsContent value="rules" className="mt-0">
            {loadingRules ? (
              <LoadingSkeleton rows={6} />
            ) : rulesError ? (
              <QueryErrorState onRetry={() => void refetchRules()} />
            ) : ruleList.length === 0 ? (
              <EmptyState
                icon={<SlidersHorizontal />}
                title="قانونی تعریف نشده"
                description="اولین قانون هشدار را اضافه کنید."
                className="bg-card"
                action={
                  <Button variant="primary" onClick={() => setRuleDrawer(true)}>
                    <Plus className="size-4" />
                    افزودن قانون هشدار
                  </Button>
                }
              />
            ) : (
              <div className="overflow-hidden rounded-xl border border-border/80 bg-card shadow-[var(--shadow-card)]">
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[820px] text-sm">
                    <thead className="border-b border-border/80 bg-muted/50 text-xs text-muted-foreground">
                      <tr>
                        {["نام", "نوع", "آستانه", "گیرندگان", "فاصله تکرار", "وضعیت", ""].map(
                          (h, i) => (
                            <th key={h || i} className="px-4 py-3 text-start font-medium whitespace-nowrap">
                              {h}
                            </th>
                          ),
                        )}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/70">
                      {ruleList.map((r: AlertRule) => (
                        <tr key={r.id} className="transition-colors hover:bg-muted/30">
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2 font-medium text-foreground">
                              {r.is_system ? (
                                <Lock
                                  className="size-3.5 shrink-0 text-muted-foreground"
                                  aria-label="قانون سیستمی"
                                />
                              ) : null}
                              <span>{r.name}</span>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-muted-foreground whitespace-nowrap">
                            {ALERT_TYPE_LABELS[r.alert_type] ?? r.alert_type}
                          </td>
                          <td className="px-4 py-3 tabular-nums whitespace-nowrap">
                            {formatThreshold(r.threshold_value)}
                          </td>
                          <td className="px-4 py-3">
                            <div className="flex flex-wrap gap-1">
                              {splitRoles(r.notify_roles).map((role) => (
                                <span
                                  key={role}
                                  className="rounded-md bg-muted px-2 py-0.5 text-xs text-foreground/80 whitespace-nowrap"
                                >
                                  {formatRoleLabel(role, t)}
                                </span>
                              ))}
                            </div>
                          </td>
                          <td className="px-4 py-3 text-muted-foreground tabular-nums whitespace-nowrap">
                            {r.cooldown_hours != null
                              ? `${Number(r.cooldown_hours).toLocaleString("fa-IR")} ساعت`
                              : "—"}
                          </td>
                          <td className="px-4 py-3">
                            <label className="inline-flex cursor-pointer items-center gap-2 whitespace-nowrap">
                              <Switch
                                checked={r.is_active}
                                disabled={toggleRule.isPending && toggleRule.variables?.id === r.id}
                                onCheckedChange={(checked) =>
                                  toggleRule.mutate({ id: r.id, is_active: checked })
                                }
                                aria-label={`فعال‌سازی ${r.name}`}
                              />
                              <span
                                className={
                                  r.is_active ? "text-xs text-foreground" : "text-xs text-muted-foreground"
                                }
                              >
                                {r.is_active ? "فعال" : "غیرفعال"}
                              </span>
                            </label>
                          </td>
                          <td className="px-4 py-3 text-end">
                            {!r.is_system ? (
                              <Button
                                size="icon"
                                variant="ghost"
                                className="size-8 text-muted-foreground hover:text-destructive"
                                loading={deleteRule.isPending && deleteRule.variables === r.id}
                                onClick={() => deleteRule.mutate(r.id)}
                                aria-label={`حذف ${r.name}`}
                              >
                                {deleteRule.isPending && deleteRule.variables === r.id ? null : (
                                  <Trash2 className="size-4" />
                                )}
                              </Button>
                            ) : null}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </TabsContent>
        ) : null}
      </Tabs>

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
  const { t, i18n } = useTranslation();
  const { projectId = "" } = useParams();
  return (
    <ProjectProvider projectId={projectId}>
      <AlertCenterContent />
    </ProjectProvider>
  );
}
