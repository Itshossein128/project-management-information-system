import * as React from "react";

import { cn } from "@/app/lib/utils";

type FieldIds = {
  containerId: string;
  labelId: string;
  helpId: string;
  errorId: string;
};

export type FieldProps = {
  name: string;
  label?: React.ReactNode;
  helpText?: React.ReactNode;
  error?: React.ReactNode;
  className?: string;
  /**
   * Defaults to `text-${name}InputLabel`, `text-${name}InputHelper`, `text-${name}InputError`.
   * Useful for checkbox/toggle where label semantics differ.
   */
  ids?: Partial<FieldIds>;
  /** Forwarded to the label `htmlFor` when provided. */
  htmlFor?: string;
  children: (ids: FieldIds) => React.ReactNode;
};

export function Field({
  name,
  label,
  helpText,
  error,
  className,
  ids,
  htmlFor,
  children,
}: FieldProps) {
  const resolvedIds: FieldIds = {
    containerId: ids?.containerId?.trim() || `container-${name}Field`,
    labelId: ids?.labelId?.trim() || `text-${name}InputLabel`,
    helpId: ids?.helpId?.trim() || `text-${name}InputHelper`,
    errorId: ids?.errorId?.trim() || `text-${name}InputError`,
  };

  return (
    <div id={resolvedIds.containerId} className={cn("grid gap-1.5", className)}>
      {label != null && (
        <label
          id={resolvedIds.labelId}
          htmlFor={htmlFor}
          className="text-sm font-medium leading-none"
        >
          {label}
        </label>
      )}

      {children(resolvedIds)}

      {helpText != null && (
        <div id={resolvedIds.helpId} className="text-xs text-muted-foreground">
          {helpText}
        </div>
      )}

      {error != null && (
        <div id={resolvedIds.errorId} className="text-xs text-destructive">
          {error}
        </div>
      )}
    </div>
  );
}

