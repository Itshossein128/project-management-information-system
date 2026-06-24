/**
 * Form middleware: single import point for textarea.
 * Change the underlying UI component here without touching feature code.
 */
import * as React from "react";
import { cn } from "@/app/lib/utils";
import { Field, type FieldProps } from "./Field";

export type TextAreaProps = Omit<React.ComponentProps<"textarea">, "name"> & {
  name: string;
  label?: FieldProps["label"];
  helpText?: FieldProps["helpText"];
  error?: FieldProps["error"];
  fieldClassName?: string;
};

export function TextArea({
  name,
  id,
  label,
  helpText,
  error,
  fieldClassName,
  className,
  ...props
}: TextAreaProps) {
  const inputId = typeof id === "string" && id.trim() ? id.trim() : `input-${name}`;

  const helpId = `text-${name}InputHelper`;
  const errorId = `text-${name}InputError`;
  const describedBy = [helpText != null ? helpId : null, error != null ? errorId : null]
    .filter(Boolean)
    .join(" ");

  return (
    <Field name={name} label={label} helpText={helpText} error={error} htmlFor={inputId} className={fieldClassName}>
      {() => (
        <textarea
          id={inputId}
          name={name}
          data-slot='textarea'
          aria-invalid={error != null || undefined}
          aria-describedby={describedBy || undefined}
          className={cn(
            "placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground dark:bg-input/30 border-input min-h-24 w-full min-w-0 rounded-md border bg-transparent px-3 py-2 text-base shadow-xs transition-[color,box-shadow] outline-none disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
            "focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]",
            "aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
            className,
          )}
          {...props}
        />
      )}
    </Field>
  );
}

