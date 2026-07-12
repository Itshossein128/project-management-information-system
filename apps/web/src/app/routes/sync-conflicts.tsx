import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { CheckCircle2 } from "lucide-react";
import { useToast } from "@/components/ui/toast";
import { PATHS } from "@/app/routeVars";
import {
  type ConflictEntry,
  getUnresolvedConflicts,
  isOfflineDBAvailable,
} from "@/app/lib/offlineDB";
import { Breadcrumb, PageHeader } from "@/components/layout/page-header";
import { ConflictCard } from "@/components/daily_reports/ConflictCard";
import { Badge } from "@/components/ui/badge";

export default function SyncConflictsPage() {
  const { projectId = "" } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [conflicts, setConflicts] = useState<ConflictEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [removingIds, setRemovingIds] = useState<Set<string>>(new Set());
  const navigatedRef = useRef(false);

  const listHref = `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_DAILY_REPORTS}`;

  const load = useCallback(async () => {
    if (!isOfflineDBAvailable() || !projectId) {
      setLoading(false);
      return;
    }
    try {
      const next = await getUnresolvedConflicts(projectId);
      setConflicts(next.filter((c) => !removingIds.has(c.conflict_id)));
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
        <p className="text-sm text-muted-foreground">در حال بارگذاری...</p>
      ) : visibleConflicts.length === 0 ? (
        <div
          data-testid="conflict-empty-state"
          className="flex flex-col items-center gap-3 rounded-xl border border-border bg-card p-10 text-center"
        >
          <CheckCircle2 className="size-10 text-emerald-500" />
          <p className="font-medium">هیچ تعارضی وجود ندارد</p>
          <p className="text-sm text-muted-foreground">
            تمام داده‌های آفلاین با موفقیت همگام‌سازی شده‌اند
          </p>
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
    </main>
  );
}
