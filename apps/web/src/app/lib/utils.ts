import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

function normalizeDigits(value: string): string {
  return value
    .replace(/[۰-۹]/g, (d) => String("۰۱۲۳۴۵۶۷۸۹".indexOf(d)))
    .replace(/[٠-٩]/g, (d) => String("٠١٢٣٤٥٦٧٨٩".indexOf(d)));
}

/** Keep a raw numeric string in form state (no grouping commas). */
export function toRawNumericString(input: string): string {
  const str = normalizeDigits(input).replace(/,/g, "").trim();
  if (!str || str === "-" || str === "." || str === "-.") return str === "-" ? "-" : "";
  const sign = str.startsWith("-") ? "-" : "";
  const unsigned = sign ? str.slice(1) : str;
  const [intPart = "", ...rest] = unsigned.split(".");
  const safeInt = intPart.replace(/[^\d]/g, "");
  const safeFrac = rest.join("").replace(/[^\d]/g, "");
  if (!safeInt && !safeFrac) return sign || "";
  return rest.length > 0 ? `${sign}${safeInt}.${safeFrac}` : `${sign}${safeInt}`;
}

export function formatWithCommas(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") return "";
  const str = normalizeDigits(String(value));
  const parts = str.split(".");
  const rawInt = parts[0].replace(/[^\d-]/g, "");
  if (!rawInt && parts.length === 1 && str.includes("-")) return "-";
  if (!rawInt && parts.length === 1) return "";
  const formattedInt = rawInt.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return parts.length > 1 ? `${formattedInt}.${parts[1].replace(/[^\d]/g, "")}` : formattedInt;
}

export function parseFormattedNumber(input: string | number | null | undefined): number {
  if (input === null || input === undefined || input === "") return 0;
  const str = toRawNumericString(String(input));
  const n = Number(str);
  return Number.isFinite(n) ? n : 0;
}
