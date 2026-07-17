import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Camera,
  CheckCircle2,
  Clock,
  Plus,
  RefreshCw,
  Save,
  Trash2,
} from "lucide-react";
import { cn } from "@/app/lib/utils";
import type { RowSyncStatus } from "@/app/lib/offlineWrite";

export type CellType =
  | "text"
  | "number"
  | "select"
  | "checkbox"
  | "time"
  | "combobox"
  | "photo";

export interface GridColumn {
  key: string;
  header: string;
  type?: CellType;
  options?: { value: string; label: string }[];
  /** For combobox: id-bearing suggestions ({ value: id, label: display }). */
  comboOptions?: { value: string; label: string }[];
  /** For combobox: the row field that stores the selected id (null when free text). */
  refKey?: string;
  width?: string;
  placeholder?: string;
  /** Read-only computed cell. */
  computed?: (row: GridRow) => string | number;
}

export type GridRow = Record<string, unknown> & {
  id?: string;
  _dirty?: boolean;
  _key: string;
};

export interface EditableGridProps {
  columns: GridColumn[];
  rows: GridRow[];
  makeEmptyRow: () => GridRow;
  onSaveRow: (row: GridRow, options?: { silent?: boolean }) => Promise<void>;
  onDeleteRow: (row: GridRow) => Promise<void>;
  readOnly?: boolean;
  addLabel?: string;
  footer?: (rows: GridRow[]) => React.ReactNode;
  /** Per-row offline sync status, keyed by row id. */
  syncStatusFor?: (row: GridRow) => RowSyncStatus | undefined;
  onRetryRow?: (row: GridRow) => void;
  /** Upload handler for photo column cells — returns stored file id. */
  onPhotoUpload?: (file: File) => Promise<string>;
}

const SYNC_META: Record<
  RowSyncStatus,
  { Icon: typeof CheckCircle2; className: string; title: string }
> = {
  synced: { Icon: CheckCircle2, className: "text-emerald-500", title: "همگام" },
  pending: {
    Icon: Clock,
    className: "text-amber-500",
    title: "در صف همگام‌سازی",
  },
  failed: {
    Icon: RefreshCw,
    className: "text-red-500",
    title: "ناموفق — تلاش مجدد",
  },
  conflict: { Icon: AlertTriangle, className: "text-red-600", title: "تعارض" },
};

function SyncCell({
  status,
  onRetry,
}: {
  status: RowSyncStatus;
  onRetry?: () => void;
}) {
  const { Icon, className, title } = SYNC_META[status];
  if (status === "failed" && onRetry) {
    return (
      <button
        type="button"
        title={title}
        aria-label={title}
        onClick={onRetry}
        className={cn("rounded p-1 hover:bg-muted", className)}
      >
        <Icon className="size-4" />
      </button>
    );
  }
  return (
    <span
      title={title}
      aria-label={title}
      className={cn("inline-flex", className)}
    >
      <Icon className="size-4" />
    </span>
  );
}

const inputClass =
  "h-8 w-full rounded border border-input bg-transparent px-2 text-sm outline-none focus-visible:border-ring focus-visible:ring-[2px] focus-visible:ring-ring/40 disabled:opacity-50";

export function EditableGrid({
  columns,
  rows: serverRows,
  makeEmptyRow,
  onSaveRow,
  onDeleteRow,
  readOnly,
  addLabel = "افزودن ردیف",
  footer,
  syncStatusFor,
  onRetryRow,
  onPhotoUpload,
}: EditableGridProps) {
  const [rows, setRows] = useState<GridRow[]>(serverRows);
  const [savingKey, setSavingKey] = useState<string | null>(null);
  const [autosavingKey, setAutosavingKey] = useState<string | null>(null);

  useEffect(() => {
    setRows(serverRows);
  }, [serverRows]);

  const setCell = (key: string, colKey: string, value: unknown) => {
    setRows((prev) =>
      prev.map((r) =>
        r._key === key ? { ...r, [colKey]: value, _dirty: true } : r,
      ),
    );
  };

  const addRow = () => setRows((prev) => [...prev, makeEmptyRow()]);

  const saveRow = async (row: GridRow, options?: { silent?: boolean }) => {
    setSavingKey(row._key);
    try {
      await onSaveRow(row, options);
      setRows((prev) =>
        prev.map((r) => (r._key === row._key ? { ...r, _dirty: false } : r)),
      );
    } finally {
      setSavingKey(null);
    }
  };

  useEffect(() => {
    if (readOnly || autosavingKey) return;
    const nextDirtyRow = rows.find((r) => r._dirty && r._key !== savingKey);
    if (!nextDirtyRow) return;
    const timer = window.setTimeout(() => {
      setAutosavingKey(nextDirtyRow._key);
      void saveRow(nextDirtyRow, { silent: true }).finally(() => {
        setAutosavingKey(null);
      });
    }, 900);
    return () => window.clearTimeout(timer);
  }, [rows, readOnly, savingKey, autosavingKey]);

  const deleteRow = async (row: GridRow) => {
    if (!row.id) {
      setRows((prev) => prev.filter((r) => r._key !== row._key));
      return;
    }
    setSavingKey(row._key);
    try {
      await onDeleteRow(row);
      setRows((prev) => prev.filter((r) => r._key !== row._key));
    } finally {
      setSavingKey(null);
    }
  };

  const listId = useMemo(
    () => `combo-${Math.random().toString(36).slice(2)}`,
    [],
  );

  return (
    <div className="space-y-3">
      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full min-w-[720px] border-collapse text-sm">
          <thead>
            <tr className="bg-muted/50 text-muted-foreground">
              <th className="w-10 px-2 py-2 text-center font-medium">#</th>
              {columns.map((c) => (
                <th
                  key={c.key}
                  className="px-2 py-2 text-right font-medium"
                  style={c.width ? { width: c.width } : undefined}
                >
                  {c.header}
                </th>
              ))}
              {syncStatusFor ? (
                <th className="w-12 px-2 py-2 text-center font-medium">
                  وضعیت
                </th>
              ) : null}
              {!readOnly ? (
                <th className="w-20 px-2 py-2 text-center font-medium">
                  عملیات
                </th>
              ) : null}
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td
                  colSpan={
                    columns.length +
                    1 +
                    (syncStatusFor ? 1 : 0) +
                    (readOnly ? 0 : 1)
                  }
                  className="px-3 py-6 text-center text-muted-foreground"
                >
                  موردی ثبت نشده است
                </td>
              </tr>
            ) : null}
            {rows.map((row, idx) => (
              <tr key={row._key} className="border-t border-border">
                <td className="px-2 py-1 text-center text-muted-foreground">
                  {idx + 1}
                </td>
                {columns.map((col) => (
                  <td key={col.key} className="px-2 py-1">
                    {renderCell(col, row, setCell, readOnly, listId, onPhotoUpload)}
                  </td>
                ))}
                {syncStatusFor ? (
                  <td className="px-2 py-1 text-center">
                    {(() => {
                      const s = syncStatusFor(row);
                      return s ? (
                        <SyncCell
                          status={s}
                          onRetry={
                            onRetryRow ? () => onRetryRow(row) : undefined
                          }
                        />
                      ) : null;
                    })()}
                  </td>
                ) : null}
                {!readOnly ? (
                  <td className="px-2 py-1">
                    <div className="flex items-center justify-center gap-1">
                      <button
                        type="button"
                        title="ذخیره"
                        aria-label="ذخیره"
                        disabled={!row._dirty || savingKey === row._key}
                        onClick={() => saveRow(row)}
                        className={cn(
                          "rounded p-1 hover:bg-muted disabled:opacity-30",
                          row._dirty
                            ? "text-emerald-600"
                            : "text-muted-foreground",
                        )}
                      >
                        <Save className="size-4" />
                      </button>
                      <button
                        type="button"
                        title="حذف"
                        aria-label="حذف"
                        disabled={savingKey === row._key}
                        onClick={() => deleteRow(row)}
                        className="rounded p-1 text-red-600 hover:bg-muted disabled:opacity-30"
                      >
                        <Trash2 className="size-4" />
                      </button>
                    </div>
                  </td>
                ) : null}
              </tr>
            ))}
          </tbody>
          {footer ? <tfoot>{footer(rows)}</tfoot> : null}
        </table>
      </div>

      {!readOnly ? (
        <button
          type="button"
          onClick={addRow}
          className="inline-flex items-center gap-1 rounded-md border border-dashed border-border px-3 py-1.5 text-sm text-muted-foreground hover:bg-muted/40"
        >
          <Plus className="size-4" />
          {addLabel}
        </button>
      ) : null}
    </div>
  );
}

function renderCell(
  col: GridColumn,
  row: GridRow,
  setCell: (key: string, colKey: string, value: unknown) => void,
  readOnly: boolean | undefined,
  listId: string,
  onPhotoUpload?: (file: File) => Promise<string>,
) {
  if (col.computed) {
    return (
      <span className="block px-1 text-muted-foreground">
        {col.computed(row)}
      </span>
    );
  }
  const value = row[col.key];
  const disabled = readOnly;

  if (col.type === "checkbox") {
    return (
      <input
        type="checkbox"
        checked={Boolean(value)}
        disabled={disabled}
        onChange={(e) => setCell(row._key, col.key, e.target.checked)}
        className="size-4"
      />
    );
  }

  if (col.type === "photo") {
    const fileId = (value as string | null) ?? null;
    return (
      <label
        className={cn(
          "inline-flex cursor-pointer items-center gap-1 rounded border border-dashed border-border px-2 py-1 text-xs",
          readOnly && "pointer-events-none opacity-50",
          fileId && "border-emerald-400 text-emerald-700",
        )}
      >
        <Camera className="size-3.5" />
        {fileId ? "عکس" : "افزودن"}
        <input
          type="file"
          accept="image/*"
          className="sr-only"
          disabled={readOnly || !onPhotoUpload}
          onChange={async (e) => {
            const file = e.target.files?.[0];
            if (!file || !onPhotoUpload) return;
            try {
              const id = await onPhotoUpload(file);
              setCell(row._key, col.key, id);
            } catch {
              /* caller may toast */
            }
            e.target.value = "";
          }}
        />
      </label>
    );
  }

  if (col.type === "select") {
    return (
      <select
        className={inputClass}
        value={(value as string) ?? ""}
        disabled={disabled}
        onChange={(e) => setCell(row._key, col.key, e.target.value)}
      >
        <option value="" disabled>
          —
        </option>
        {(col.options ?? []).map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    );
  }

  if (col.type === "combobox") {
    const cid = `${listId}-${col.key}`;
    return (
      <>
        <input
          className={inputClass}
          list={cid}
          value={(value as string) ?? ""}
          placeholder={col.placeholder}
          disabled={disabled}
          onChange={(e) => {
            const text = e.target.value;
            setCell(row._key, col.key, text);
            if (col.refKey) {
              const match = (col.comboOptions ?? []).find(
                (o) => o.label === text,
              );
              setCell(row._key, col.refKey, match ? match.value : null);
            }
          }}
        />
        <datalist id={cid}>
          {(col.comboOptions ?? []).map((o) => (
            <option key={o.value} value={o.label} />
          ))}
        </datalist>
      </>
    );
  }

  return (
    <input
      type={
        col.type === "number" ? "number" : col.type === "time" ? "time" : "text"
      }
      className={inputClass}
      value={(value as string | number) ?? ""}
      placeholder={col.placeholder}
      disabled={disabled}
      onChange={(e) =>
        setCell(
          row._key,
          col.key,
          col.type === "number"
            ? e.target.value === ""
              ? null
              : Number(e.target.value)
            : e.target.value,
        )
      }
    />
  );
}
