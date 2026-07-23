import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { CheckCircle2, RefreshCw, Trash2 } from "lucide-react";
import { useToast } from "@/components/ui/toast";
import { PATHS } from "@/app/routeVars";
import {
  type ConflictEntry,
  getFailedQueue,
  getUnresolvedConflicts,
  isOfflineDBAvailable,
  type QueueItem,
} from "@/app/lib/offlineDB";
import { discardFailedQueueItem, retryFailedQueueItem } from "@/app/lib/syncService";
import { EmptyState } from "@/components/layout/empty-state";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { ConflictCard } from "@/components/daily_reports/ConflictCard";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/sprint-button";

export default function SyncConflictsPage() {
  const { projectId = "" } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [conflicts, setConflicts] = useState<ConflictEntry[]>([]);
  const [failedItems, setFailedItems] = useState<QueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [removingIds, setRemovingIds] = useState<Set<string>>(new Set());
  const navigatedRef = useRef(false);

  const listHref = `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_DAILY_REPORTS}`;
  const overviewHref = `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_OVERVIEW}`;

  const load = useCallback(async () => {
    if (!isOfflineDBAvailable() || !projectId) {
      setLoading(false);
      return;
    }
    try {
      const [next, failed] = await Promise.all([
        getUnresolvedConflicts(projectId),
        getFailedQueue(),
      ]);
      setConflicts(next.filter((c) => !removingIds.has(c.conflict_id)));
      setFailedItems(failed.filter((f) => f.project_id === projectId));
    } catch {
      /* db not ready */
    } finally {
      setLoading(false);
    }
  }, [projectId, removingIds]);

  useEffect(() => {
    void load();
  }, [load]);

  const handleResolved = async () => {
    if (!isOfflineDBAvailable() || !projectId) return;
    const remaining = await getUnresolvedConflicts(projectId);
    const visible = remaining.filter((c) => !removingIds.has(c.conflict_id));
    setConflicts(visible);
    if (visible.length === 0 && !navigatedRef.current) {
      navigatedRef.current = true;
      toast.success("همه تعارض‌ها حل شدند");
      navigate(listHref);
    }
  };

  const visibleConflicts = conflicts.filter((c) => !removingIds.has(c.conflict_id));

  return (
    <main
      data-testid="conflict-page-container"
      className="page-main page-shell mx-auto max-w-4xl px-4 py-6"
    >
      <Breadcrumb
        items={[
          { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
          { label: "نمای کلی", href: overviewHref },
          { label: "گزارش‌های روزانه", href: listHref },
          { label: "تعارض‌های همگام‌سازی" },
        ]}
      />
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <PageHeader
          title="تعارض‌های همگام‌سازی"
          subtitle="مواردی که هنگام همگام‌سازی با نسخه سرور تعارض داشتند"
        />
        {visibleConflicts.length > 0 ? (
          <Badge
            variant="danger"
            className="shrink-0"
            label={`${visibleConflicts.length} تعارض نیاز به بررسی دارد`}
          />
        ) : null}
      </div>

      {loading ? (
        <LoadingSkeleton rows={6} />
      ) : visibleConflicts.length === 0 ? (
        <div data-testid="conflict-empty-state">
          <EmptyState
            icon={<CheckCircle2 className="text-success-500" />}
            title="هیچ تعارضی وجود ندارد"
            description="تمام داده‌های آفلاین با موفقیت همگام‌سازی شده‌اند"
          />
        </div>
      ) : (
        <div className="space-y-4">
          {visibleConflicts.map((c, index) => (
            <ConflictCard
              key={c.conflict_id}
              index={index}
              conflict={c}
              onRemoving={() => {
                setRemovingIds((prev) => new Set(prev).add(c.conflict_id));
              }}
              onResolved={() => {
                void handleResolved();
              }}
            />
          ))}
        </div>
      )}

      {failedItems.length > 0 ? (
        <section className="mt-8 space-y-3">
          <h2 className="text-lg font-semibold">صف ناموفق ({failedItems.length})</h2>
          {failedItems.map((item) => (
            <div
              key={item.queue_id}
              className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border bg-card p-4 text-sm"
            >
              <div>
                <p className="font-medium">{item.entity_type}</p>
                <p className="text-muted-foreground">
                  {item.error_message ?? "خطای نامشخص"}
                </p>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    void retryFailedQueueItem(item.queue_id).then(() => load());
                  }}
                >
                  <RefreshCw className="size-4" />
                  تلاش مجدد
                </Button>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => {
                    void discardFailedQueueItem(item.queue_id).then(() => load());
                  }}
                >
                  <Trash2 className="size-4" />
                  حذف
                </Button>
              </div>
            </div>
          ))}
        </section>
      ) : null}
    </main>
  );
}
