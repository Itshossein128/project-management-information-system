/** 1-based API page from TanStack zero-based page index. */
export function apiPageFromIndex(pageIndex: number): number {
  return pageIndex + 1;
}

export function getPageCount(totalCount: number, pageSize: number): number {
  if (pageSize <= 0) return 1;
  return Math.max(1, Math.ceil(totalCount / pageSize));
}

export function shouldShowPagination(
  totalCount: number,
  pageSize: number,
): boolean {
  return totalCount > pageSize;
}
