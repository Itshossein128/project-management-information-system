import { useTranslation } from "react-i18next";
import MultiDatePicker, { DateObject } from "react-multi-date-picker";
import gregorian from "react-date-object/calendars/gregorian";
import persian from "react-date-object/calendars/persian";
import gregorian_en from "react-date-object/locales/gregorian_en";
import persian_fa from "react-date-object/locales/persian_fa";
import { cn } from "@/app/lib/utils";
import { Field, type FieldProps } from "./Field";

/** Vite SSR may expose the CJS module namespace; unwrap to the real component. */
const DatePicker =
  (MultiDatePicker as unknown as { default?: typeof MultiDatePicker }).default ??
  MultiDatePicker;

/**
 * Parses an ISO Gregorian string (`YYYY-MM-DD`) into a `DateObject` converted to
 * the active calendar and locale for display.
 */
function parseIsoToDateObject(
  iso: string | undefined | null,
  calendar: any,
  locale: any,
): DateObject | "" {
  if (!iso) return "";
  const parts = iso.slice(0, 10).split("-").map(Number);
  if (parts.length !== 3 || parts.some(Number.isNaN)) return "";
  const [year, month, day] = parts;
  const d = new DateObject({ year, month, day, calendar: gregorian });
  return d.convert(calendar, locale);
}

/**
 * Converts a `DateObject` (which could be in Solar Hijri or Gregorian calendar)
 * back to an ISO `YYYY-MM-DD` Gregorian date string for wire/API storage.
 */
function dateObjectToIso(value: DateObject | null): string {
  if (!value) return "";
  const g = value.convert(gregorian, gregorian_en);
  const year = g.year;
  const month = String(g.month.number).padStart(2, "0");
  const day = String(g.day).padStart(2, "0");
  return `${year}-${month}-${day}`;
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
  const isFa = i18n.language === "fa";
  const activeCalendar = isFa ? persian : gregorian;
  const activeLocale = isFa ? persian_fa : gregorian_en;
  const format = isFa ? "YYYY/MM/DD" : "YYYY-MM-DD";

  const inputId = id?.trim() ? id.trim() : `input-${name}`;

  const parsedValue = parseIsoToDateObject(value, activeCalendar, activeLocale);
  const parsedMinDate = parseIsoToDateObject(minDate, activeCalendar, activeLocale);
  const parsedMaxDate = parseIsoToDateObject(maxDate, activeCalendar, activeLocale);

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
          value={parsedValue}
          onChange={(date) => {
            const next = Array.isArray(date) ? date[0] ?? null : date ?? null;
            onChange(dateObjectToIso(next as DateObject | null));
          }}
          calendar={activeCalendar}
          locale={activeLocale}
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
