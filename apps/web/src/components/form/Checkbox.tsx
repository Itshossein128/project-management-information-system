/**
 * Form middleware: single import point for checkbox.
 * Change the underlying UI component here without touching feature code.
 */
import * as React from "react";
import { cn } from "@/app/lib/utils";
import { Field, type FieldProps } from "./Field";

export type CheckboxProps = Omit<React.ComponentProps<"input">, "type" | "name"> & {
  name: string;
  label?: FieldProps["label"];
  helpText?: FieldProps["helpText"];
  error?: FieldProps["error"];
  fieldClassName?: string;
};

export function Checkbox({
  name,
  id,
  label,
  helpText,
  error,
  fieldClassName,
  className,
  ...props
}: CheckboxProps) {
  const inputId = typeof id === "string" && id.trim() ? id.trim() : `checkbox-${name}`;

  const labelId = `text-${name}CheckboxLabel`;
  const helpId = `text-${name}InputHelper`;
  const errorId = `text-${name}InputError`;
  const describedBy = [helpText != null ? helpId : null, error != null ? errorId : null]
    .filter(Boolean)
    .join(" ");

  return (
    <Field
      name={name}
      label={undefined}
      helpText={helpText}
      error={error}
      className={fieldClassName}
      ids={{ labelId }}
    >
      {() => (
        <div className='flex items-center gap-2'>
          <input
            id={inputId}
            name={name}
            type='checkbox'
            aria-invalid={error != null || undefined}
            aria-describedby={describedBy || undefined}
            className={cn(
              "border-input text-primary focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] dark:bg-input/30 h-4 w-4 rounded border bg-transparent shadow-xs outline-none disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50",
              className,
            )}
            {...props}
          />
          {label != null && (
            <label id={labelId} htmlFor={inputId} className='text-sm leading-none'>
              {label}
            </label>
          )}
        </div>
      )}
    </Field>
  );
}

