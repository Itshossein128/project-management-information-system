import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type ColumnFiltersState,
  type PaginationState,
  type RowSelectionState,
  type SortingState,
} from "@tanstack/react-table";
import { cn } from "@/app/lib/utils";
import { useEffect, useMemo, useState, type ReactNode } from "react";
import { GridPagination } from "./grid-pagination";
import { getPageCount, shouldShowPagination } from "./pagination";
import { GridToolbar } from "./toolbar";

export interface DataTableProps<TData> {
  name: string;
  columns: ColumnDef<TData, unknown>[];
  data: TData[];
  emptyMessage?: string;
  className?: string;

  manual?: boolean;

  sorting?: SortingState;
  onSortingChange?: (updater: SortingState) => void;

  pagination?: PaginationState;
  onPaginationChange?: (updater: PaginationState) => void;
  pageCount?: number;
  /** Total row count from API (`count` or `total`). Drives pagination footer. */
  totalCount?: number;
  isLoading?: boolean;

  globalFilter?: string;
  onGlobalFilterChange?: (value: string) => void;
  columnFilters?: ColumnFiltersState;
  onColumnFiltersChange?: (updater: ColumnFiltersState) => void;

  enableRowSelection?: boolean;
  rowSelection?: RowSelectionState;
  onRowSelectionChange?: (updater: RowSelectionState) => void;
  getRowId?: (originalRow: TData, index: number, parent?: unknown) => string;

  toolbar?: ReactNode;
  toolbarLeftSlot?: ReactNode;
  toolbarRightSlot?: ReactNode;
  searchPlaceholder?: string;
}

export function DataTable<TData>({
  name,
  columns,
  data,
  emptyMessage = "No rows to display.",
  className,
  manual = false,

  sorting: sortingProp,
  onSortingChange,

  pagination: paginationProp,
  onPaginationChange,
  pageCount: pageCountProp,
  totalCount = 0,
  isLoading = false,

  globalFilter,
  onGlobalFilterChange,
  columnFilters: columnFiltersProp,
  onColumnFiltersChange,

  enableRowSelection = false,
  rowSelection: rowSelectionProp,
  onRowSelectionChange,
  getRowId,

  toolbar,
  toolbarLeftSlot,
  toolbarRightSlot,
  searchPlaceholder,
}: DataTableProps<TData>) {
  const [sortingInternal, setSortingInternal] = useState<SortingState>([]);
  const [paginationInternal, setPaginationInternal] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 20,
  });
  const [columnFiltersInternal, setColumnFiltersInternal] =
    useState<ColumnFiltersState>([]);
  const [rowSelectionInternal, setRowSelectionInternal] =
    useState<RowSelectionState>({});

  const sorting = sortingProp ?? sortingInternal;
  const pagination = paginationProp ?? paginationInternal;
  const pageCount =
    pageCountProp ??
    (manual && totalCount > 0
      ? getPageCount(totalCount, pagination.pageSize)
      : undefined);
  const showPaginationFooter =
    manual &&
    paginationProp != null &&
    onPaginationChange != null &&
    shouldShowPagination(totalCount, pagination.pageSize);
  const columnFilters = columnFiltersProp ?? columnFiltersInternal;
  const rowSelection = rowSelectionProp ?? rowSelectionInternal;

  const showToolbar =
    toolbar != null ||
    typeof onGlobalFilterChange === "function" ||
    toolbarLeftSlot != null ||
    toolbarRightSlot != null;

  useEffect(() => {
    if (!manual || !onPaginationChange || pageCount == null) return;
    const maxIndex = pageCount - 1;
    if (pagination.pageIndex > maxIndex) {
      onPaginationChange({ ...pagination, pageIndex: Math.max(0, maxIndex) });
    }
  }, [
    manual,
    onPaginationChange,
    pageCount,
    pagination.pageIndex,
    pagination.pageSize,
    pagination,
  ]);

  const withSelectionColumns = useMemo<ColumnDef<TData, unknown>[]>(() => {
    if (!enableRowSelection) return columns;

    const selectionColumn: ColumnDef<TData, unknown> = {
      id: "__select",
      header: ({ table }) => (
        <div id={`container-gridSelectAll-${name}`} className="flex items-center">
          <input
            id={`checkbox-gridSelectAll-${name}`}
            type="checkbox"
            checked={table.getIsAllPageRowsSelected()}
            ref={(el) => {
              if (!el) return;
              el.indeterminate =
                table.getIsSomePageRowsSelected() &&
                !table.getIsAllPageRowsSelected();
            }}
            onChange={table.getToggleAllPageRowsSelectedHandler()}
            aria-label="Select all rows"
          />
        </div>
      ),
      cell: ({ row }) => (
        <div
          id={`container-gridSelectRow-${name}-${row.index}`}
          className="flex items-center"
        >
          <input
            id={`checkbox-gridSelectRow-${name}-${row.index}`}
            type="checkbox"
            checked={row.getIsSelected()}
            disabled={!row.getCanSelect()}
            onChange={row.getToggleSelectedHandler()}
            aria-label={`Select row ${row.index + 1}`}
          />
        </div>
      ),
      enableSorting: false,
      enableHiding: false,
      size: 44,
    };

    return [selectionColumn, ...columns];
  }, [columns, enableRowSelection, name]);

  const table = useReactTable({
    data,
    columns: withSelectionColumns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: manual ? undefined : getSortedRowModel(),
    getFilteredRowModel: manual ? undefined : getFilteredRowModel(),
    getPaginationRowModel: manual ? undefined : getPaginationRowModel(),
    manualSorting: manual,
    manualFiltering: manual,
    manualPagination: manual,
    onSortingChange: (updater) => {
      const next =
        typeof updater === "function" ? updater(sorting) : updater;
      onSortingChange?.(next);
      setSortingInternal(next);
    },
    onPaginationChange: (updater) => {
      const next =
        typeof updater === "function" ? updater(pagination) : updater;
      onPaginationChange?.(next);
      setPaginationInternal(next);
    },
    onColumnFiltersChange: (updater) => {
      const next =
        typeof updater === "function" ? updater(columnFilters) : updater;
      onColumnFiltersChange?.(next);
      setColumnFiltersInternal(next);
    },
    onRowSelectionChange: (updater) => {
      const next =
        typeof updater === "function" ? updater(rowSelection) : updater;
      onRowSelectionChange?.(next);
      setRowSelectionInternal(next);
    },
    onGlobalFilterChange: (updater) => {
      const next = typeof updater === "function" ? updater(globalFilter ?? "") : updater;
      onGlobalFilterChange?.(String(next));
    },
    enableRowSelection,
    getRowId,
    pageCount,
    state: {
      sorting,
      pagination,
      columnFilters,
      globalFilter: globalFilter ?? "",
      rowSelection,
    },
  });

  return (
    <div
      id={`container-dataTable-${name}`}
      className={cn("surface-panel", className)}
    >
      {showToolbar ? (
        toolbar ? (
          <div
            id={`container-gridToolbarCustom-${name}`}
            className="border-border border-b p-3 sm:p-4"
          >
            {toolbar}
          </div>
        ) : (
          <div className="border-border border-b p-3 sm:p-4">
            <GridToolbar
              name={name}
              searchValue={globalFilter ?? ""}
              searchPlaceholder={searchPlaceholder}
              onSearchChange={onGlobalFilterChange ?? (() => {})}
              leftSlot={toolbarLeftSlot}
              rightSlot={toolbarRightSlot}
            />
          </div>
        )
      ) : null}
      <div
        id={`container-dataTableScroll-${name}`}
        className="overflow-x-auto overscroll-x-contain"
      >
        <table
          id={`grid-${name}`}
          className="w-full min-w-0 border-collapse text-sm sm:min-w-[480px]"
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
                    className="px-3 py-2 text-start font-medium text-muted-foreground sm:px-4 sm:py-3"
                  >
                    {header.isPlaceholder ? null : header.column.getCanSort() ? (
                      <button
                        id={`button-sort-${name}-${header.id}`}
                        type="button"
                        className="inline-flex items-center gap-1 hover:text-foreground"
                        onClick={header.column.getToggleSortingHandler()}
                      >
                        <span id={`text-sortLabel-${name}-${header.id}`}>
                          {flexRender(
                            header.column.columnDef.header,
                            header.getContext(),
                          )}
                        </span>
                        <span
                          id={`text-sortDirection-${name}-${header.id}`}
                          className="text-xs"
                        >
                          {header.column.getIsSorted() === "asc"
                            ? "▲"
                            : header.column.getIsSorted() === "desc"
                              ? "▼"
                              : "↕"}
                        </span>
                      </button>
                    ) : (
                      flexRender(
                        header.column.columnDef.header,
                        header.getContext(),
                      )
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
                  colSpan={withSelectionColumns.length}
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
                      className="px-3 py-2 align-middle text-foreground sm:px-4 sm:py-3"
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
      {showPaginationFooter ? (
        <GridPagination
          name={name}
          pageIndex={pagination.pageIndex}
          pageSize={pagination.pageSize}
          totalCount={totalCount}
          isLoading={isLoading}
          onPageIndexChange={(nextIndex) =>
            onPaginationChange?.({
              ...pagination,
              pageIndex: nextIndex,
            })
          }
        />
      ) : null}
    </div>
  );
}
