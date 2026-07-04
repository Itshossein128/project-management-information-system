/** 1-based API page from TanStack zero-based page index. */
// Function to manage apiPageFromIndex
export function apiPageFromIndex(pageIndex: number): number {
  return pageIndex + 1;
}

// Function to manage getPageCount
export function getPageCount(totalCount: number, pageSize: number): number {
  if (pageSize <= 0) return 1;
  return Math.max(1, Math.ceil(totalCount / pageSize));
}

// Function to manage shouldShowPagination
export function shouldShowPagination(
  totalCount: number,
  pageSize: number,
): boolean {
  return totalCount > pageSize;
}
