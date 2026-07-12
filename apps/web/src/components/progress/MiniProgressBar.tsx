export function MiniProgressBar({
  plannedPct,
  actualPct,
}: {
  plannedPct: number;
  actualPct: number;
}) {
  return (
    <div className="relative h-2 w-full min-w-[80px] overflow-hidden rounded-full bg-muted">
      <div
        className="absolute inset-y-0 start-0 rounded-full bg-slate-400/70"
        style={{ width: `${Math.min(plannedPct, 100)}%` }}
      />
      <div
        className="absolute inset-y-0 start-0 rounded-full bg-emerald-500"
        style={{ width: `${Math.min(actualPct, 100)}%` }}
      />
    </div>
  );
}
