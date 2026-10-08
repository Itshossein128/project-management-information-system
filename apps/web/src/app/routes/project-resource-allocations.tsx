import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  approveCapacityException,
  CapacityConflictError,
  createCapacityException,
  createResourceAllocation,
  deleteResourceAllocation,
  fetchCapacityExceptions,
  fetchPersonDossier,
  fetchResourceAllocations,
  listResults,
  rejectCapacityException,
  submitCapacityException,
  updatePersonDossier,
  type CapacityConflict,
  type ResourceAllocation,
} from "@/app/lib/api/hr-capacity";
import { fetchActivities } from "@/app/lib/api/activities";
import {
  asList,
  fetchOrganizationUnits,
} from "@/app/lib/api/central-data";
import { fetchMembers } from "@/app/lib/api/members";
import { fetchWBSFlat } from "@/app/lib/api/wbs";
import { PATHS } from "@/app/routeVars";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { EmptyState } from "@/components/layout/empty-state";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Button } from "@/components/ui/sprint-button";
import { Drawer } from "@/components/ui/drawer";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import { AllocationFormPanel } from "@/components/hr/AllocationFormPanel";
import { CapacityExceptionPanel } from "@/components/hr/CapacityExceptionPanel";
import { PersonDossierPanel } from "@/components/hr/PersonDossierPanel";
import { LaborRatesPanel } from "@/components/hr/LaborRatesPanel";

function Content() {
  const { t } = useTranslation();
  const { projectId } = useProject();
  const { has } = usePermission(projectId);
  const canEdit = has("edit_hr");
  const canApprove = has("approve_hr");
  const canViewWage = has("view_wage");
  const canEditWage = has("edit_wage");
  const toast = useToast();
  const qc = useQueryClient();

  const [allocOpen, setAllocOpen] = useState(false);
  const [dossierUserId, setDossierUserId] = useState<string | null>(null);
  const [conflict, setConflict] = useState<CapacityConflict | null>(null);
  const [pendingAlloc, setPendingAlloc] = useState<Record<string, unknown> | null>(null);
  const [exceptionReason, setExceptionReason] = useState("");
  const [pendingExceptionId, setPendingExceptionId] = useState<string | null>(null);

  const allocationsQ = useQuery({
    queryKey: ["resource-allocations", projectId],
    queryFn: () => fetchResourceAllocations(projectId),
  });
  const exceptionsQ = useQuery({
    queryKey: ["capacity-exceptions", projectId],
    queryFn: () => fetchCapacityExceptions(projectId),
  });
  const membersQ = useQuery({
    queryKey: ["members", projectId],
    queryFn: () => fetchMembers(projectId),
  });
  const wbsQ = useQuery({
    queryKey: ["wbs-flat", projectId],
    queryFn: () => fetchWBSFlat(projectId),
  });
  const activitiesQ = useQuery({
    queryKey: ["activities", projectId],
    queryFn: () => fetchActivities(projectId, { per_page: 200 }),
  });
  const orgUnitsQ = useQuery({
    queryKey: ["organization-units"],
    queryFn: fetchOrganizationUnits,
  });

  const rows = listResults(allocationsQ.data);
  const exceptions = listResults(exceptionsQ.data);
  const members = membersQ.data ?? [];
  const wbsNodes = wbsQ.data ?? [];
  const activities = activitiesQ.data?.results ?? [];
  const orgUnits = asList(orgUnitsQ.data ?? []).map((u) => ({
    id: u.id,
    name: u.name,
  }));
  const memberName = useMemo(() => {
    const map = new Map<string, string>();
    for (const m of members) {
      if (m.user_id) map.set(m.user_id, m.full_name || m.email || m.user_id);
    }
    return map;
  }, [members]);
  const wbsLabel = useMemo(() => {
    const map = new Map<string, string>();
    for (const n of wbsNodes) map.set(n.wbs_id, `${n.wbs_code} ${n.wbs_name}`);
    return map;
  }, [wbsNodes]);
  const activityLabel = useMemo(() => {
    const map = new Map<string, string>();
    for (const a of activities) map.set(a.activity_id, `${a.activity_code} ${a.activity_name}`);
    return map;
  }, [activities]);

  const createMut = useMutation({
    mutationFn: (body: Record<string, unknown>) => createResourceAllocation(projectId, body),
    onSuccess: () => {
      toast.success(t("hr.capacity.allocationSaved"));
      setAllocOpen(false);
      setConflict(null);
      setPendingAlloc(null);
      setPendingExceptionId(null);
      setExceptionReason("");
      void qc.invalidateQueries({ queryKey: ["resource-allocations", projectId] });
    },
    onError: (err: Error) => {
      if (err instanceof CapacityConflictError) {
        setConflict(err.conflict);
        toast.error(t("hr.capacity.capacityConflict"));
        return;
      }
      toast.error(err.message);
    },
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => deleteResourceAllocation(projectId, id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["resource-allocations", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const submitExceptionMut = useMutation({
    mutationFn: async () => {
      if (!pendingAlloc) throw new Error("No pending allocation");
      const reason = exceptionReason.trim();
      if (!reason) throw new Error(t("hr.capacity.reasonRequired"));
      return createCapacityException(projectId, {
        person_id: pendingAlloc.person_id,
        start_date: pendingAlloc.start_date,
        end_date: pendingAlloc.end_date,
        requested_capacity_percent:
          pendingAlloc.capacity_percent ?? pendingAlloc.capacity_hours,
        reason,
        submit: true,
      });
    },
    onSuccess: (ex) => {
      setPendingExceptionId(ex.id);
      toast.success(t("hr.capacity.exceptionSubmitted"));
      void qc.invalidateQueries({ queryKey: ["capacity-exceptions", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (allocationsQ.isLoading) return <LoadingSkeleton rows={6} />;
  if (allocationsQ.isError) {
    return <QueryErrorState onRetry={() => void allocationsQ.refetch()} />;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2">
        {canEdit && (
          <Button size="sm" onClick={() => setAllocOpen(true)}>
            {t("hr.capacity.newAllocation")}
          </Button>
        )}
      </div>

      {conflict && (
        <div
          className="rounded-md border border-amber-500/40 bg-amber-500/10 p-3 text-sm space-y-2"
          role="alert"
        >
          <p className="font-medium">{t("hr.capacity.capacityConflict")}</p>
          <p>
            {t("hr.capacity.committed")}: {conflict.committed} — {t("hr.capacity.available")}:{" "}
            {conflict.available} — {t("hr.capacity.requested")}: {conflict.requested}
          </p>
          {canEdit && (
            <>
              <label className="block">
                <span className="mb-1 block">{t("hr.capacity.exceptionReason")}</span>
                <textarea
                  className="w-full rounded-md border bg-background px-2 py-1.5"
                  rows={3}
                  value={exceptionReason}
                  onChange={(e) => setExceptionReason(e.target.value)}
                />
              </label>
              <div className="flex flex-wrap gap-2">
                <Button
                  size="sm"
                  variant="secondary"
                  disabled={submitExceptionMut.isPending}
                  onClick={() => submitExceptionMut.mutate()}
                >
                  {t("hr.capacity.submitException")}
                </Button>
                {pendingExceptionId && canApprove === false && (
                  <span className="text-muted-foreground self-center">
                    {t("hr.capacity.awaitingApproval")}
                  </span>
                )}
                {pendingExceptionId && (
                  <Button
                    size="sm"
                    onClick={() =>
                      createMut.mutate({
                        ...pendingAlloc!,
                        capacity_exception_id: pendingExceptionId,
                      })
                    }
                  >
                    {t("hr.capacity.retryWithException")}
                  </Button>
                )}
              </div>
            </>
          )}
        </div>
      )}

      {rows.length === 0 ? (
        <EmptyState
          title={t("hr.capacity.emptyTitle")}
          description={t("hr.capacity.emptyDescription")}
          action={
            canEdit ? (
              <Button size="sm" onClick={() => setAllocOpen(true)}>
                {t("hr.capacity.newAllocation")}
              </Button>
            ) : undefined
          }
        />
      ) : (
        <div className="overflow-x-auto rounded-md border">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/40 text-start">
                <th className="p-2 text-start">{t("hr.capacity.person")}</th>
                <th className="p-2 text-start">{t("hr.capacity.role")}</th>
                <th className="p-2 text-start">{t("hr.capacity.scope")}</th>
                <th className="p-2 text-start">{t("hr.capacity.dates")}</th>
                <th className="p-2 text-start">{t("hr.capacity.capacity")}</th>
                <th className="p-2 text-start">{t("hr.capacity.status")}</th>
                <th className="p-2" />
              </tr>
            </thead>
            <tbody>
              {rows.map((row: ResourceAllocation) => (
                <tr key={row.id} className="border-b">
                  <td className="p-2">
                    <button
                      type="button"
                      className="text-primary underline-offset-2 hover:underline"
                      onClick={() => setDossierUserId(row.person_id)}
                    >
                      {memberName.get(row.person_id) ?? row.person_id.slice(0, 8)}
                    </button>
                    {row.has_capacity_exception ? (
                      <span className="ms-2 inline-block">
                        <Badge variant="warning" label={t("hr.capacity.exceptionFlag")} />
                      </span>
                    ) : null}
                  </td>
                  <td className="p-2">{row.role}</td>
                  <td className="p-2">
                    {row.wbs_id ? (
                      <Link
                        className="underline-offset-2 hover:underline"
                        to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_WBS}`}
                      >
                        {wbsLabel.get(row.wbs_id) ?? row.wbs_id.slice(0, 8)}
                      </Link>
                    ) : (
                      "—"
                    )}
                    {row.activity_id ? (
                      <>
                        {" / "}
                        <Link
                          className="underline-offset-2 hover:underline"
                          to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_ACTIVITIES}`}
                        >
                          {activityLabel.get(row.activity_id) ?? row.activity_id.slice(0, 8)}
                        </Link>
                      </>
                    ) : null}
                  </td>
                  <td className="p-2">
                    {row.start_date} → {row.end_date}
                  </td>
                  <td className="p-2">{row.capacity_percent}%</td>
                  <td className="p-2">{row.status}</td>
                  <td className="p-2 text-end">
                    {canEdit && (
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => deleteMut.mutate(row.id)}
                      >
                        {t("common.delete")}
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <CapacityExceptionPanel
        projectId={projectId}
        exceptions={exceptions}
        canApprove={canApprove}
        canEdit={canEdit}
        onSubmit={(id) =>
          submitCapacityException(projectId, id).then(() =>
            qc.invalidateQueries({ queryKey: ["capacity-exceptions", projectId] }),
          )
        }
        onApprove={async (id) => {
          const ex = await approveCapacityException(projectId, id);
          setPendingExceptionId(ex.id);
          void qc.invalidateQueries({ queryKey: ["capacity-exceptions", projectId] });
          if (pendingAlloc) {
            toast.success(t("hr.capacity.exceptionApprovedRetry"));
          }
        }}
        onReject={(id) =>
          rejectCapacityException(projectId, id).then(() =>
            qc.invalidateQueries({ queryKey: ["capacity-exceptions", projectId] }),
          )
        }
      />

      <LaborRatesPanel
        projectId={projectId}
        members={members}
        canViewWage={canViewWage}
        canEditWage={canEditWage}
      />

      <Drawer
        isOpen={allocOpen}
        onClose={() => setAllocOpen(false)}
        title={t("hr.capacity.newAllocation")}
      >
        <AllocationFormPanel
          members={members}
          wbsNodes={wbsNodes}
          activities={activities}
          pending={createMut.isPending}
          onSubmit={(body) => {
            setPendingAlloc(body);
            setConflict(null);
            setPendingExceptionId(null);
            createMut.mutate(body);
          }}
        />
      </Drawer>

      <Drawer
        isOpen={!!dossierUserId}
        onClose={() => setDossierUserId(null)}
        title={t("hr.capacity.dossier")}
      >
        {dossierUserId ? (
          <PersonDossierPanel
            projectId={projectId}
            userId={dossierUserId}
            canEdit={canEdit}
            members={members}
            orgUnits={orgUnits}
            fetchDossier={fetchPersonDossier}
            updateDossier={updatePersonDossier}
          />
        ) : null}
      </Drawer>
    </div>
  );
}

export default function ProjectResourceAllocationsPage() {
  const { t } = useTranslation();
  const { projectId = "" } = useParams();

  return (
    <ProjectProvider projectId={projectId}>
      <div className="space-y-4 p-4 md:p-6">
        <Breadcrumb
          items={[
            { label: t("nav.projectResources") },
            { label: t("nav.projectAllocations") },
          ]}
        />
        <PageHeader
          title={t("hr.capacity.title")}
          subtitle={t("hr.capacity.description")}
        />
        <Content />
      </div>
    </ProjectProvider>
  );
}
