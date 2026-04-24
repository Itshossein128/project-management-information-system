import * as XLSX from "xlsx";

export function downloadExcel(args: {
  filename: string;
  sheetName?: string;
  headers: string[];
  rows: Record<string, unknown>[];
}) {
  const ws = XLSX.utils.json_to_sheet(args.rows, {
    header: args.headers,
    skipHeader: false,
  });
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, args.sheetName ?? "Sheet1");
  const buf = XLSX.write(wb, { type: "array", bookType: "xlsx" });
  const blob = new Blob([buf], {
    type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  });

  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = args.filename.endsWith(".xlsx") ? args.filename : `${args.filename}.xlsx`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

