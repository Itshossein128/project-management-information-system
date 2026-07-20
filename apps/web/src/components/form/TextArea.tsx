/**
 * Form middleware: single import point for textarea.
 * Change the underlying UI component here without touching feature code.
 */
import * as React from "react";
import { cn } from "@/app/lib/utils";
import { Field, type FieldProps } from "./Field";
import { Textarea } from "@/components/ui/textarea";

export type TextAreaProps = Omit<React.ComponentProps<"textarea">, "name"> & {
  name: string;
  label?: FieldProps["label"];
  helpText?: FieldProps["helpText"];
  error?: FieldProps["error"];
  fieldClassName?: string;
  sticky?: FieldProps["sticky"];
  onStickyChange?: FieldProps["onStickyChange"];
  stickyAriaLabel?: FieldProps["stickyAriaLabel"];
};

export function TextArea({
  name,
  id,
  label,
  helpText,
  error,
  fieldClassName,
  sticky,
  onStickyChange,
  stickyAriaLabel,
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
    <Field
      name={name}
      label={label}
      helpText={helpText}
      error={error}
      htmlFor={inputId}
      className={fieldClassName}
      sticky={sticky}
      onStickyChange={onStickyChange}
      stickyAriaLabel={stickyAriaLabel}
    >
      {() => (
        <Textarea
          id={inputId}
          name={name}
          aria-invalid={error != null || undefined}
          aria-describedby={describedBy || undefined}
          className={cn("min-h-24", className)}
          {...props}
        />
      )}
    </Field>
  );
}

