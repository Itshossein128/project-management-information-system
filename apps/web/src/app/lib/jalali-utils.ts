import DateObject from "react-date-object";
import gregorian from "react-date-object/calendars/gregorian";
import persian from "react-date-object/calendars/persian";
import gregorian_en from "react-date-object/locales/gregorian_en";
import persian_fa from "react-date-object/locales/persian_fa";

/** True when i18n language is Persian (`fa`, `fa-IR`, …). */
export function isPersianLanguage(lang: string | undefined | null): boolean {
  return (lang ?? "").toLowerCase().startsWith("fa");
}

/** Calendar / locale / input format for date pickers, matched to UI language. */
export function getDatePickerCalendarConfig(lang: string | undefined | null) {
  const isFa = isPersianLanguage(lang);
  return {
    isFa,
    calendar: isFa ? persian : gregorian,
    locale: isFa ? persian_fa : gregorian_en,
    format: isFa ? "YYYY/MM/DD" : "YYYY-MM-DD",
  } as const;
}

/**
 * Parse an ISO Gregorian string (`YYYY-MM-DD`) into a `DateObject` on the
 * target calendar/locale for picker display.
 */
export function parseIsoToDateObject(
  iso: string | undefined | null,
  calendar: typeof gregorian | typeof persian,
  locale: typeof gregorian_en | typeof persian_fa,
): DateObject | null {
  if (!iso) return null;
  const parts = iso.slice(0, 10).split("-").map(Number);
  if (parts.length !== 3 || parts.some(Number.isNaN)) return null;
  const [year, month, day] = parts;
  return new DateObject({
    year,
    month,
    day,
    calendar: gregorian,
    locale: gregorian_en,
  }).convert(calendar, locale);
}

/**
 * Convert a picker `DateObject` to ISO Gregorian `YYYY-MM-DD`.
 *
 * Rebuilds from Y/M/D before converting. `DateObject.convert()` mutates in
 * place — mutating the picker's instance leaves Gregorian Y/M/D under a Persian
 * calendar (e.g. day 25 of آذر year 2026) and shows a Gregorian input value.
 */
export function dateObjectToIso(value: DateObject | null | undefined): string {
  if (!value) return "";
  const copy = new DateObject({
    year: value.year,
    month: value.month.number,
    day: value.day,
    hour: value.hour,
    minute: value.minute,
    second: value.second,
    millisecond: value.millisecond,
    calendar: value.calendar,
    locale: gregorian_en,
  });
  return copy.convert(gregorian, gregorian_en).format("YYYY-MM-DD");
}

export function jalaliToIso(jalali: string): string {
  if (!jalali) return "";
  const parts = jalali.split("/").map(Number);
  if (parts.length !== 3 || parts.some(Number.isNaN)) return "";
  const [year, month, day] = parts;
  return new DateObject({ year, month, day, calendar: persian })
    .convert(gregorian)
    .format("YYYY-MM-DD");
}

/** Convert ISO Gregorian to Jalali ``YYYY/MM/DD`` for API payloads. */
export function isoToJalali(iso: string): string {
  if (!iso) return "";
  const parts = iso.split("-").map(Number);
  if (parts.length !== 3 || parts.some(Number.isNaN)) return "";
  const [year, month, day] = parts;
  return new DateObject({ year, month, day, calendar: gregorian })
    .convert(persian)
    .format("YYYY/MM/DD");
}

/** Convert ISO Gregorian filter bounds to Jalali for API query params. */
export function isoRangeToJalali(from: string, to: string): { date_from?: string; date_to?: string } {
  const params: { date_from?: string; date_to?: string } = {};
  if (from) params.date_from = isoToJalali(from);
  if (to) params.date_to = isoToJalali(to);
  return params;
}

/** Format ISO date for display; returns Jalali when parsable, otherwise em dash. */
export function formatDisplayDate(iso: string | null | undefined): string {
  if (!iso || iso.startsWith("Invalid")) return "—";
  const jalali = isoToJalali(iso.slice(0, 10));
  return jalali || (iso.slice(0, 10) === "Invalid Da" ? "—" : iso.slice(0, 10));
}

/** Format an ISO datetime as Jalali date + HH:MM (local wall-clock from the string). */
export function formatDisplayDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  const date = formatDisplayDate(iso.slice(0, 10));
  const time = iso.slice(11, 16);
  return time ? `${date} ${time}` : date;
}
