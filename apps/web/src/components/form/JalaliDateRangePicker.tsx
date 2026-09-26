import { useTranslation } from "react-i18next";
import MultiDatePicker, { DateObject } from "react-multi-date-picker";
import gregorian from "react-date-object/calendars/gregorian";
import persian from "react-date-object/calendars/persian";
import gregorian_en from "react-date-object/locales/gregorian_en";
import persian_fa from "react-date-object/locales/persian_fa";
import { cn } from "@/app/lib/utils";
import { Field, type FieldProps } from "./Field";

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
): DateObject | null {
  if (!iso) return null;
  const parts = iso.slice(0, 10).split("-").map(Number);
  if (parts.length !== 3 || parts.some(Number.isNaN)) return null;
  const [year, month, day] = parts;
  const d = new DateObject({ year, month, day, calendar: gregorian });
  return d.convert(calendar, locale);
}

/**
 * Converts a `DateObject` back to an ISO `YYYY-MM-DD` Gregorian date string.
 */
function dateObjectToIso(value: DateObject | null | undefined): string {
  if (!value) return "";
  const g = value.convert(gregorian, gregorian_en);
  const year = g.year;
  const month = String(g.month.number).padStart(2, "0");
  const day = String(g.day).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export interface DateRangeValue {
  /** ISO `YYYY-MM-DD` Gregorian, or "" when not set. */
  from: string;
  to: string;
}

export interface JalaliDateRangePickerProps {
  name: string;
  value: DateRangeValue;
  onChange: (next: DateRangeValue) => void;
  label?: FieldProps["label"];
  helpText?: FieldProps["helpText"];
  error?: FieldProps["error"];
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  fieldClassName?: string;
  id?: string;
}

/**
 * Date range input with locale-matched calendar.
 *
 * - When language is 'fa': displays Solar Hijri (Persian) calendar.
 * - When language is 'en': displays Gregorian calendar.
 * - Emits two ISO Gregorian `YYYY-MM-DD` strings (`from`, `to`).
 * - Both ends may be empty (then the filter is treated as "no bound on that side").
 */
export function JalaliDateRangePicker({
  name,
  value,
  onChange,
  label,
  helpText,
  error,
  placeholder,
  disabled,
  className,
  fieldClassName,
  id,
}: JalaliDateRangePickerProps) {
  const { i18n, t } = useTranslation();
  const isFa = i18n.language === "fa";
  const activeCalendar = isFa ? persian : gregorian;
  const activeLocale = isFa ? persian_fa : gregorian_en;
  const format = isFa ? "YYYY/MM/DD" : "YYYY-MM-DD";
  const dateSeparator = isFa ? " تا " : " to ";

  const inputId = id?.trim() ? id.trim() : `input-${name}`;

  const parsedFrom = parseIsoToDateObject(value.from, activeCalendar, activeLocale);
  const parsedTo = parseIsoToDateObject(value.to, activeCalendar, activeLocale);

  const valueArr: DateObject[] = [parsedFrom, parsedTo].filter(
    (item): item is DateObject => item !== null,
  );

  return (
    <Field
      name={name}
      label={label}
      helpText={helpText}
      error={error}
      htmlFor={inputId}
      className={fieldClassName}
    >
      {() => (
        <DatePicker
          id={inputId}
          name={name}
          range
          dateSeparator={dateSeparator}
          value={valueArr}
          onChange={(dates) => {
            const arr = Array.isArray(dates) ? (dates as DateObject[]) : [];
            onChange({
              from: dateObjectToIso(arr[0]),
              to: dateObjectToIso(arr[1]),
            });
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
          editable={false}
        />
      )}
    </Field>
  );
}
