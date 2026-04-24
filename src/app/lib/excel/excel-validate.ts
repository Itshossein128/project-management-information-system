import { z } from "zod";

export interface ExcelRowError {
  /** 1-based Excel row number (includes header row). */
  excelRow: number;
  /** Field key (our internal key), if available. */
  field?: string;
  /** Original header name, if available. */
  header?: string;
  /** Human message, ready for i18n. */
  message: string;
}

export interface ExcelValidationResult<T> {
  validRows: T[];
  invalidRows: { excelRow: number; raw: Record<string, unknown>; errors: ExcelRowError[] }[];
  totalRows: number;
}

export type ExcelColumnMapping<T> = Record<keyof T & string, string[]>;

export interface ExcelCoerceOptions {
  trimStrings?: boolean;
}

function pickFirstHeaderValue(
  raw: Record<string, unknown>,
  headers: string[],
): unknown {
  for (const h of headers) {
    if (h in raw) return raw[h];
    // fallback: case-insensitive match
    const found = Object.keys(raw).find((k) => k.trim().toLowerCase() === h.trim().toLowerCase());
    if (found) return raw[found];
  }
  return undefined;
}

export function mapExcelRow<T extends Record<string, unknown>>(
  raw: Record<string, unknown>,
  mapping: ExcelColumnMapping<T>,
  options: ExcelCoerceOptions = {},
): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const key of Object.keys(mapping)) {
    const value = pickFirstHeaderValue(raw, mapping[key as keyof T & string] ?? []);
    if (options.trimStrings !== false && typeof value === "string") out[key] = value.trim();
    else out[key] = value;
  }
  return out;
}

export function validateExcelRows<T extends Record<string, unknown>>(args: {
  /** Parsed rows from `readExcelFile` (each row keyed by Excel header text). */
  rows: Record<string, unknown>[];
  /** Maps internal keys → accepted header names. */
  mapping: ExcelColumnMapping<T>;
  /** Zod schema for the mapped row object. */
  schema: z.ZodType<T>;
  /** Excel row number offset. Default: 2 (row1 header, row2 first data). */
  firstDataRowNumber?: number;
}): ExcelValidationResult<T> {
  const firstDataRowNumber = args.firstDataRowNumber ?? 2;

  const validRows: T[] = [];
  const invalidRows: ExcelValidationResult<T>["invalidRows"] = [];

  args.rows.forEach((raw, idx) => {
    const excelRow = firstDataRowNumber + idx;
    const mapped = mapExcelRow<T>(raw, args.mapping);
    const parsed = args.schema.safeParse(mapped);

    if (parsed.success) {
      validRows.push(parsed.data);
      return;
    }

    const errors: ExcelRowError[] = parsed.error.issues.map((issue) => ({
      excelRow,
      field: issue.path?.[0] ? String(issue.path[0]) : undefined,
      message: issue.message,
    }));
    invalidRows.push({ excelRow, raw, errors });
  });

  return {
    validRows,
    invalidRows,
    totalRows: args.rows.length,
  };
}

