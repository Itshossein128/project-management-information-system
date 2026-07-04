import * as XLSX from "xlsx";

// Function to manage downloadExcel
export function downloadExcel(args: {
  filename: string;
  sheetName?: string;
  headers: string[];
  rows: Record<string, unknown>[];
}) {
  // Variable holding ws
  const ws = XLSX.utils.json_to_sheet(args.rows, {
    header: args.headers,
    skipHeader: false,
  });
  // Variable holding wb
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, args.sheetName ?? "Sheet1");
  // Variable holding buf
  const buf = XLSX.write(wb, { type: "array", bookType: "xlsx" });
  // Variable holding blob
  const blob = new Blob([buf], {
    type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  });

  // Variable holding url
  const url = URL.createObjectURL(blob);
  // Variable holding a
  const a = document.createElement("a");
  a.href = url;
  a.download = args.filename.endsWith(".xlsx") ? args.filename : `${args.filename}.xlsx`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

