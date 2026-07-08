import { useCallback, useEffect, useState } from "react";
import { useToast } from "@/components/ui/toast";
import { useOnlineStatus } from "@/app/hooks/useOnlineStatus";
import {
  type ChildResource,
  createChildRow,
  deleteChildRow,
  updateChildRow,
} from "@/app/lib/api/daily-reports";
import { generateUUID, isOfflineDBAvailable } from "@/app/lib/offlineDB";
import {
  buildChildRowSyncMap,
  queueChildWrite,
  type RowSyncStatus,
} from "@/app/lib/offlineWrite";
import { syncPendingQueue } from "@/app/lib/syncService";
import { EditableGrid, type GridColumn, type GridRow } from "./EditableGrid";

export interface InlineGridTabProps {
  projectId: string;
  reportId: string | null;
  resource: ChildResource;
  columns: GridColumn[];
  serverRows: readonly { id?: string }[];
  emptyRow: () => Record<string, unknown>;
  toPayload: (row: GridRow) => Record<string, unknown>;
  onChanged: () => void;
  readOnly?: boolean;
  addLabel?: string;
  footer?: (rows: GridRow[]) => React.ReactNode;
}

/** Generic inline-editable tab backed by a daily-report child endpoint. */
export function InlineGridTab({
  projectId,
  reportId,
  resource,
  columns,
  serverRows,
  emptyRow,
  toPayload,
  onChanged,
  readOnly,
  addLabel,
  footer,
}: InlineGridTabProps) {
  const toast = useToast();
  const isOnline = useOnlineStatus();
  const canOffline = isOfflineDBAvailable();
  const [syncMap, setSyncMap] = useState<Map<string, RowSyncStatus>>(new Map());

  const refreshSyncMap = useCallback(async () => {
    if (!reportId || !canOffline) {
      setSyncMap(new Map());
      return;
    }
    setSyncMap(await buildChildRowSyncMap(projectId, reportId, resource));
  }, [projectId, reportId, resource, canOffline]);

  useEffect(() => {
    void refreshSyncMap();
  }, [refreshSyncMap, serverRows]);

  if (!reportId) {
    return (
      <p className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
        برای افزودن ردیف، ابتدا هدر گزارش را ذخیره کنید.
      </p>
    );
  }

  const rows: GridRow[] = serverRows.map((r) => ({
    ...(r as Record<string, unknown>),
    _key: r.id ?? generateUUID(),
  }));

  const onSaveRow = async (row: GridRow) => {
    const payload = toPayload(row);
    if (!isOnline && canOffline) {
      await queueChildWrite(
        projectId,
        reportId,
        resource,
        row.id ? "PATCH" : "POST",
        payload,
        row.id,
      );
      toast.warning("ذخیره آفلاین — در صف همگام‌سازی");
      await refreshSyncMap();
      return;
    }
    try {
      if (row.id) {
        await updateChildRow(projectId, reportId, resource, row.id, payload);
      } else {
        await createChildRow(projectId, reportId, resource, payload);
      }
      toast.success("ذخیره شد");
      onChanged();
    } catch (e) {
      if (typeof navigator !== "undefined" && !navigator.onLine && canOffline) {
        await queueChildWrite(projectId, reportId, resource, row.id ? "PATCH" : "POST", payload, row.id);
        toast.warning("ذخیره آفلاین — در صف همگام‌سازی");
        await refreshSyncMap();
        return;
      }
      toast.error((e as Error).message);
      throw e;
    }
  };

  const onDeleteRow = async (row: GridRow) => {
    if (!row.id) return;
    if (!isOnline && canOffline) {
      await queueChildWrite(projectId, reportId, resource, "DELETE", {}, row.id);
      toast.warning("حذف آفلاین — در صف همگام‌سازی");
      await refreshSyncMap();
      return;
    }
    try {
      await deleteChildRow(projectId, reportId, resource, row.id);
      toast.success("حذف شد");
      onChanged();
    } catch (e) {
      toast.error((e as Error).message);
      throw e;
    }
  };

  const onRetryRow = async () => {
    try {
      await syncPendingQueue();
      toast.success("همگام‌سازی انجام شد");
    } catch {
      toast.error("همگام‌سازی ناموفق بود");
    }
    await refreshSyncMap();
    onChanged();
  };

  const hasSyncInfo = canOffline && syncMap.size > 0;

  return (
    <EditableGrid
      columns={columns}
      rows={rows}
      makeEmptyRow={() => ({ ...emptyRow(), _key: generateUUID() })}
      onSaveRow={onSaveRow}
      onDeleteRow={onDeleteRow}
      readOnly={readOnly}
      addLabel={addLabel}
      footer={footer}
      syncStatusFor={
        hasSyncInfo
          ? (row) => (row.id ? (syncMap.get(row.id) ?? "synced") : undefined)
          : undefined
      }
      onRetryRow={() => void onRetryRow()}
    />
  );
}
