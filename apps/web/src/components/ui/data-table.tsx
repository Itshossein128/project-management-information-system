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

  return (
    <div className="overflow-x-auto rounded-xl border border-border/80 bg-card shadow-[var(--shadow-card)]">
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
                  {col.render ? col.render(row) : String((row as Record<string, unknown>)[col.key] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
