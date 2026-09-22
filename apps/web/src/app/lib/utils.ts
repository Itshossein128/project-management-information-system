import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatWithCommas(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") return "";
  const str = String(value)
    .replace(/[۰-۹]/g, (d) => String("۰۱۲۳۴۵۶۷۸۹".indexOf(d)))
    .replace(/[٠-٩]/g, (d) => String("٠١٢٣٤٥٦٧٨٩".indexOf(d)));
  const parts = str.split(".");
  const rawInt = parts[0].replace(/[^\d-]/g, "");
  if (!rawInt && parts.length === 1 && str.includes("-")) return "-";
  if (!rawInt && parts.length === 1) return "";
  const formattedInt = rawInt.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return parts.length > 1 ? `${formattedInt}.${parts[1]}` : formattedInt;
}

export function parseFormattedNumber(input: string | number | null | undefined): number {
  if (input === null || input === undefined || input === "") return 0;
  const str = String(input)
    .replace(/[۰-۹]/g, (d) => String("۰۱۲۳۴۵۶۷۸۹".indexOf(d)))
    .replace(/[٠-٩]/g, (d) => String("٠١٢٣٥٦٧٨٩".indexOf(d)))
    .replace(/,/g, "")
    .trim();
  const n = Number(str);
  return Number.isFinite(n) ? n : 0;
}
