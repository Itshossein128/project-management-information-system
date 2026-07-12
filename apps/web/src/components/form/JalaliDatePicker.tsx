import { cn } from "@/app/lib/utils";
import DatePicker from "react-multi-date-picker";
import type { DateObject } from "react-multi-date-picker";
import persian from "react-date-object/calendars/persian";
import persian_fa from "react-date-object/locales/persian_fa";
import { Field, type FieldProps } from "./Field";

const ISO_DATE_FORMAT = "YYYY-MM-DD";

/**
 * `react-multi-date-picker` returns a `DateObject` (or null) that we serialize
 * to an ISO `YYYY-MM-DD` string for storage / API transport. The Jalali
 * calendar is for display only — the wire format stays Gregorian/ISO.
 */
function dateObjectToIso(value: DateObject | null): string {
  if (!value) return "";
  // `react-date-object` defaults to Gregorian when no calendar is provided.
  // Type defs require a calendar argument, so we pass `undefined` to preserve
  // the runtime default behavior while keeping SSR-friendly imports.
  const g = value.convert(undefined as unknown as any);
  return g.format(ISO_DATE_FORMAT);
}

export interface JalaliDatePickerProps {
  name: string;
  /** ISO `YYYY-MM-DD` (Gregorian). Empty string means "no date selected". */
  value: string;
  onChange: (isoDate: string) => void;
  label?: FieldProps["label"];
  helpText?: FieldProps["helpText"];
  error?: FieldProps["error"];
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  className?: string;
  fieldClassName?: string;
  id?: string;
  /** Optional ISO bounds (Gregorian). */
  minDate?: string;
  maxDate?: string;
  sticky?: FieldProps["sticky"];
  onStickyChange?: FieldProps["onStickyChange"];
  stickyAriaLabel?: FieldProps["stickyAriaLabel"];
}

/**
 * Single-date input with a Jalali (Persian) calendar UI.
 *
 * - User sees Persian dates and Persian digits.
 * - The component emits ISO Gregorian (`YYYY-MM-DD`) strings via `onChange`,
 *   which is what the Django backend (`DateField`) expects.
 */
export function JalaliDatePicker({
  name,
  value,
  onChange,
  label,
  helpText,
  error,
  placeholder,
  disabled,
  required,
  className,
  fieldClassName,
  id,
  minDate,
  maxDate,
  sticky,
  onStickyChange,
  stickyAriaLabel,
}: JalaliDatePickerProps) {
  const inputId = id?.trim() ? id.trim() : `input-${name}`;

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
        <DatePicker
          id={inputId}
          name={name}
          value={value || ""}
          onChange={(date) => {
            const next = Array.isArray(date) ? date[0] ?? null : date ?? null;
            onChange(dateObjectToIso(next as DateObject | null));
          }}
          calendar={persian}
          locale={persian_fa}
          format={ISO_DATE_FORMAT}
          calendarPosition="bottom-right"
          inputClass={cn(
            "border-input bg-transparent dark:bg-input/30 h-9 w-full rounded-md border px-3 text-base shadow-xs outline-none transition-[color,box-shadow] disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
            "focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]",
            "aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
            className,
          )}
          containerClassName="w-full"
          placeholder={placeholder}
          disabled={disabled}
          required={required}
          minDate={minDate}
          maxDate={maxDate}
          editable={false}
        />
      )}
    </Field>
  );
}
