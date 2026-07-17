import { useState } from "react";
import { AlertTriangle, Loader2 } from "lucide-react";
import { apiFetch } from "@/app/lib/api-client";
import { useToast } from "@/components/ui/toast";
import { Badge } from "@/components/ui/badge";
import { ConflictMergeEditor } from "@/components/sync/ConflictMergeEditor";
import {
  type ConflictEntry,
  getConflictQueueEndpoint,
  removeQueueItem,
  resolveConflict,
} from "@/app/lib/offlineDB";

type Resolution = "local" | "server" | "merge";

const ENTITY_LABELS: Record<string, string> = {
  daily_report: "گزارش روزانه",
  daily_activity: "فعالیت",
  daily_labor: "نیروی انسانی",
  daily_equipment: "تجهیزات",
  daily_material: "مصالح",
  weather_log: "وضعیت جوی",
};

async function parseApiError(res: Response): Promise<string> {
  const raw = await res.text();
  if (!raw) return res.statusText || "خطا در ارتباط با سرور";
  try {
    const body = JSON.parse(raw) as {
      error?: { message?: string } | string;
      detail?: string;
    };
    if (typeof body.error === "object" && body.error?.message) return body.error.message;
    if (typeof body.error === "string") return body.error;
    if (body.detail) return body.detail;
  } catch {
    /* fall through */
  }
  return raw;
}

export function ConflictCard({
  conflict,
  index,
  onResolved,
  onRemoving,
}: {
  conflict: ConflictEntry;
  index: number;
  onResolved: () => void;
  onRemoving?: () => void;
}) {
  const toast = useToast();
  const [choice, setChoice] = useState<Resolution>("server");
  const [showMerge, setShowMerge] = useState(false);
  const [busy, setBusy] = useState(false);
  const [fading, setFading] = useState(false);

  const conflictReason =
    conflict.conflict_fields.length > 0
      ? `فیلدهای متعارض: ${conflict.conflict_fields.join("، ")}`
      : "تعارض در همگام‌سازی داده";

  const finishResolve = (toastMsg: string) => {
    setFading(true);
    onRemoving?.();
    window.setTimeout(() => {
      toast.success(toastMsg);
      onResolved();
    }, 300);
  };

  const patchPayload = async (payload: unknown, toastMsg: string) => {
    const queueInfo = await getConflictQueueEndpoint(conflict.queue_id);
    if (!queueInfo) {
      toast.error("رکورد صف همگام‌سازی یافت نشد");
      return false;
    }
    const res = await apiFetch(queueInfo.endpoint, {
      method: queueInfo.method === "PATCH" ? "PATCH" : "POST",
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const message = await parseApiError(res);
      toast.error(message);
      if (import.meta.env?.MODE === "test") {
        console.warn("[DAILY_LOG] conflict PATCH failed:", message);
      }
      return false;
    }
    await resolveConflict(
      conflict.conflict_id,
      toastMsg.includes("ادغام") ? "resolved_merged" : "resolved_local",
    );
    await removeQueueItem(conflict.queue_id);
    finishResolve(toastMsg);
    return true;
  };

  const apply = async () => {
    if (choice === "merge") {
      setShowMerge(true);
      return;
    }
    setBusy(true);
    try {
      if (choice === "server") {
        await resolveConflict(conflict.conflict_id, "resolved_server");
        await removeQueueItem(conflict.queue_id);
        finishResolve("نسخه سرور اعمال شد");
        return;
      }
      await patchPayload(conflict.local_payload, "نسخه شما اعمال شد");
    } catch (e) {
      toast.error((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const handleMergeSave = async (merged: Record<string, unknown>) => {
    setBusy(true);
    try {
      await patchPayload(merged, "نسخه ادغام شده ذخیره شد");
    } catch (e) {
      toast.error((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const entityLabel = ENTITY_LABELS[conflict.entity_type] ?? conflict.entity_type;
  const shortId = conflict.conflict_id.slice(0, 8);

  return (
    <div
      data-testid={`conflict-card-${index}`}
      className={`space-y-4 rounded-xl border border-red-300 bg-card p-4 transition-opacity duration-300 ${fading ? "opacity-0" : "opacity-100"}`}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <AlertTriangle className="size-5 text-red-700 dark:text-red-300" />
          <Badge variant="neutral" label={entityLabel} />
          <span className="text-sm text-muted-foreground">
            {new Date(conflict.created_at).toLocaleString("fa-IR")}
          </span>
          <span className="font-mono text-xs text-muted-foreground" title={conflict.conflict_id}>
            #{shortId}
          </span>
        </div>
      </div>

      <p className="text-sm text-red-800 dark:text-red-200">{conflictReason}</p>

      {!showMerge ? (
        <>
          <div className="flex flex-wrap gap-4 text-sm">
            <label className="flex items-center gap-2">
              <input
                type="radio"
                data-testid="conflict-option-server"
                name={`res-${conflict.conflict_id}`}
                checked={choice === "server"}
                onChange={() => setChoice("server")}
              />
              استفاده از نسخه سرور
            </label>
            <label className="flex items-center gap-2">
              <input
                type="radio"
                data-testid="conflict-option-local"
                name={`res-${conflict.conflict_id}`}
                checked={choice === "local"}
                onChange={() => setChoice("local")}
              />
              استفاده از نسخه من
            </label>
            <label className="flex items-center gap-2">
              <input
                type="radio"
                data-testid="conflict-option-merge"
                name={`res-${conflict.conflict_id}`}
                checked={choice === "merge"}
                onChange={() => setChoice("merge")}
              />
              ادغام دستی
            </label>
          </div>

          <div className="flex justify-end">
            <button
              type="button"
              data-testid="conflict-apply-btn"
              disabled={busy || !choice}
              aria-busy={busy}
              onClick={() => void apply()}
              className="inline-flex items-center gap-2 rounded-md bg-primary px-5 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              {busy && choice !== "merge" && <Loader2 className="size-4 animate-spin" />}
              اعمال تصمیم
            </button>
          </div>
        </>
      ) : (
        <ConflictMergeEditor
          localPayload={conflict.local_payload}
          serverPayload={conflict.server_payload}
          conflictFields={conflict.conflict_fields}
          busy={busy}
          onCancel={() => setShowMerge(false)}
          onSave={(merged) => void handleMergeSave(merged)}
        />
      )}
    </div>
  );
}
