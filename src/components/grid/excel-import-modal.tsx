import { useMemo, useState } from "react";
import { z } from "zod";

import { Button, Card, CardContent, CardHeader, CardTitle } from "@/components/form";
import { readExcelFile } from "@/app/lib/excel/excel-read";
import {
  type ExcelColumnMapping,
  type ExcelValidationResult,
  validateExcelRows,
} from "@/app/lib/excel/excel-validate";
import { downloadExcel } from "@/app/lib/excel/excel-write";

export interface ExcelImportModalProps<T extends Record<string, unknown>> {
  name: string;
  title: string;
  open: boolean;
  onClose: () => void;
  mapping: ExcelColumnMapping<T>;
  schema: z.ZodType<T>;
  onSubmitValidRows: (rows: T[], file: File) => Promise<void> | void;
}

export function ExcelImportModal<T extends Record<string, unknown>>({
  name,
  title,
  open,
  onClose,
  mapping,
  schema,
  onSubmitValidRows,
}: ExcelImportModalProps<T>) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ExcelValidationResult<T> | null>(null);

  const invalidCount = result?.invalidRows.length ?? 0;
  const validCount = result?.validRows.length ?? 0;

  const errorRowsForExport = useMemo(() => {
    if (!result) return [];
    return result.invalidRows.map((r) => ({
      excelRow: r.excelRow,
      errors: r.errors.map((e) => `${e.field ?? "row"}: ${e.message}`).join(" | "),
      ...r.raw,
    }));
  }, [result]);

  if (!open) return null;

  return (
    <div
      id={`modal-excelImport-${name}`}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      role="dialog"
      aria-modal="true"
    >
      <Card id={`container-excelImportCard-${name}`} className="w-full max-w-3xl">
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle id={`text-excelImportTitle-${name}`}>{title}</CardTitle>
          <Button
            id={`button-closeExcelImport-${name}`}
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => {
              if (loading) return;
              onClose();
            }}
          >
            Close
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          <div id={`container-excelImportFile-${name}`} className="space-y-2">
            <label id={`text-excelImportFileLabel-${name}`} className="text-sm font-medium">
              Excel file (.xlsx)
            </label>
            <input
              id={`input-excelFile-${name}`}
              type="file"
              accept=".xlsx"
              onChange={async (e) => {
                setError(null);
                setResult(null);
                const f = e.target.files?.[0] ?? null;
                setFile(f);
                if (!f) return;
                setLoading(true);
                try {
                  const parsed = await readExcelFile(f);
                  const validated = validateExcelRows<T>({
                    rows: parsed.rows,
                    mapping,
                    schema,
                    firstDataRowNumber: 2,
                  });
                  setResult(validated);
                } catch (err) {
                  setError(err instanceof Error ? err.message : "Failed to read Excel file.");
                } finally {
                  setLoading(false);
                }
              }}
            />
            {loading ? (
              <p id={`text-excelImportLoading-${name}`} className="text-muted-foreground text-sm">
                Reading and validating…
              </p>
            ) : null}
            {error ? (
              <p id={`text-excelImportError-${name}`} className="text-destructive text-sm">
                {error}
              </p>
            ) : null}
          </div>

          {result ? (
            <div id={`container-excelImportSummary-${name}`} className="rounded-md border p-3">
              <p id={`text-excelImportSummary-${name}`} className="text-sm">
                Total rows: <span id={`text-excelImportTotal-${name}`}>{result.totalRows}</span> — Valid:{" "}
                <span id={`text-excelImportValid-${name}`}>{validCount}</span> — Invalid:{" "}
                <span id={`text-excelImportInvalid-${name}`}>{invalidCount}</span>
              </p>

              {invalidCount > 0 ? (
                <div id={`container-excelImportInvalidList-${name}`} className="mt-3 space-y-2">
                  <div className="flex flex-wrap gap-2">
                    <Button
                      id={`button-exportExcelImportErrors-${name}`}
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        downloadExcel({
                          filename: `${name}-import-errors.xlsx`,
                          sheetName: "Errors",
                          headers: Object.keys(errorRowsForExport[0] ?? { excelRow: "", errors: "" }),
                          rows: errorRowsForExport,
                        });
                      }}
                    >
                      Export error report
                    </Button>
                  </div>

                  <div className="max-h-56 overflow-auto rounded border p-2">
                    {result.invalidRows.slice(0, 50).map((r, idx) => (
                      <div
                        key={`${r.excelRow}-${idx}`}
                        id={`item-excelImportInvalidRow-${name}-${idx}`}
                        className="border-b py-2 last:border-b-0"
                      >
                        <p
                          id={`text-excelImportInvalidRowTitle-${name}-${idx}`}
                          className="text-sm font-medium"
                        >
                          Row {r.excelRow}
                        </p>
                        <ul
                          id={`list-excelImportInvalidRowErrors-${name}-${idx}`}
                          className="list-disc pl-5 text-sm text-destructive"
                        >
                          {r.errors.map((e, eidx) => (
                            <li
                              key={`${eidx}-${e.message}`}
                              id={`text-excelImportInvalidRowError-${name}-${idx}-${eidx}`}
                            >
                              {e.field ? `${e.field}: ` : ""}{e.message}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                    {result.invalidRows.length > 50 ? (
                      <p
                        id={`text-excelImportInvalidMore-${name}`}
                        className="pt-2 text-muted-foreground text-sm"
                      >
                        Showing first 50 invalid rows. Export the report for all errors.
                      </p>
                    ) : null}
                  </div>
                </div>
              ) : null}
            </div>
          ) : null}

          <div id={`container-excelImportActions-${name}`} className="flex items-center justify-end gap-2">
            <Button
              id={`button-cancelExcelImport-${name}`}
              type="button"
              variant="outline"
              onClick={() => {
                if (loading) return;
                onClose();
              }}
            >
              Cancel
            </Button>
            <Button
              id={`button-submitExcelImport-${name}`}
              type="button"
              disabled={!file || !result || invalidCount > 0 || validCount === 0 || loading}
              onClick={async () => {
                if (!file || !result) return;
                setError(null);
                setLoading(true);
                try {
                  await onSubmitValidRows(result.validRows, file);
                  onClose();
                } catch (err) {
                  setError(err instanceof Error ? err.message : "Import failed.");
                } finally {
                  setLoading(false);
                }
              }}
            >
              Import {validCount ? `(${validCount})` : ""}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

