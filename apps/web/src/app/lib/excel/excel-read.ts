import * as XLSX from "xlsx";

export interface ExcelReadOptions {
  /** Sheet name; if omitted uses the first sheet. */
  sheetName?: string;
  /** If true, empty rows are skipped. Default: true */
  skipEmpty?: boolean;
}

export interface ExcelReadResult {
  sheetName: string;
  /** Headers as seen in file (row 1). */
  headers: string[];
  /** Raw row objects (keys are headers). */
  rows: Record<string, unknown>[];
}

function normalizeHeader(value: unknown): string {
  if (value == null) return "";
  if (typeof value === "string") return value.trim();
  return String(value).trim();
}

export async function readExcelFile(
  file: File,
  options: ExcelReadOptions = {},
): Promise<ExcelReadResult> {
  const buf = await file.arrayBuffer();
  const wb = XLSX.read(buf, { type: "array" });
  const sheetName = options.sheetName ?? wb.SheetNames[0] ?? "";
  if (!sheetName) {
    return { sheetName: "", headers: [], rows: [] };
  }
  const ws = wb.Sheets[sheetName];
  const raw = XLSX.utils.sheet_to_json<Record<string, unknown>>(ws, {
    defval: null,
    raw: false,
  });

  // Extract headers from first row of the sheet (more reliable than Object keys).
  const range = ws["!ref"] ? XLSX.utils.decode_range(ws["!ref"]) : null;
  const headers: string[] = [];
  if (range) {
    for (let c = range.s.c; c <= range.e.c; c++) {
      const addr = XLSX.utils.encode_cell({ r: 0, c });
      const cell = ws[addr];
      headers.push(normalizeHeader(cell?.v));
    }
  } else if (raw.length) {
    headers.push(...Object.keys(raw[0] ?? {}).map(normalizeHeader));
  }

  const skipEmpty = options.skipEmpty ?? true;
  const rows = skipEmpty
    ? raw.filter((r) => Object.values(r).some((v) => v != null && String(v).trim() !== ""))
    : raw;

  return { sheetName, headers: headers.filter(Boolean), rows };
}

