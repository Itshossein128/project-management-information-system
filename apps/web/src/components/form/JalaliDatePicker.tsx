import { useTranslation } from "react-i18next";
import MultiDatePicker from "react-multi-date-picker";
import DateObject from "react-date-object";
import {
  dateObjectToIso,
  getDatePickerCalendarConfig,
  parseIsoToDateObject,
} from "@/app/lib/jalali-utils";
import { cn } from "@/app/lib/utils";
import { Field, type FieldProps } from "./Field";

/** Vite SSR may expose the CJS module namespace; unwrap to the real component. */
const DatePicker =
  (MultiDatePicker as unknown as { default?: typeof MultiDatePicker }).default ??
  MultiDatePicker;

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
 * Single-date input with locale-matched calendar UI.
 *
 * - When language is 'fa': displays Solar Hijri (Persian) calendar and digits.
 * - When language is 'en': displays Gregorian calendar and digits.
 * - Always emits and accepts ISO Gregorian (`YYYY-MM-DD`) strings via `value` / `onChange`.
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
  const { i18n } = useTranslation();
  const { calendar, locale, format } = getDatePickerCalendarConfig(i18n.language);

  const inputId = id?.trim() ? id.trim() : `input-${name}`;

  const parsedValue = parseIsoToDateObject(value, calendar, locale);
  const parsedMinDate = parseIsoToDateObject(minDate, calendar, locale);
  const parsedMaxDate = parseIsoToDateObject(maxDate, calendar, locale);

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
          value={parsedValue ?? ""}
          onChange={(date: DateObject | DateObject[] | null) => {
            const next = Array.isArray(date) ? date[0] ?? null : date ?? null;
            onChange(dateObjectToIso(next));
          }}
          calendar={calendar}
          locale={locale}
          format={format}
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
          minDate={parsedMinDate || undefined}
          maxDate={parsedMaxDate || undefined}
          editable={false}
        />
      )}
    </Field>
  );
}
