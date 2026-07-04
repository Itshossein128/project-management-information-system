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

// Function to manage GridToolbar
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
      className={cn(
        "flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between",
        className,
      )}
    >
      <div
        id={`container-gridToolbarLeft-${name}`}
        className="flex flex-col gap-2 sm:flex-row sm:items-center"
      >
        <Input
          id={`input-gridSearch-${name}`}
          name={`gridSearch-${name}`}
          className="w-full sm:max-w-xs"
          value={searchValue}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder={searchPlaceholder}
        />
        {leftSlot}
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
  );
}
