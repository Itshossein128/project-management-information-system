import { cn } from "@/app/lib/utils";
import DatePicker from "react-multi-date-picker";
import type { DateObject } from "react-multi-date-picker";
import persian from "react-date-object/calendars/persian";
import persian_fa from "react-date-object/locales/persian_fa";
import { Field, type FieldProps } from "./Field";

const ISO_DATE_FORMAT = "YYYY-MM-DD";

function dateObjectToIso(value: DateObject | null | undefined): string {
  if (!value) return "";
  const g = value.convert(undefined as unknown as any);
  return g.format(ISO_DATE_FORMAT);
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
 * Date range input with a Jalali calendar.
 *
 * - User sees Persian dates and Persian digits.
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
  const inputId = id?.trim() ? id.trim() : `input-${name}`;

  const valueArr: string[] = [value.from || "", value.to || ""].filter(Boolean);

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
          dateSeparator=" تا "
          value={valueArr}
          onChange={(dates) => {
            const arr = Array.isArray(dates) ? (dates as DateObject[]) : [];
            onChange({
              from: dateObjectToIso(arr[0]),
              to: dateObjectToIso(arr[1]),
            });
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
          editable={false}
        />
      )}
    </Field>
  );
}
