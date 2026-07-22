import { cn } from "src/app/lib/utils";
import { LoadingSkeleton } from "src/components/layout/page-header";

export interface Column<T> {
  key: string;
  label: string;
  render?: (row: T) => React.ReactNode;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  emptyMessage?: string;
  onRowClick?: (row: T) => void;
  rowKey: (row: T) => string;
}

export function DataTable<T>({
  columns,
  data,
  loading,
  emptyMessage = "داده‌ای یافت نشد",
  onRowClick,
  rowKey,
}: DataTableProps<T>) {
  if (loading) {
    return <LoadingSkeleton rows={6} />;
  }

  if (data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border py-16 text-center text-muted-foreground">
        <p>{emptyMessage}</p>
      </div>
    );
  }

  const cellContent = (col: Column<T>, row: T) =>
    col.render
      ? col.render(row)
      : String((row as Record<string, unknown>)[col.key] ?? "");

  return (
    <>
      {/* Mobile (< sm): stacked cards — avoids the table's horizontal scroll */}
      <div className="flex flex-col gap-3 sm:hidden">
        {data.map((row) => {
          const labelled = columns.filter((c) => c.label);
          const unlabelled = columns.filter((c) => !c.label);
          return (
            <div
              key={rowKey(row)}
              role={onRowClick ? "button" : undefined}
              tabIndex={onRowClick ? 0 : undefined}
              onClick={() => onRowClick?.(row)}
              onKeyDown={(e) => {
                if (onRowClick && (e.key === "Enter" || e.key === " ")) {
                  e.preventDefault();
                  onRowClick(row);
                }
              }}
              className={cn(
                "rounded-xl border border-border/80 bg-card p-4 shadow-[var(--shadow-card)]",
                onRowClick &&
                  "card-interactive cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-ring/50",
              )}
            >
              <dl className="flex flex-col gap-2.5">
                {labelled.map((col) => (
                  <div
                    key={col.key}
                    className="flex items-start justify-between gap-3"
                  >
                    <dt className="shrink-0 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                      {col.label}
                    </dt>
                    <dd className="min-w-0 break-words text-end font-medium">
                      {cellContent(col, row)}
                    </dd>
                  </div>
                ))}
              </dl>
              {unlabelled.length > 0 ? (
                <div className="mt-3 flex flex-wrap items-center justify-end gap-2 border-t border-border/60 pt-3">
                  {unlabelled.map((col) => (
                    <div key={col.key}>{cellContent(col, row)}</div>
                  ))}
                </div>
              ) : null}
            </div>
          );
        })}
      </div>

      {/* Desktop (>= sm): table */}
      <div className="hidden overflow-x-auto rounded-xl border border-border/80 bg-card shadow-[var(--shadow-card)] sm:block">
        <table className="w-full min-w-[640px] text-sm">
          <thead>
            <tr className="border-b border-border/80 bg-muted/40">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="px-4 py-3 text-start text-xs font-semibold uppercase tracking-wide text-muted-foreground"
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr
                key={rowKey(row)}
                className={cn(
                  "border-b border-border/60 transition-colors duration-150 last:border-0",
                  onRowClick &&
                    "cursor-pointer hover:bg-brand-50/60 dark:hover:bg-brand-950/30",
                )}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-3">
                    {cellContent(col, row)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
