import { Link } from "react-router";
import { PATHS } from "@/app/routeVars";
import { isoToJalali } from "@/app/lib/jalali-utils";
import type { ProgressHistoryRow } from "@/app/lib/api/progress";
import { EmptyState } from "@/components/layout/empty-state";
import { cn } from "@/app/lib/utils";

export function ProgressHistoryTable({
  projectId,
  rows,
}: {
  projectId: string;
  rows: ProgressHistoryRow[];
}) {
  if (rows.length === 0) {
    return (
      <EmptyState
        title="هنوز گزارش تأیید‌شده‌ای ثبت نشده است"
        description="پس از تأیید گزارش‌های روزانه، تاریخچه پیشرفت اینجا نمایش داده می‌شود."
      />
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="w-full min-w-[720px] text-sm">
        <thead className="bg-muted/50">
          <tr>
            {["تاریخ", "پیشرفت برنامه", "پیشرفت واقعی", "انحراف", "تأییدکننده", "گزارش"].map((h) => (
              <th key={h} className="px-3 py-2 text-start font-medium">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.report_id} className="border-t border-border">
              <td className="px-3 py-2">{isoToJalali(row.date)}</td>
              <td className="px-3 py-2">{row.planned_pct.toFixed(1)}٪</td>
              <td className="px-3 py-2">{row.actual_pct.toFixed(1)}٪</td>
              <td
                className={cn(
                  "px-3 py-2 font-medium",
                  row.variance_pct < 0 ? "text-red-600" : row.variance_pct > 0 ? "text-emerald-600" : "",
                )}
              >
                {row.variance_pct > 0 ? "+" : ""}
                {row.variance_pct.toFixed(1)}٪
              </td>
              <td className="px-3 py-2">{row.approved_by_name || "—"}</td>
              <td className="px-3 py-2">
                <Link
                  to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_DAILY_REPORTS}/${row.report_id}/view`}
                  className="text-primary hover:underline"
                >
                  مشاهده
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
