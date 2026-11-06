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
  void queryClient.cancelQueries();
  queryClient.clear();
}

