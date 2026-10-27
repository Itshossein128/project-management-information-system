import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 15_000,
    },
  },
});

// Detail includes actor-specific capabilities; history includes private reasons.
// Cancel before eviction so a late response cannot refill another session's key.
export function clearProjectSessionQueries() {
  const prefixes = new Set(["project", "businesses", "unit-section", "status-undo-history", "status-undo-preview"]);
  const filters = { predicate: (query: { queryKey: readonly unknown[] }) => prefixes.has(String(query.queryKey[0])) };
  void queryClient.cancelQueries(filters);
  queryClient.removeQueries(filters);
}

