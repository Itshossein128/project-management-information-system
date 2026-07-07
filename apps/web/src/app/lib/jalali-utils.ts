import DateObject from "react-date-object";
import gregorian from "react-date-object/calendars/gregorian";
import persian from "react-date-object/calendars/persian";
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
  if (!iso) return "—";
  const jalali = isoToJalali(iso.slice(0, 10));
  return jalali || iso.slice(0, 10);
}
