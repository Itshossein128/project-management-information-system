import {
  WARNING_TYPE_COLORS,
  WARNING_TYPE_LABELS,
  type SubcontractorWarning,
} from "@/app/lib/api/subcontractors";
import { Button } from "@/components/ui/sprint-button";

interface Props {
  warnings: SubcontractorWarning[];
  canEdit: boolean;
  onResolve: (w: SubcontractorWarning) => void;
}

export function WarningTimeline({ warnings, canEdit, onResolve }: Props) {
  if (!warnings.length) {
    return <p className="text-sm text-muted-foreground">اخطاری ثبت نشده است.</p>;
  }

  return (
    <div className="space-y-4">
      {warnings.map((w) => (
        <div
          key={w.id}
          className={`rounded-lg border p-4 ${w.resolved ? "opacity-60" : ""}`}
        >
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`rounded px-2 py-0.5 text-xs font-medium ${WARNING_TYPE_COLORS[w.warning_type] ?? ""}`}
            >
              {WARNING_TYPE_LABELS[w.warning_type] ?? w.warning_type}
            </span>
            <span className="text-sm text-muted-foreground">{w.warning_date}</span>
            {w.resolved ? (
              <span className="text-xs text-muted-foreground line-through">
                رفع شد در {w.resolved_date}
              </span>
            ) : (
              <span className="rounded bg-danger-100 px-2 py-0.5 text-xs text-danger-800">رفع نشده</span>
            )}
          </div>
          <p className={`mt-2 text-sm ${w.resolved ? "line-through" : ""}`}>{w.reason}</p>
          {!w.resolved && canEdit ? (
            <Button variant="secondary" size="sm" className="mt-2" onClick={() => onResolve(w)}>
              ثبت رفع
            </Button>
          ) : null}
        </div>
      ))}
    </div>
  );
}
