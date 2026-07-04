
import { useCallback, useEffect, useMemo, useState } from "react";
import type { GridState } from "./types";

export interface UseGridStateOptions {
  initial?: Partial<GridState>;
  /**
   * Preferred new option name.
   * For backward compatibility with routes using `initialPageIndex/initialPageSize`,
   * those are also supported.
   */
  pageSize?: number;
  /**
   * Preferred new option name.
   * For backward compatibility with routes using `searchDebounceMs`,
   * that is also supported.
   */
  debounceMs?: number;

  // Backward-compatible aliases used in routes
  initialPageIndex?: number;
  initialPageSize?: number;
  searchDebounceMs?: number;
}

export interface UseGridStateResult {
  state: GridState;
  /**
   * Backward-compatible view used by routes and grid components.
   * - `query.search` reflects the current input value (not debounced).
   */
  query: {
    pagination: GridState["pagination"];
    sorting: GridState["sorting"];
    search: string;
  };
  setSearch: (value: string) => void;
  searchInput: string;
  debouncedSearch: string;
  setSorting: (
    updater:
      | GridState["sorting"]
      | ((prev: GridState["sorting"]) => GridState["sorting"]),
  ) => void;
  setPagination: (
    updater:
      | GridState["pagination"]
      | ((prev: GridState["pagination"]) => GridState["pagination"]),
  ) => void;
  setColumnFilters: (
    updater:
      | GridState["columnFilters"]
      | ((prev: GridState["columnFilters"]) => GridState["columnFilters"]),
  ) => void;
  setRowSelection: (
    updater:
      | GridState["rowSelection"]
      | ((prev: GridState["rowSelection"]) => GridState["rowSelection"]),
  ) => void;
  resetPage: () => void;
}

const DEFAULT_PAGE_SIZE = 20;

// Function to manage useGridState
export function useGridState(options: UseGridStateOptions = {}): UseGridStateResult {
  // Variable holding pageSize
  const pageSize = options.initialPageSize ?? options.pageSize ?? DEFAULT_PAGE_SIZE;
  // Variable holding debounceMs
  const debounceMs = options.searchDebounceMs ?? options.debounceMs ?? 350;

  const [sorting, setSorting] = useState<GridState["sorting"]>(
    options.initial?.sorting ?? [],
  );
  const [pagination, setPagination] = useState<GridState["pagination"]>(
    options.initial?.pagination ?? {
      pageIndex: options.initialPageIndex ?? 0,
      pageSize,
    },
  );
  const [columnFilters, setColumnFilters] = useState<GridState["columnFilters"]>(
    options.initial?.columnFilters ?? [],
  );
  const [rowSelection, setRowSelection] = useState<GridState["rowSelection"]>(
    options.initial?.rowSelection ?? {},
  );

  const [searchInput, setSearchInput] = useState(options.initial?.globalFilter ?? "");
  const [debouncedSearch, setDebouncedSearch] = useState(
    options.initial?.globalFilter ?? "",
  );

  useEffect(() => {
    // Variable holding handle
    const handle = window.setTimeout(() => {
      setDebouncedSearch(searchInput);
    }, debounceMs);
    return () => window.clearTimeout(handle);
  }, [searchInput, debounceMs]);

  useEffect(() => {
    setPagination((prev) => ({ ...prev, pageIndex: 0 }));
  }, [debouncedSearch]);

  // Variable holding resetPage
  const resetPage = useCallback(() => {
    setPagination((prev) => ({ ...prev, pageIndex: 0 }));
  }, []);

  // Variable holding setSearch
  const setSearch = useCallback(
    (value: string) => {
      setSearchInput(value);
      resetPage();
    },
    [resetPage],
  );

  // Variable holding setSortingWithReset
  const setSortingWithReset = useCallback(
    (
      updater:
        | GridState["sorting"]
        | ((prev: GridState["sorting"]) => GridState["sorting"]),
    ) => {
      setSorting(updater);
      resetPage();
    },
    [resetPage],
  );

  // Variable holding state
  const state = useMemo<GridState>(
    () => ({
      sorting,
      pagination,
      columnFilters,
      globalFilter: debouncedSearch,
      rowSelection,
    }),
    [sorting, pagination, columnFilters, debouncedSearch, rowSelection],
  );

  return {
    state,
    query: {
      pagination,
      sorting,
      search: searchInput,
    },
    setSearch,
    searchInput,
    debouncedSearch,
    setSorting: setSortingWithReset,
    setPagination,
    setColumnFilters,
    setRowSelection,
    resetPage,
  };
}

