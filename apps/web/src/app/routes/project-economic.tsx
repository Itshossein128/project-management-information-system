import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useParams } from "react-router";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import {
  fetchEconomicSnapshot,
  fetchFinancingCost,
  fetchLatestSimulation,
  fetchSimulationStatus,
  formatFaAmount,
  runSimulation,
} from "@/app/lib/api/economic";
import { LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/sprint-button";

function profitColor(v: number) {
  return v >= 0 ? "#059669" : "#dc2626";
}

function EconomicContent() {
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_dashboard");

  const [iterations, setIterations] = useState(5000);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [simResult, setSimResult] = useState<Record<string, unknown> | null>(null);
  const [params, setParams] = useState({
    inflation_rate_mean: 0.3,
    payment_delay_mean: 45,
    cost_overrun_mean: 1.05,
  });

  const { data: snapshot, isLoading: loadingSnap } = useQuery({
    queryKey: ["economic-snapshot", projectId],
    queryFn: () => fetchEconomicSnapshot(projectId),
    enabled: canView,
  });

  const { data: financing } = useQuery({
    queryKey: ["financing", projectId],
    queryFn: () => fetchFinancingCost(projectId),
    enabled: canView,
  });

  const { data: latestSim } = useQuery({
    queryKey: ["sim-latest", projectId],
    queryFn: () => fetchLatestSimulation(projectId),
    enabled: canView && !simResult,
  });

  const simulate = useMutation({
    mutationFn: () =>
      runSimulation(projectId, { iterations, scenario_params: params }),
    onSuccess: (data) => setTaskId(data.task_id),
  });

  useEffect(() => {
    if (!taskId) return;
    const timer = setInterval(async () => {
      const status = await fetchSimulationStatus(projectId, taskId);
      if (status.status === "done" && status.result) {
        setSimResult(status.result);
        setTaskId(null);
        clearInterval(timer);
      }
    }, 2000);
    return () => clearInterval(timer);
  }, [taskId, projectId]);

  if (isLoading || loadingSnap) return <LoadingSkeleton rows={12} />;
  if (!project) return <p>پروژه یافت نشد</p>;
  if (!canView) return <p className="p-8 text-center text-muted-foreground">دسترسی ندارید.</p>;
  if (!snapshot) return null;

  const profitBars = [
    { name: "حسابداری", value: snapshot.accounting_profit },
    { name: "واقعی", value: snapshot.real_profit },
    { name: "اقتصادی", value: snapshot.economic_profit },
  ];

  const sim = simResult ?? latestSim?.result;
  const probLoss = sim ? Number((sim as { prob_of_loss?: number }).prob_of_loss ?? 0) : 0;

  return (
    <div className="space-y-8">
      <PageHeader title="تحلیل اقتصادی" subtitle={project.project_name} />

      <div className="grid gap-4 md:grid-cols-3">
        {[
          {
            title: "سود حسابداری",
            value: snapshot.accounting_profit,
            formula: "درآمد − هزینه واقعی",
            sub: `${formatFaAmount(snapshot.revenue_to_date)} − ${formatFaAmount(snapshot.actual_cost)}`,
          },
          {
            title: "سود واقعی",
            value: snapshot.real_profit,
            formula: "درآمد − هزینه تعدیل‌شده با تورم",
            sub: `تفاوت: ${formatFaAmount(snapshot.real_profit - snapshot.accounting_profit)}`,
          },
          {
            title: "سود اقتصادی",
            value: snapshot.economic_profit,
            formula: "درآمد − هزینه − تأمین مالی",
            sub: `${formatFaAmount(snapshot.financing_cost)} هزینه تأخیر`,
          },
        ].map((card) => (
          <div key={card.title} className="rounded-lg border p-4">
            <p className="text-sm text-muted-foreground">{card.title}</p>
            <p className={`text-2xl font-bold ${card.value >= 0 ? "text-emerald-600" : "text-red-600"}`}>
              {formatFaAmount(card.value)}
            </p>
            <p className="mt-1 text-xs text-muted-foreground">{card.formula}</p>
            <p className="text-xs text-amber-700">{card.sub}</p>
          </div>
        ))}
      </div>

      <div className="h-72 rounded-lg border p-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={profitBars}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis tickFormatter={(v) => formatFaAmount(v)} />
            <Tooltip formatter={(v) => formatFaAmount(Number(v ?? 0))} />
            <Bar dataKey="value">
              {profitBars.map((entry) => (
                <Cell key={entry.name} fill={profitColor(entry.value)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-lg border p-4">
          <h3 className="mb-3 font-semibold">تعدیل تورم</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                {["دسته", "اسمی", "تعدیل‌شده", "ضریب"].map((h) => (
                  <th key={h} className="py-1 text-start">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {(snapshot.inflation_detail ?? []).map((row) => (
                <tr key={row.cost_category} className="border-b">
                  <td className="py-1">{row.cost_category}</td>
                  <td className="py-1">{formatFaAmount(row.nominal_cost)}</td>
                  <td className="py-1">{formatFaAmount(row.adjusted_cost)}</td>
                  <td className="py-1">{row.inflation_factor.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="rounded-lg border p-4">
          <h3 className="mb-3 font-semibold">هزینه تأمین مالی</h3>
          <p className="mb-2 text-3xl font-bold">{financing?.avg_payment_delay_days?.toFixed(0) ?? 0} روز</p>
          <p className="mb-4 text-sm text-muted-foreground">میانگین تأخیر پرداخت</p>
          <table className="w-full text-sm">
            <tbody>
              {(financing?.details ?? []).map((d) => (
                <tr key={d.ipc_number} className="border-b">
                  <td className="py-1">IPC {d.ipc_number}</td>
                  <td className="py-1">{d.delay_days} روز</td>
                  <td className="py-1">{formatFaAmount(d.financing_cost)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="rounded-lg border p-6 space-y-4">
        <h3 className="font-semibold">شبیه‌سازی مونت‌کارلو</h3>
        <div className="grid gap-4 md:grid-cols-3">
          {(
            [
              ["نرخ تورم", "inflation_rate_mean", 0.5],
              ["تأخیر پرداخت (روز)", "payment_delay_mean", 90],
              ["ضریب اضافه هزینه", "cost_overrun_mean", 1.5],
            ] as const
          ).map(([label, key, max]) => (
            <label key={key} className="text-sm">
              {label}: {params[key]}
              <input
                type="range"
                min={0}
                max={max}
                step={0.01}
                value={params[key]}
                onChange={(e) => setParams({ ...params, [key]: Number(e.target.value) })}
                className="mt-1 w-full"
              />
            </label>
          ))}
        </div>
        <div className="flex gap-3">
          {[1000, 5000, 10000].map((n) => (
            <label key={n} className="flex items-center gap-1 text-sm">
              <input type="radio" checked={iterations === n} onChange={() => setIterations(n)} />
              {n.toLocaleString("fa-IR")}
            </label>
          ))}
        </div>
        <Button variant="primary" onClick={() => simulate.mutate()} disabled={simulate.isPending || Boolean(taskId)}>
          {taskId ? `در حال اجرای ${iterations.toLocaleString("fa-IR")} سناریو...` : "اجرای شبیه‌سازی"}
        </Button>
        {sim ? (
          <div className="grid gap-4 md:grid-cols-4">
            {[
              ["بدبینانه P10", (sim as { p10?: number }).p10],
              ["محتمل P50", (sim as { p50?: number }).p50],
              ["خوش‌بینانه P90", (sim as { p90?: number }).p90],
            ].map(([label, val]) => (
              <div key={String(label)} className="rounded border p-3 text-center">
                <p className="text-xs text-muted-foreground">{label}</p>
                <p className="text-lg font-semibold">{formatFaAmount(Number(val ?? 0))}</p>
              </div>
            ))}
            <div className="rounded border p-3 text-center">
              <p className="text-xs text-muted-foreground">احتمال زیان</p>
              <p className={`text-lg font-semibold ${probLoss > 0.3 ? "text-red-600" : probLoss > 0.1 ? "text-amber-600" : "text-emerald-600"}`}>
                {(probLoss * 100).toFixed(1)}٪
              </p>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default function ProjectEconomicPage() {
  const { projectId = "" } = useParams();
  return (
    <ProjectProvider projectId={projectId}>
      <EconomicContent />
    </ProjectProvider>
  );
}
