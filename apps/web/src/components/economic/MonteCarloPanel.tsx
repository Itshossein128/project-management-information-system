import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import {
  fetchLatestSimulation,
  fetchSimulationStatus,
  formatFaAmount,
  runSimulation,
  simPercentile,
  type SimulationResult,
} from "@/app/lib/api/economic";
import { Button } from "@/components/ui/sprint-button";

export function MonteCarloPanel({ projectId }: { projectId: string }) {
  const [iterations, setIterations] = useState(5000);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [simResult, setSimResult] = useState<SimulationResult | Record<string, unknown> | null>(null);
  const [params, setParams] = useState({
    inflation_rate_mean: 0.3,
    payment_delay_mean: 45,
    cost_overrun_mean: 1.05,
    productivity_factor_mean: 1.0,
  });

  const { data: latestSim } = useQuery({
    queryKey: ["sim-latest", projectId],
    queryFn: () => fetchLatestSimulation(projectId),
    enabled: !simResult,
  });

  const simulate = useMutation({
    mutationFn: () => runSimulation(projectId, { iterations, scenario_params: params }),
    onSuccess: (data) => setTaskId(data.task_id),
  });

  useEffect(() => {
    if (!taskId) return;
    const timer = setInterval(async () => {
      const status = await fetchSimulationStatus(projectId, taskId);
      if (status.status === "done" && status.result) {
        setSimResult(status.result as unknown as SimulationResult);
        setTaskId(null);
        clearInterval(timer);
      }
    }, 2000);
    return () => clearInterval(timer);
  }, [taskId, projectId]);

  const sim = simResult ?? latestSim?.result;
  const probLoss = sim ? Number(sim.prob_of_loss ?? 0) : 0;
  const maxWc = sim ? Number((sim as SimulationResult).max_working_capital ?? 0) : 0;

  return (
    <div className="rounded-lg border p-6 space-y-4" data-testid="monte-carlo-panel">
      <h3 className="font-semibold">شبیه‌سازی مونت‌کارلو</h3>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {(
          [
            ["نرخ تورم", "inflation_rate_mean", 0.5],
            ["تأخیر پرداخت (روز)", "payment_delay_mean", 90],
            ["ضریب اضافه هزینه", "cost_overrun_mean", 1.5],
            ["بهره‌وری", "productivity_factor_mean", 1.5],
          ] as const
        ).map(([label, key, max]) => (
          <label key={key} className="text-sm">
            {label}: {params[key]}
            <input
              data-testid={key === "productivity_factor_mean" ? "monte-carlo-productivity" : undefined}
              type="range"
              min={key === "productivity_factor_mean" ? 0.5 : 0}
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
      <Button
        variant="primary"
        onClick={() => simulate.mutate()}
        disabled={simulate.isPending || Boolean(taskId)}
        data-testid="run-simulation"
      >
        {taskId ? `در حال اجرای ${iterations.toLocaleString("fa-IR")} سناریو...` : "اجرای شبیه‌سازی"}
      </Button>
      {sim ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          {(
            [
              ["بدبینانه P10", "p10"],
              ["محتمل P50", "p50"],
              ["خوش‌بینانه P90", "p90"],
            ] as const
          ).map(([label, key]) => (
            <div key={key} className="rounded border p-3 text-center" data-testid={`sim-${key}`}>
              <p className="text-xs text-muted-foreground">{label}</p>
              <p className="text-lg font-semibold">{formatFaAmount(simPercentile(sim, key))}</p>
            </div>
          ))}
          <div className="rounded border p-3 text-center" data-testid="max-working-capital">
            <p className="text-xs text-muted-foreground">حداکثر سرمایه در گردش (P90)</p>
            <p className="text-lg font-semibold">{formatFaAmount(maxWc)}</p>
          </div>
          <div className="rounded border p-3 text-center">
            <p className="text-xs text-muted-foreground">احتمال زیان</p>
            <p
              className={`text-lg font-semibold ${probLoss > 0.3 ? "text-danger-600" : probLoss > 0.1 ? "text-warning-600" : "text-success-600"}`}
            >
              {(probLoss * 100).toFixed(1)}٪
            </p>
          </div>
        </div>
      ) : null}
    </div>
  );
}
