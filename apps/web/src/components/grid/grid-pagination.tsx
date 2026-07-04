import { Button } from "@/components/form";
import { cn } from "@/app/lib/utils";
import { getPageCount, shouldShowPagination } from "@/components/grid/pagination";
import { useTranslation } from "react-i18next";

export interface GridPaginationProps {
  name: string;
  pageIndex: number;
  pageSize: number;
  totalCount: number;
  onPageIndexChange: (pageIndex: number) => void;
  isLoading?: boolean;
  className?: string;
}

// Function to manage GridPagination
export function GridPagination({
  name,
  pageIndex,
  pageSize,
  totalCount,
  onPageIndexChange,
  isLoading = false,
  className,
}: GridPaginationProps) {
  const { t } = useTranslation();
  // Variable holding totalPages
  const totalPages = getPageCount(totalCount, pageSize);

  if (!shouldShowPagination(totalCount, pageSize)) {
    return null;
  }

  // Variable holding canPrev
  const canPrev = pageIndex > 0;
  // Variable holding canNext
  const canNext = pageIndex + 1 < totalPages;

  return (
    <div
      id={`container-gridPagination-${name}`}
      className={cn(
        "flex flex-col gap-2 border-border border-t px-3 py-3 sm:flex-row sm:items-center sm:justify-between sm:px-4",
        className,
      )}
    >
      <p
        id={`text-gridPaginationInfo-${name}`}
        className="text-muted-foreground text-sm"
      >
        {t("grid.pageInfo", {
          page: pageIndex + 1,
          totalPages,
          count: totalCount,
        })}
      </p>
      <div
        id={`container-gridPaginationActions-${name}`}
        className="flex flex-wrap gap-2"
      >
        <Button
          id={`button-gridPaginationPrev-${name}`}
          type="button"
          variant="outline"
          size="sm"
          disabled={!canPrev || isLoading}
          onClick={() => onPageIndexChange(Math.max(0, pageIndex - 1))}
        >
          {t("grid.prev")}
        </Button>
        <Button
          id={`button-gridPaginationNext-${name}`}
          type="button"
          variant="outline"
          size="sm"
          disabled={!canNext || isLoading}
          onClick={() => onPageIndexChange(pageIndex + 1)}
        >
          {t("grid.next")}
        </Button>
      </div>
    </div>
  );
}
