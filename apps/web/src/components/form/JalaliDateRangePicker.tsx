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

const DatePicker =
  (MultiDatePicker as unknown as { default?: typeof MultiDatePicker }).default ??
  MultiDatePicker;

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
  const { i18n } = useTranslation();
  const { isFa, calendar, locale, format } = getDatePickerCalendarConfig(i18n.language);
  const dateSeparator = isFa ? " تا " : " to ";

  const inputId = id?.trim() ? id.trim() : `input-${name}`;

  const parsedFrom = parseIsoToDateObject(value.from, calendar, locale);
  const parsedTo = parseIsoToDateObject(value.to, calendar, locale);

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
          onChange={(dates: DateObject | DateObject[] | null) => {
            const arr = Array.isArray(dates) ? dates : [];
            onChange({
              from: dateObjectToIso(arr[0]),
              to: dateObjectToIso(arr[1]),
            });
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
          editable={false}
        />
      )}
    </Field>
  );
}
