import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  type ColumnDef,
} from "@tanstack/react-table";
import { cn } from "@/app/lib/utils";

export interface DataTableProps<TData> {
  name: string;
  columns: ColumnDef<TData, unknown>[];
  data: TData[];
  emptyMessage?: string;
  className?: string;
}

export function DataTable<TData>({
  name,
  columns,
  data,
  emptyMessage = "No rows to display.",
  className,
}: DataTableProps<TData>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div
      id={`container-dataTable-${name}`}
      className={cn(
        "overflow-hidden rounded-xl border border-border bg-card shadow-sm",
        className,
      )}
    >
      <div id={`container-dataTableScroll-${name}`} className="overflow-x-auto">
        <table
          id={`grid-${name}`}
          className="w-full min-w-[320px] border-collapse text-sm"
        >
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr
                key={headerGroup.id}
                id={`row-headerGroup-${headerGroup.id}`}
                className="border-border border-b bg-muted/50"
              >
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    id={`text-columnHeader-${name}-${header.id}`}
                    className="px-4 py-3 text-start font-medium text-muted-foreground"
                  >
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext(),
                        )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.length === 0 ? (
              <tr id={`row-empty-${name}`}>
                <td
                  id={`text-emptyState-${name}`}
                  colSpan={columns.length}
                  className="px-4 py-10 text-center text-muted-foreground"
                >
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              table.getRowModel().rows.map((row, index) => (
                <tr
                  key={row.id}
                  id={`row-data-${name}-${index}`}
                  className="border-border border-b last:border-b-0 hover:bg-muted/30"
                >
                  {row.getVisibleCells().map((cell) => (
                    <td
                      key={cell.id}
                      id={`cell-${name}-${cell.column.id}-${index}`}
                      className="px-4 py-3 align-middle text-foreground"
                    >
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
