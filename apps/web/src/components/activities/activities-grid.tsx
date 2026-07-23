import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Clock,
  GitBranchPlus,
  LayoutGrid,
  Network,
  Pencil,
  Scale,
  Search,
  Trash2,
} from "lucide-react";
import { Fragment, useState } from "react";
import {
  deleteActivity,
  fetchActivities,
  fetchActivity,
  fetchWeightSummary,
  type Activity,
  type ActivityStatus,
} from "@/app/lib/api/activities";
import { fetchMembers } from "@/app/lib/api/members";
import { fetchWBSFlat } from "@/app/lib/api/wbs";
import { usePermission } from "@/app/contexts/project-context";
import { ActivityDrawer } from "@/components/activities/activity-drawer";
import { AddRelationModal } from "@/components/activities/add-relation-modal";
import { NetworkDiagramView } from "@/components/activities/network-diagram-view";
import { EmptyState } from "@/components/layout/empty-state";
import { LoadingSkeleton } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Modal } from "@/components/overlay/modal";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/sprint-button";
import { Checkbox, Field, Input, Select } from "@/components/form";
import { useToast } from "@/components/ui/toast";
import { cn } from "@/app/lib/utils";

const STATUS_LABELS: Record<ActivityStatus, { label: string; variant: "neutral" | "info" | "warning" | "success" }> = {
  not_started: { label: "شروع نشده", variant: "neutral" },
  in_progress: { label: "در حال اجرا", variant: "info" },
  suspended: { label: "متوقف", variant: "warning" },
  completed: { label: "تکمیل شده", variant: "success" },
};

function formatWeight(weight: string | null): string {
  if (weight == null || weight === "") return "—";
  return `${Math.round(parseFloat(weight) * 10000) / 100}٪`;
}

export interface ActivitiesGridProps {
  projectId: string;
}

export function ActivitiesGrid({ projectId }: ActivitiesGridProps) {
  const toast = useToast();
  const qc = useQueryClient();
  const { has } = usePermission(projectId);
  const canEdit = has("edit_activities");

  const [viewMode, setViewMode] = useState<"table" | "network">("table");
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<ActivityStatus | "">("");
  const [wbsFilter, setWbsFilter] = useState("");
  const [responsibleFilter, setResponsibleFilter] = useState("");
  const [overdueOnly, setOverdueOnly] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editActivity, setEditActivity] = useState<Activity | null>(null);
  const [relationAnchor, setRelationAnchor] = useState<Activity | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Activity | null>(null);
  const [weightModalOpen, setWeightModalOpen] = useState(false);

  const listParams = {
    page,
    per_page: 50,
    search: search || undefined,
    status: statusFilter || undefined,
    wbs_id: wbsFilter || undefined,
    responsible_id: responsibleFilter || undefined,
    is_overdue: overdueOnly || undefined,
  };

  const { data, isLoading, isFetching, isError, refetch } = useQuery({
    queryKey: ["activities", projectId, listParams],
    queryFn: () => fetchActivities(projectId, listParams),
    enabled: viewMode === "table",
  });

  const { data: expandedDetail } = useQuery({
    queryKey: ["activity", projectId, expandedId],
    queryFn: () => fetchActivity(projectId, expandedId!),
    enabled: Boolean(expandedId),
  });

  const { data: wbsFlat = [] } = useQuery({
    queryKey: ["wbs-flat", projectId],
    queryFn: () => fetchWBSFlat(projectId),
  });

  const { data: members = [] } = useQuery({
    queryKey: ["members", projectId],
    queryFn: () => fetchMembers(projectId),
  });

  const { data: weightSummary } = useQuery({
    queryKey: ["activity-weight-summary", projectId],
    queryFn: () => fetchWeightSummary(projectId),
    enabled: weightModalOpen,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteActivity(projectId, id),
    onSuccess: () => {
      toast.success("فعالیت حذف شد");
      setDeleteTarget(null);
      void qc.invalidateQueries({ queryKey: ["activities", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const activities = data?.results ?? [];
  const totalCount = data?.count ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalCount / 50));

  function openCreate() {
    setEditActivity(null);
    setDrawerOpen(true);
  }

  async function openEdit(act: Activity) {
    try {
      const detail = await fetchActivity(projectId, act.activity_id);
      setEditActivity(detail);
      setDrawerOpen(true);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "خطا");
    }
  }

  async function openFromNetwork(id: string) {
    try {
      const detail = await fetchActivity(projectId, id);
      setEditActivity(detail);
      setDrawerOpen(true);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "خطا");
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div className="flex flex-wrap items-end gap-3">
          {viewMode === "table" ? (
            <>
              <Field name="activity_search" label="جستجو" htmlFor="activity-search">
                {() => (
                  <div className="relative">
                    <Search className="absolute start-2 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="activity-search"
                      className="w-48 ps-8"
                      placeholder="جستجو…"
                      value={search}
                      onChange={(e) => {
                        setSearch(e.target.value);
                        setPage(1);
                      }}
                    />
                  </div>
                )}
              </Field>
              <Select
                name="wbs_filter"
                label="WBS"
                value={wbsFilter || "all"}
                onChange={(e) => {
                  setWbsFilter(e.target.value === "all" ? "" : e.target.value);
                  setPage(1);
                }}
                options={[
                  { value: "all", label: "همه WBS" },
                  ...wbsFlat.map((n) => ({
                    value: n.wbs_id,
                    label: `${n.wbs_code} — ${n.wbs_name}`,
                  })),
                ]}
                fieldClassName="min-w-[10rem]"
              />
              <Select
                name="status_filter"
                label="وضعیت"
                value={statusFilter || "all"}
                onChange={(e) => {
                  setStatusFilter(
                    e.target.value === "all"
                      ? ""
                      : (e.target.value as ActivityStatus),
                  );
                  setPage(1);
                }}
                options={[
                  { value: "all", label: "همه وضعیت‌ها" },
                  ...Object.entries(STATUS_LABELS).map(([k, v]) => ({
                    value: k,
                    label: v.label,
                  })),
                ]}
                fieldClassName="min-w-[9rem]"
              />
              <Select
                name="responsible_filter"
                label="مسئول"
                value={responsibleFilter || "all"}
                onChange={(e) => {
                  setResponsibleFilter(
                    e.target.value === "all" ? "" : e.target.value,
                  );
                  setPage(1);
                }}
                options={[
                  { value: "all", label: "همه مسئولین" },
                  ...members
                    .filter((m) => m.user_id)
                    .map((m) => ({
                      value: m.user_id!,
                      label: m.full_name,
                    })),
                ]}
                fieldClassName="min-w-[9rem]"
              />
              <Checkbox
                name="overdue_only"
                label="فقط معوق"
                checked={overdueOnly}
                onChange={(e) => {
                  setOverdueOnly(
                    Boolean((e.target as unknown as { value: boolean }).value),
                  );
                  setPage(1);
                }}
                fieldClassName="pb-2"
              />
            </>
          ) : null}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="flex rounded-md border border-border p-0.5">
            <Button
              variant={viewMode === "table" ? "primary" : "ghost"}
              size="sm"
              onClick={() => setViewMode("table")}
            >
              <LayoutGrid className="size-4" />
              جدول
            </Button>
            <Button
              variant={viewMode === "network" ? "primary" : "ghost"}
              size="sm"
              onClick={() => setViewMode("network")}
            >
              <Network className="size-4" />
              شبکه
            </Button>
          </div>
          <Button variant="secondary" size="sm" onClick={() => setWeightModalOpen(true)}>
            <Scale className="size-4" />
            وزن‌سنجی
          </Button>
          {canEdit ? (
            <Button size="sm" onClick={openCreate}>افزودن فعالیت</Button>
          ) : null}
        </div>
      </div>

      {viewMode === "network" ? (
        <NetworkDiagramView projectId={projectId} onNodeClick={(id) => void openFromNetwork(id)} />
      ) : isLoading ? (
        <LoadingSkeleton rows={8} />
      ) : isError ? (
        <QueryErrorState onRetry={() => void refetch()} />
      ) : activities.length === 0 ? (
        <EmptyState
          title="فعالیتی یافت نشد"
          description="فعالیت جدیدی اضافه کنید یا فیلترها را تغییر دهید."
          action={
            canEdit ? (
              <Button variant="primary" onClick={openCreate}>
                افزودن فعالیت
              </Button>
            ) : null
          }
        />
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full min-w-[960px] text-sm">
            <thead className="bg-muted/50 text-muted-foreground">
              <tr>
                <th className="px-3 py-2 text-start font-medium">کد</th>
                <th className="px-3 py-2 text-start font-medium">نام فعالیت</th>
                <th className="px-3 py-2 text-start font-medium">WBS</th>
                <th className="px-3 py-2 text-start font-medium">واحد</th>
                <th className="px-3 py-2 text-start font-medium">مقدار کل</th>
                <th className="px-3 py-2 text-start font-medium">وزن</th>
                <th className="px-3 py-2 text-start font-medium">شروع برنامه</th>
                <th className="px-3 py-2 text-start font-medium">پایان برنامه</th>
                <th className="px-3 py-2 text-start font-medium">مدت</th>
                <th className="px-3 py-2 text-start font-medium">مسئول</th>
                <th className="px-3 py-2 text-start font-medium">وضعیت</th>
                <th className="px-3 py-2 text-start font-medium">عملیات</th>
              </tr>
            </thead>
            <tbody>
              {activities.map((act) => {
                const st = STATUS_LABELS[act.status];
                const expanded = expandedId === act.activity_id;
                const detail = expanded && expandedDetail?.activity_id === act.activity_id
                  ? expandedDetail
                  : null;
                return (
                  <Fragment key={act.activity_id}>
                    <tr
                      className={cn(
                        "border-t border-border hover:bg-muted/30 cursor-pointer",
                        isFetching && "opacity-70",
                      )}
                      onClick={() => setExpandedId(expanded ? null : act.activity_id)}
                    >
                      <td className="px-3 py-2">
                        <button
                          type="button"
                          className="font-mono text-primary hover:underline"
                          onClick={(e) => { e.stopPropagation(); void openEdit(act); }}
                        >
                          {act.activity_code}
                        </button>
                      </td>
                      <td className="px-3 py-2 max-w-[180px] truncate">{act.activity_name}</td>
                      <td className="px-3 py-2 max-w-[120px] truncate text-muted-foreground">
                        {act.wbs_code} {act.wbs_name}
                      </td>
                      <td className="px-3 py-2">{act.unit_name ?? "—"}</td>
                      <td className="px-3 py-2">{act.total_quantity ?? "—"}</td>
                      <td className={cn("px-3 py-2", !act.weight && "text-warning-600")}>
                        {formatWeight(act.weight)}
                      </td>
                      <td className="px-3 py-2">{act.planned_start ?? "—"}</td>
                      <td className="px-3 py-2">{act.planned_finish ?? "—"}</td>
                      <td className="px-3 py-2">
                        {act.planned_duration != null ? `${act.planned_duration} روز` : "—"}
                      </td>
                      <td className="px-3 py-2">{act.responsible_full_name ?? "—"}</td>
                      <td className="px-3 py-2">
                        <span className="inline-flex items-center gap-1">
                          <Badge variant={st.variant} label={st.label} />
                          {act.is_overdue ? <Clock className="size-4 text-danger-500" aria-label="معوق" /> : null}
                        </span>
                      </td>
                      <td className="px-3 py-2" onClick={(e) => e.stopPropagation()}>
                        <div className="flex gap-1">
                          {canEdit ? (
                            <>
                              <Button variant="ghost" size="icon-sm" onClick={() => void openEdit(act)} aria-label="ویرایش">
                                <Pencil className="size-4" />
                              </Button>
                              <Button variant="ghost" size="icon-sm" onClick={() => setRelationAnchor(act)} aria-label="ارتباط">
                                <GitBranchPlus className="size-4" />
                              </Button>
                              <Button variant="ghost" size="icon-sm" onClick={() => setDeleteTarget(act)} aria-label="حذف">
                                <Trash2 className="size-4" />
                              </Button>
                            </>
                          ) : null}
                        </div>
                      </td>
                    </tr>
                    {expanded && detail ? (
                      <tr key={`${act.activity_id}-detail`} className="border-t border-border bg-muted/20">
                        <td colSpan={12} className="px-4 py-3 text-sm">
                          <div className="grid gap-3 md:grid-cols-2">
                            <div>
                              <p className="font-medium text-muted-foreground">توضیحات</p>
                              <p>{detail.description || "—"}</p>
                            </div>
                            <div>
                              <p className="font-medium text-muted-foreground">شروع/پایان واقعی</p>
                              <p>{detail.actual_start ?? "—"} / {detail.actual_finish ?? "—"}</p>
                            </div>
                            <div>
                              <p className="font-medium text-muted-foreground">پیش‌نیازها</p>
                              <ul className="list-inside list-disc">
                                {(detail.predecessors ?? []).length === 0 ? (
                                  <li className="list-none text-muted-foreground">—</li>
                                ) : (
                                  detail.predecessors!.map((p) => (
                                    <li key={p.activity_id}>
                                      {p.activity_code} → {p.activity_name} ({p.relation_type}
                                      {p.lag_days ? `, ${p.lag_days}روز` : ""})
                                    </li>
                                  ))
                                )}
                              </ul>
                            </div>
                            <div>
                              <p className="font-medium text-muted-foreground">جانشین‌ها</p>
                              <ul className="list-inside list-disc">
                                {(detail.successors ?? []).length === 0 ? (
                                  <li className="list-none text-muted-foreground">—</li>
                                ) : (
                                  detail.successors!.map((s) => (
                                    <li key={s.activity_id}>
                                      {s.activity_code} → {s.activity_name} ({s.relation_type})
                                    </li>
                                  ))
                                )}
                              </ul>
                            </div>
                          </div>
                        </td>
                      </tr>
                    ) : null}
                  </Fragment>
                );
              })}
            </tbody>
          </table>
          <div className="flex items-center justify-between border-t border-border px-3 py-2 text-sm text-muted-foreground">
            <span>صفحه {page} از {totalPages} ({totalCount} مورد)</span>
            <div className="flex gap-2">
              <Button variant="secondary" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>قبلی</Button>
              <Button variant="secondary" size="sm" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>بعدی</Button>
            </div>
          </div>
        </div>
      )}

      <ActivityDrawer
        projectId={projectId}
        isOpen={drawerOpen}
        onClose={() => { setDrawerOpen(false); setEditActivity(null); }}
        activity={editActivity}
        onSaved={() => {
          toast.success(editActivity ? "فعالیت به‌روزرسانی شد" : "فعالیت ایجاد شد");
          setDrawerOpen(false);
          setEditActivity(null);
          void qc.invalidateQueries({ queryKey: ["activities", projectId] });
        }}
        onError={(msg) => toast.error(msg)}
      />

      {relationAnchor ? (
        <AddRelationModal
          projectId={projectId}
          anchor={relationAnchor}
          isOpen={Boolean(relationAnchor)}
          onClose={() => setRelationAnchor(null)}
          onSuccess={() => {
            toast.success("ارتباط ثبت شد");
            void qc.invalidateQueries({ queryKey: ["activities", projectId] });
          }}
        />
      ) : null}

      <Modal
        open={deleteTarget !== null}
        onOpenChange={(open) => { if (!open) setDeleteTarget(null); }}
        title="حذف فعالیت"
        idBase="deleteActivity"
      >
        <p className="text-sm">آیا از حذف «{deleteTarget?.activity_name}» مطمئن هستید؟</p>
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setDeleteTarget(null)}>لغو</Button>
          <Button
            variant="danger"
            disabled={deleteMutation.isPending}
            onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget.activity_id)}
          >
            حذف
          </Button>
        </div>
      </Modal>

      <Modal
        open={weightModalOpen}
        onOpenChange={setWeightModalOpen}
        title="وزن‌سنجی فعالیت‌ها"
        idBase="activityWeightSummary"
      >
        {weightSummary ? (
          <div className="space-y-3 text-sm">
            <p>مجموع وزن: <strong>{Math.round(weightSummary.total_weight * 1000) / 10}٪</strong></p>
            <p>باقی‌مانده: <strong>{Math.round(Math.abs(weightSummary.remaining) * 1000) / 10}٪</strong></p>
            <p>متعادل: {weightSummary.is_balanced ? "بله" : "خیر"}</p>
            {weightSummary.warning ? (
              <p className="text-warning-700 dark:text-warning-400">{weightSummary.warning}</p>
            ) : null}
          </div>
        ) : (
          <LoadingSkeleton rows={3} />
        )}
      </Modal>
    </div>
  );
}
