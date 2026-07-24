import {
  Legend,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from "recharts";
import type { PerformanceScore } from "@/app/lib/api/subcontractors";
import { chartColor } from "@/design/tokens";

const AXES = [
  { key: "progress_score", label: "پیشرفت" },
  { key: "quality_score", label: "کیفیت" },
  { key: "hse_score", label: "HSE" },
  { key: "payment_compliance_score", label: "پرداخت" },
  { key: "cooperation_score", label: "همکاری" },
] as const;

function buildChartData(latest: PerformanceScore | null, history: PerformanceScore[]) {
  const avg: Record<string, number> = {};
  for (const axis of AXES) {
    const vals = history
      .map((s) => s[axis.key])
      .filter((v): v is number => v != null);
    avg[axis.key] = vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
  }
  return AXES.map((axis) => ({
    subject: axis.label,
    latest: latest ? Number(latest[axis.key] ?? 0) : 0,
    average: avg[axis.key] ?? 0,
  }));
}

interface Props {
  latest: PerformanceScore | null;
  history: PerformanceScore[];
}

export function PerformanceRadarChart({ latest, history }: Props) {
  const data = buildChartData(latest, history);
  const latestColor = chartColor("brand");
  const averageColor = chartColor("neutral");
  return (
    <ResponsiveContainer width="100%" height={320}>
      <RadarChart data={data} cx="50%" cy="50%" outerRadius="75%">
        <PolarGrid />
        <PolarAngleAxis dataKey="subject" />
        <PolarRadiusAxis angle={90} domain={[0, 10]} />
        <Radar name="آخرین ارزیابی" dataKey="latest" stroke={latestColor} fill={latestColor} fillOpacity={0.4} />
        <Radar name="میانگین" dataKey="average" stroke={averageColor} fill="transparent" strokeWidth={2} />
        <Legend />
      </RadarChart>
    </ResponsiveContainer>
  );
}
