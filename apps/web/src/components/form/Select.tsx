/**
 * Form middleware: single import point for select.
 * Change the underlying UI component here without touching feature code.
 */
import * as React from "react";
import { cn } from "@/app/lib/utils";
import { Field, type FieldProps } from "./Field";
import {
  Select as ShadcnSelect,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useTranslation } from "react-i18next";

export type SelectOption = {
  value: string;
  label: string;
  disabled?: boolean;
};

export type SelectProps = Omit<React.ComponentProps<"select">, "name" | "children" | "value" | "onChange" | "dir"> & {
  name: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  label?: FieldProps["label"];
  helpText?: FieldProps["helpText"];
  error?: FieldProps["error"];
  fieldClassName?: string;
  options: SelectOption[];
  placeholder?: string;
};

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
  value,
  onChange,
  disabled,
  ...props
}: SelectProps) {
  const selectId = typeof id === "string" && id.trim() ? id.trim() : `select-${name}`;

  const helpId = `text-${name}InputHelper`;
  const errorId = `text-${name}InputError`;
  const describedBy = [helpText != null ? helpId : null, error != null ? errorId : null]
    .filter(Boolean)
    .join(" ");

  const { i18n } = useTranslation();
  const dir = i18n.dir();

  // Extract events and aria props that are safe for buttons
  const { "aria-label": ariaLabel, "aria-labelledby": ariaLabelledby, style, onBlur, onFocus } = props;

  return (
    <Field name={name} label={label} helpText={helpText} error={error} htmlFor={selectId} className={fieldClassName}>
      {() => (
        <ShadcnSelect
          name={name}
          value={value}
          onValueChange={(newVal) => {
            if (onChange) {
              onChange({
                target: { name, value: newVal },
                currentTarget: { name, value: newVal },
              } as React.ChangeEvent<HTMLSelectElement>);
            }
          }}
          disabled={disabled}
          dir={dir}
        >
          <SelectTrigger
            id={selectId}
            className={cn("w-full", className)}
            aria-invalid={error != null || undefined}
            aria-describedby={describedBy || undefined}
            aria-label={ariaLabel}
            aria-labelledby={ariaLabelledby}
            style={style}
            onBlur={onBlur as unknown as React.FocusEventHandler<HTMLButtonElement>}
            onFocus={onFocus as unknown as React.FocusEventHandler<HTMLButtonElement>}
          >
            <SelectValue placeholder={placeholder} />
          </SelectTrigger>
          <SelectContent>
            {options.map((opt) => (
              <SelectItem key={opt.value} value={opt.value} disabled={opt.disabled}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </ShadcnSelect>
      )}
    </Field>
  );
}
