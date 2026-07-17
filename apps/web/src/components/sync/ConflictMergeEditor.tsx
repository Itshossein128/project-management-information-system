import { useMemo, useState } from "react";

function asRecord(value: unknown): Record<string, unknown> {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }
  return {};
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "object") {
    try {
      return JSON.stringify(value);
    } catch {
      return String(value);
    }
  }
  return String(value);
}

function inputTypeFor(value: unknown): "text" | "number" {
  return typeof value === "number" ? "number" : "text";
}

export interface ConflictMergeEditorProps {
  localPayload: unknown;
  serverPayload: unknown;
  conflictFields: string[];
  onSave: (merged: Record<string, unknown>) => void;
  onCancel: () => void;
  busy?: boolean;
}

export function ConflictMergeEditor({
  localPayload,
  serverPayload,
  conflictFields,
  onSave,
  onCancel,
  busy = false,
}: ConflictMergeEditorProps) {
  const local = asRecord(localPayload);
  const server = asRecord(serverPayload);
  const conflictSet = useMemo(() => new Set(conflictFields), [conflictFields]);

  const allKeys = useMemo(() => {
    const keys = new Set(
      [...Object.keys(local), ...Object.keys(server)].filter((k) => {
        const v = local[k] ?? server[k];
        if (Array.isArray(v)) return false;
        if (v !== null && typeof v === "object") return false;
        if (k.endsWith("_label") || k.endsWith("_name")) return false;
        return true;
      }),
    );
    const ordered = [...conflictFields.filter((k) => keys.has(k))];
    for (const k of keys) {
      if (!conflictSet.has(k)) ordered.push(k);
    }
    return ordered;
  }, [local, server, conflictFields, conflictSet]);

  const [merged, setMerged] = useState<Record<string, unknown>>(() => {
    const initial: Record<string, unknown> = { ...server };
    for (const key of conflictFields) {
      if (key in server) initial[key] = server[key];
      else if (key in local) initial[key] = local[key];
    }
    return initial;
  });

  const setField = (key: string, raw: string, original: unknown) => {
    if (typeof original === "number") {
      const n = raw === "" ? null : Number(raw);
      setMerged((prev) => ({ ...prev, [key]: Number.isNaN(n) ? raw : n }));
      return;
    }
    if (typeof original === "boolean") {
      setMerged((prev) => ({ ...prev, [key]: raw === "true" }));
      return;
    }
    setMerged((prev) => ({ ...prev, [key]: raw }));
  };

  return (
    <div data-testid="conflict-merge-editor" className="space-y-3 rounded-lg border border-border bg-muted/20 p-3">
      <div className="grid grid-cols-3 gap-2 text-center text-xs font-medium text-muted-foreground">
        <span>نسخه سرور</span>
        <span>نسخه نهایی</span>
        <span>نسخه شما</span>
      </div>

      {allKeys.map((key) => {
        const isConflict = conflictSet.has(key);
        const localVal = local[key];
        const serverVal = server[key];
        const differs = formatValue(localVal) !== formatValue(serverVal);

        if (!isConflict) {
          return (
            <div key={key} className="rounded-md border border-border bg-card px-3 py-2 text-sm">
              <span className="font-medium text-muted-foreground">{key}: </span>
              <span>{formatValue(serverVal ?? localVal)}</span>
            </div>
          );
        }

        return (
          <div key={key} className="grid grid-cols-3 gap-2 text-sm">
            <div
              data-testid={`conflict-merge-field-server-${key}`}
              className={`rounded-md border px-2 py-1.5 ${differs ? "border-amber-400 bg-amber-50 dark:bg-amber-950/30" : "border-border bg-card"}`}
            >
              {formatValue(serverVal)}
            </div>
            <input
              data-testid={`conflict-merge-field-input-${key}`}
              type={inputTypeFor(serverVal ?? localVal)}
              className="rounded-md border border-input bg-background px-2 py-1.5"
              value={merged[key] === null || merged[key] === undefined ? "" : String(merged[key])}
              onChange={(e) => setField(key, e.target.value, serverVal ?? localVal)}
            />
            <div
              data-testid={`conflict-merge-field-local-${key}`}
              className={`rounded-md border px-2 py-1.5 ${differs ? "border-amber-400 bg-amber-50 dark:bg-amber-950/30" : "border-border bg-card"}`}
            >
              {formatValue(localVal)}
            </div>
          </div>
        );
      })}

      <div className="flex justify-end gap-2 pt-2">
        <button
          type="button"
          data-testid="conflict-merge-cancel-btn"
          disabled={busy}
          onClick={onCancel}
          className="rounded-md border border-border px-4 py-2 text-sm hover:bg-muted disabled:opacity-50"
        >
          انصراف
        </button>
        <button
          type="button"
          data-testid="conflict-merge-save-btn"
          disabled={busy}
          onClick={() => onSave(merged)}
          className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          ذخیره نسخه ادغام شده
        </button>
      </div>
    </div>
  );
}
