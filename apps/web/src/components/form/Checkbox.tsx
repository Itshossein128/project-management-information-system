/**
 * Form middleware: single import point for checkbox.
 * Change the underlying UI component here without touching feature code.
 */
import * as React from "react";
import { cn } from "@/app/lib/utils";
import { Field, type FieldProps } from "./Field";
import { Checkbox as ShadcnCheckbox } from "@/components/ui/checkbox";

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
      {() => {
        // We separate standard native onChange from standard Radix onChange.
        // Radix Checkbox takes an `onCheckedChange` and `checked`.
        // We need to bridge react-hook-form or traditional onChange to Radix.
        const { value, onChange, ...restProps } = props as any;

        return (
          <div className='flex items-center gap-2 group'>
            <ShadcnCheckbox
              id={inputId}
              name={name}
              aria-invalid={error != null || undefined}
              aria-describedby={describedBy || undefined}
              className={className}
              checked={
                props.checked !== undefined
                  ? props.checked
                  : (value === true || value === "true")
              }
              onCheckedChange={(checked) => {
                // If the user provided an onChange (like react-hook-form), call it
                // creating a fake event that mimics standard input.
                if (onChange) {
                  onChange({
                    target: { name, value: checked, checked, type: "checkbox" },
                  } as unknown as React.ChangeEvent<HTMLInputElement>);
                }
              }}
              disabled={props.disabled}
              required={props.required}
              {...restProps}
            />
            {label != null && (
              <label id={labelId} htmlFor={inputId} className='text-sm leading-none cursor-pointer group-hover:text-primary transition-colors'>
                {label}
              </label>
            )}
          </div>
        )
      }}
    </Field>
  );
}

