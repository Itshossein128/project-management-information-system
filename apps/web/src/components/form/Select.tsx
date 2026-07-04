/**
 * Form middleware: single import point for select.
 * Change the underlying UI component here without touching feature code.
 */
import * as React from "react";
import { cn } from "@/app/lib/utils";
import { Field, type FieldProps } from "./Field";

export type SelectOption = {
  value: string;
  label: string;
  disabled?: boolean;
};

export type SelectProps = Omit<React.ComponentProps<"select">, "name" | "children"> & {
  name: string;
  label?: FieldProps["label"];
  helpText?: FieldProps["helpText"];
  error?: FieldProps["error"];
  fieldClassName?: string;
  options: SelectOption[];
  placeholder?: string;
};

// Function to manage Select
export function Select({
  name,
  id,
  label,
  helpText,
  error,
  fieldClassName,
  className,
  options,
  placeholder,
  ...props
}: SelectProps) {
  // Variable holding selectId
  const selectId = typeof id === "string" && id.trim() ? id.trim() : `select-${name}`;

  // Variable holding helpId
  const helpId = `text-${name}InputHelper`;
  // Variable holding errorId
  const errorId = `text-${name}InputError`;
  // Variable holding describedBy
  const describedBy = [helpText != null ? helpId : null, error != null ? errorId : null]
    .filter(Boolean)
    .join(" ");

  return (
    <Field name={name} label={label} helpText={helpText} error={error} htmlFor={selectId} className={fieldClassName}>
      {() => (
        <select
          id={selectId}
          name={name}
          data-slot='select'
          aria-invalid={error != null || undefined}
          aria-describedby={describedBy || undefined}
          className={cn(
            "border-input bg-transparent dark:bg-input/30 h-9 w-full rounded-md border px-3 text-base shadow-xs outline-none transition-[color,box-shadow] disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
            "focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]",
            "aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
            className,
          )}
          {...props}
        >
          {placeholder != null && (
            <option id={`text-${name}SelectPlaceholder`} value='' disabled>
              {placeholder}
            </option>
          )}
          {options.map((opt) => (
            <option key={opt.value} value={opt.value} disabled={opt.disabled}>
              {opt.label}
            </option>
          ))}
        </select>
      )}
    </Field>
  );
}

