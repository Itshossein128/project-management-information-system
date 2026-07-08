import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router";
import { CheckCircle2 } from "lucide-react";
import { useToast } from "@/components/ui/toast";
import { PATHS } from "@/app/routeVars";
import {
  type ConflictEntry,
  getUnresolvedConflicts,
  isOfflineDBAvailable,
} from "@/app/lib/offlineDB";
import { syncPendingQueue } from "@/app/lib/syncService";
import { Breadcrumb, PageHeader } from "@/components/layout/page-header";
import { ConflictCard } from "@/components/daily_reports/ConflictCard";

export default function SyncConflictsPage() {
  const { projectId = "" } = useParams();
  const toast = useToast();
  const [conflicts, setConflicts] = useState<ConflictEntry[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    if (!isOfflineDBAvailable() || !projectId) {
      setLoading(false);
      return;
    }
    try {
      setConflicts(await getUnresolvedConflicts(projectId));
    } catch {
      /* db not ready */
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void load();
  }, [load]);

  const onResolved = async () => {
    // Re-run the queue so re-queued local/merge resolutions push to the server.
    try {
      await syncPendingQueue();
    } catch {
      /* offline; will retry later */
    }
    await load();
  };

  const listHref = `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_DAILY_REPORTS}`;

  return (
    <main className="page-main page-shell mx-auto max-w-4xl px-4 py-6">
      <Breadcrumb
        items={[
          { label: "گزارش‌های روزانه", href: listHref },
          { label: "تعارض‌های همگام‌سازی" },
        ]}
      />
      <PageHeader
        title="تعارض‌های همگام‌سازی"
        subtitle="مواردی که هنگام همگام‌سازی با نسخه سرور تعارض داشتند"
      />

      {loading ? (
        <p className="text-sm text-muted-foreground">در حال بارگذاری...</p>
      ) : conflicts.length === 0 ? (
        <div className="flex flex-col items-center gap-2 rounded-xl border border-border bg-card p-10 text-center">
          <CheckCircle2 className="size-10 text-emerald-500" />
          <p className="text-sm text-muted-foreground">هیچ تعارضی وجود ندارد.</p>
          <Link to={listHref} className="text-sm text-primary hover:underline">
            بازگشت به گزارش‌ها
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {conflicts.map((c) => (
            <ConflictCard
              key={c.conflict_id}
              conflict={c}
              onResolved={() => {
                void onResolved();
                toast.success("تعارض حل شد");
              }}
            />
          ))}
        </div>
      )}
    </main>
  );
}
