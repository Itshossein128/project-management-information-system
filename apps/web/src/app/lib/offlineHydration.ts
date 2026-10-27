import type { LocalReportSnapshot } from "./offlineDB";

function fieldErrorFor(snapshot: LocalReportSnapshot, row: object) {
  const record = row as { client_id?: unknown; id?: unknown };
  const clientId = String(record.client_id ?? record.id ?? "");
  const fields = snapshot.field_errors?.[clientId];
  if (!fields) return {};
  const [field, code] = Object.entries(fields)[0] ?? [];
  if (!field || !code) return {};
  return { field_error: { field, code } };
}

export interface ReconciledReportData<THeader = Record<string, unknown>, TRow = Record<string, unknown>> {
  header: THeader;
  rows: TRow[];
}

export function reconcileServerWithLocalSnapshot<
  THeader extends Record<string, unknown> = Record<string, unknown>,
  TRow extends object = Record<string, unknown>,
>(
  serverHeader: THeader,
  serverRows: TRow[] = [],
  snapshot: LocalReportSnapshot | null | undefined,
  sectionKey?: string,
): ReconciledReportData<THeader, TRow> {
  const mergedHeader: THeader = {
    ...serverHeader,
    ...(snapshot?.overlay_header as Partial<THeader> | undefined),
  };

  if (!sectionKey || !snapshot) {
    const rowsWithStatus = (serverRows || []).map((row) => ({
      ...row,
      sync_status: (row as any).sync_status ?? "synced",
    }));
    return { header: mergedHeader, rows: rowsWithStatus as TRow[] };
  }

  const tombstones = new Set(snapshot.tombstones?.[sectionKey] ?? []);
  const overlayRows = (snapshot.overlay_rows?.[sectionKey] ?? []) as Record<string, unknown>[];

  const matchedOverlayIndices = new Set<number>();
  const reconciledRows: Record<string, unknown>[] = [];

  for (const sRow of serverRows || []) {
    const sId = String((sRow as any).id ?? "");
    const cId = String((sRow as any).client_id ?? "");

    if ((sId && tombstones.has(sId)) || (cId && tombstones.has(cId))) {
      continue;
    }

    const overlayIdx = overlayRows.findIndex(
      (oRow) =>
        (sId && String(oRow.id ?? "") === sId) ||
        (cId && String(oRow.client_id ?? "") === cId) ||
        (sId && String(oRow.client_id ?? "") === sId),
    );

    if (overlayIdx >= 0) {
      matchedOverlayIndices.add(overlayIdx);
      reconciledRows.push({
        ...sRow,
        ...overlayRows[overlayIdx],
        ...fieldErrorFor(snapshot, overlayRows[overlayIdx]),
        sync_status: "pending",
        _offline: true,
      });
    } else {
      reconciledRows.push({
        ...sRow,
        sync_status: (sRow as any).sync_status ?? "synced",
      });
    }
  }

  for (let i = 0; i < overlayRows.length; i++) {
    if (!matchedOverlayIndices.has(i)) {
      const oRow = overlayRows[i];
      const oId = String(oRow.id ?? "");
      const oCId = String(oRow.client_id ?? "");
      if ((oId && tombstones.has(oId)) || (oCId && tombstones.has(oCId))) {
        continue;
      }
      reconciledRows.push({
        ...oRow,
        ...fieldErrorFor(snapshot, oRow),
        sync_status: "pending",
        _offline: true,
      });
    }
  }

  return {
    header: mergedHeader,
    rows: reconciledRows as TRow[],
  };
}
