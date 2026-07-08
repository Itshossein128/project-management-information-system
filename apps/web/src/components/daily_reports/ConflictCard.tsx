import { useState } from "react";
import { AlertTriangle } from "lucide-react";
import { useToast } from "@/components/ui/toast";
import {
  clearSyncedItems,
  type ConflictEntry,
  getQueueItem,
  resolveConflict,
  updateQueueItem,
} from "@/app/lib/offlineDB";

type Resolution = "local" | "server" | "merge";

function pretty(value: unknown): string {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

export function ConflictCard({
  conflict,
  onResolved,
}: {
  conflict: ConflictEntry;
  onResolved: () => void;
}) {
  const toast = useToast();
  const [choice, setChoice] = useState<Resolution>("server");
  const [mergeText, setMergeText] = useState(() => pretty(conflict.local_payload));
  const [busy, setBusy] = useState(false);

  const apply = async () => {
    setBusy(true);
    try {
      const queueItem = await getQueueItem(conflict.queue_id);
      if (choice === "server") {
        // Discard the local change.
        if (queueItem) {
          await updateQueueItem(conflict.queue_id, { status: "synced" });
          await clearSyncedItems();
        }
        await resolveConflict(conflict.conflict_id, "resolved_server");
      } else if (choice === "local") {
        if (queueItem) {
          await updateQueueItem(conflict.queue_id, {
            status: "pending",
            retry_count: 0,
            error_message: null,
          });
        }
        await resolveConflict(conflict.conflict_id, "resolved_local");
      } else {
        let merged: unknown;
        try {
          merged = JSON.parse(mergeText);
        } catch {
          toast.error("JSON نامعتبر است");
          setBusy(false);
          return;
        }
        if (queueItem) {
          await updateQueueItem(conflict.queue_id, {
            payload: merged,
            status: "pending",
            retry_count: 0,
            error_message: null,
          });
        }
        await resolveConflict(conflict.conflict_id, "resolved_merged");
      }
      toast.success("تعارض حل شد");
      onResolved();
    } catch (e) {
      toast.error((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-4 rounded-xl border border-red-300 bg-card p-4">
      <div className="flex items-center gap-2 text-red-700 dark:text-red-300">
        <AlertTriangle className="size-5" />
        <h3 className="font-semibold">
          تعارض در {conflict.entity_type} — {new Date(conflict.created_at).toLocaleString("fa-IR")}
        </h3>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        <div>
          <p className="mb-1 text-sm font-medium text-muted-foreground">نسخه محلی (شما)</p>
          <pre className="max-h-52 overflow-auto rounded-md border border-border bg-muted/40 p-2 text-xs">
            {pretty(conflict.local_payload)}
          </pre>
        </div>
        <div>
          <p className="mb-1 text-sm font-medium text-muted-foreground">نسخه سرور</p>
          <pre className="max-h-52 overflow-auto rounded-md border border-border bg-muted/40 p-2 text-xs">
            {pretty(conflict.server_payload)}
          </pre>
        </div>
      </div>

      <div className="flex flex-wrap gap-4 text-sm">
        {(
          [
            ["server", "استفاده از نسخه سرور (رد تغییرات محلی)"],
            ["local", "استفاده از نسخه محلی (بازنویسی سرور)"],
            ["merge", "ادغام دستی"],
          ] as [Resolution, string][]
        ).map(([value, label]) => (
          <label key={value} className="flex items-center gap-2">
            <input
              type="radio"
              name={`res-${conflict.conflict_id}`}
              checked={choice === value}
              onChange={() => setChoice(value)}
            />
            {label}
          </label>
        ))}
      </div>

      {choice === "merge" ? (
        <textarea
          className="min-h-[160px] w-full rounded-md border border-input bg-transparent p-2 font-mono text-xs"
          value={mergeText}
          onChange={(e) => setMergeText(e.target.value)}
        />
      ) : null}

      <div className="flex justify-end">
        <button
          type="button"
          disabled={busy}
          onClick={apply}
          className="rounded-md bg-primary px-5 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          اعمال
        </button>
      </div>
    </div>
  );
}
