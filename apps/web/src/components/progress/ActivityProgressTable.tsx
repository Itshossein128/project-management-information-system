import { Link } from "react-router";
import { PATHS } from "@/app/routeVars";
import { isoToJalali } from "@/app/lib/jalali-utils";
import type { ActivityProgressRow } from "@/app/lib/api/progress";
import { EmptyState } from "@/components/layout/empty-state";
import { Badge } from "@/components/ui/badge";
import { MiniProgressBar } from "@/components/progress/MiniProgressBar";
import { cn } from "@/app/lib/utils";

const STATUS_LABELS: Record<string, { label: string; variant: "neutral" | "info" | "warning" | "success" }> = {
  not_started: { label: "شروع نشده", variant: "neutral" },
  in_progress: { label: "در حال اجرا", variant: "info" },
  suspended: { label: "متوقف", variant: "warning" },
  completed: { label: "تکمیل شده", variant: "success" },
};

export function ActivityProgressTable({
  projectId,
  rows,
}: {
  projectId: string;
  rows: ActivityProgressRow[];
}) {
  if (rows.length === 0) {
    return (
      <EmptyState
        title="فعالیتی با وزن تعریف‌شده یافت نشد"
        description="برای نمایش پیشرفت، وزن فعالیت‌ها را در فهرست فعالیت‌ها تنظیم کنید."
      />
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="w-full min-w-[1100px] text-sm">
        <thead className="bg-muted/50">
          <tr>
            {[
              "کد",
              "نام فعالیت",
              "WBS",
              "وزن",
              "برنامه٪",
              "واقعی٪",
              "انحراف",
              "مقدار کل",
              "مقدار انجام شده",
              "واحد",
              "وضعیت",
              "آخرین به‌روزرسانی",
            ].map((h) => (
              <th key={h} className="px-3 py-2 text-start font-medium">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const status = STATUS_LABELS[row.status] ?? { label: row.status, variant: "neutral" as const };
            return (
              <tr key={row.activity_id} className="border-t border-border hover:bg-muted/30">
                <td className="px-3 py-2">
                  <Link
                    to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_ACTIVITIES}`}
                    className="text-primary hover:underline"
                  >
                    {row.activity_code}
                  </Link>
                </td>
                <td className="px-3 py-2">{row.activity_name}</td>
                <td className="px-3 py-2">{row.wbs_name || "—"}</td>
                <td className="px-3 py-2">
                  {row.weight != null ? `${(row.weight * 100).toFixed(2)}٪` : "—"}
                </td>
                <td className="px-3 py-2">{row.planned_progress_pct.toFixed(1)}٪</td>
                <td className="px-3 py-2">
                  <div className="flex min-w-[120px] flex-col gap-1">
                    <span>{row.actual_progress_pct.toFixed(1)}٪</span>
                    <MiniProgressBar
                      plannedPct={row.planned_progress_pct}
                      actualPct={row.actual_progress_pct}
                    />
                  </div>
                </td>
                <td
                  className={cn(
                    "px-3 py-2 font-medium",
                    row.variance_pct < 0 ? "text-danger-600" : row.variance_pct > 0 ? "text-success-600" : "",
                  )}
                >
                  {row.variance_pct > 0 ? "+" : ""}
                  {row.variance_pct.toFixed(1)}٪
                </td>
                <td className="px-3 py-2">{row.total_quantity ?? "—"}</td>
                <td className="px-3 py-2">{row.cumulative_quantity ?? "—"}</td>
                <td className="px-3 py-2">{row.unit || "—"}</td>
                <td className="px-3 py-2">
                  <div className="flex flex-wrap items-center gap-1">
                    <Badge variant={status.variant} label={status.label} />
                    {row.is_behind ? <Badge variant="danger" label="تأخیر" /> : null}
                  </div>
                </td>
                <td className="px-3 py-2">
                  {row.last_update_date ? isoToJalali(row.last_update_date) : "—"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
