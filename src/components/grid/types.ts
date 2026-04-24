import type {
  ColumnFiltersState,
  PaginationState,
  RowSelectionState,
  SortingState,
  Updater,
} from "@tanstack/react-table";

export type GridFilters = Record<
  string,
  string | number | boolean | null | undefined
>;

export interface GridServerMeta {
  totalCount: number;
  pageCount: number;
}

export type GridSortingState = SortingState;
export type GridColumnFiltersState = ColumnFiltersState;
export type GridPaginationState = PaginationState;
export type GridRowSelectionState = RowSelectionState;

export interface GridState {
  sorting: GridSortingState;
  pagination: GridPaginationState;
  columnFilters: GridColumnFiltersState;
  globalFilter: string;
  rowSelection: GridRowSelectionState;
}

export interface GridQueryState {
  pagination: GridPaginationState;
  sorting: GridSortingState;
  search: string;
  filters: GridFilters;
}

export type GridStateUpdater = Updater<GridState>;

