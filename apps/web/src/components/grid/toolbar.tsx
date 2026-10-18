import type * as React from "react";

import { Button, Input } from "@/components/form";
import { cn } from "@/app/lib/utils";

export interface GridToolbarProps {
  name: string;
  searchValue: string;
  onSearchChange: (next: string) => void;
  searchPlaceholder?: string;
  className?: string;

  leftSlot?: React.ReactNode;
  onNewClick?: () => void;
  newLabel?: string;

  onImportClick?: () => void;
  importLabel?: string;

  onExportClick?: () => void;
  exportLabel?: string;

  rightSlot?: React.ReactNode;
}

export function GridToolbar({
  name,
  searchValue,
  onSearchChange,
  searchPlaceholder = "Search…",
  className,
  leftSlot,
  onNewClick,
  newLabel = "New",
  onImportClick,
  importLabel = "Import Excel",
  onExportClick,
  exportLabel = "Export Excel",
  rightSlot,
}: GridToolbarProps) {
  return (
    <div
      id={`container-gridToolbar-${name}`}
      className={cn("flex min-w-0 flex-col gap-3", className)}
    >
      <div className="flex min-w-0 flex-wrap items-center justify-between gap-3">
        <div
          id={`container-gridToolbarLeft-${name}`}
          className="min-w-0 flex-[1_1_16rem] sm:max-w-xs"
        >
          <Input
            id={`input-gridSearch-${name}`}
            name={`gridSearch-${name}`}
            aria-label={searchPlaceholder}
            className="w-full sm:max-w-xs"
            value={searchValue}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder={searchPlaceholder}
          />
        </div>

        <div
          id={`container-gridToolbarRight-${name}`}
          className="flex flex-wrap items-center justify-end gap-2"
        >
          {onImportClick ? (
            <Button
              id={`button-gridImport-${name}`}
              type="button"
              variant="outline"
              size="sm"
              onClick={onImportClick}
            >
              {importLabel}
            </Button>
          ) : null}
          {onExportClick ? (
            <Button
              id={`button-gridExport-${name}`}
              type="button"
              variant="outline"
              size="sm"
              onClick={onExportClick}
            >
              {exportLabel}
            </Button>
          ) : null}
          {onNewClick ? (
            <Button
              id={`button-gridNew-${name}`}
              type="button"
              size="sm"
              onClick={onNewClick}
            >
              {newLabel}
            </Button>
          ) : null}
          {rightSlot}
        </div>
      </div>
      {leftSlot}
    </div>
  );
}
