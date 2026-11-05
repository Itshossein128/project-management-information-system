import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import { useTranslation } from "react-i18next";
import { ApiRequestError } from "@/app/lib/api-client";
import {
  createLocalRole,
  deleteLocalRole,
  fetchAccessChanges,
  fetchAssignableRoles,
  fetchLocalRoleImpact,
  fetchMembers,
  setLocalRolePermissions,
  updateLocalRole,
  updateMember,
  type ProjectMember,
  type Role,
} from "@/app/lib/api/members";
import { formatDisplayDate } from "@/app/lib/jalali-utils";
import { fetchPermissionCatalog } from "@/app/lib/api/roles";
import { formatPermissionLabel } from "@/app/lib/permission-labels";
import { formatRoleLabel } from "@/app/lib/role-labels";
import { PATHS } from "@/app/routeVars";
import { AddMemberDrawer } from "@/components/projects/add-member-drawer";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/sprint-button";
import { DataTable } from "@/components/ui/data-table";
import { Modal } from "@/components/overlay/modal";
import { EmptyState } from "@/components/layout/empty-state";
import { Breadcrumb, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { useToast } from "@/components/ui/toast";
import { useActiveProjectPermission } from "@/app/contexts/project-context";

export default function ProjectMembersPage() {
  const { t } = useTranslation();
  const { projectId = "" } = useParams();
  const { has } = useActiveProjectPermission(projectId);
  const canManageMembers = has("manage_members");
  const toast = useToast();
  const qc = useQueryClient();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editMember, setEditMember] = useState<ProjectMember | null>(null);
  const [deactivateTarget, setDeactivateTarget] =
    useState<ProjectMember | null>(null);
  const [localRoleName, setLocalRoleName] = useState("");

  const { data: members = [], isLoading, isError, refetch } = useQuery({
    queryKey: ["members", projectId],
    queryFn: () => fetchMembers(projectId),
  });

  const { data: roles = [] } = useQuery({
    queryKey: ["roles", projectId],
    queryFn: () => fetchAssignableRoles(projectId),
  });
  const { data: catalog = [] } = useQuery({
    queryKey: ["permission-catalog"],
    queryFn: fetchPermissionCatalog,
  });
  const { data: changes = [] } = useQuery({
    queryKey: ["access-changes", projectId],
    queryFn: () => fetchAccessChanges(projectId),
    enabled: Boolean(projectId),
  });
  const createRoleMutation = useMutation({
    mutationFn: () => createLocalRole(projectId, { role_name: localRoleName.trim() }),
    onSuccess: () => {
      toast.success(t("projectMembers.localRoleCreated"));
      setLocalRoleName("");
      void qc.invalidateQueries({ queryKey: ["roles", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const deactivateMutation = useMutation({
    mutationFn: (userId: string) =>
      updateMember(projectId, userId, { status: "inactive" }),
    onSuccess: () => {
      toast.success(t("projectMembers.deactivateSuccess"));
      setDeactivateTarget(null);
      void qc.invalidateQueries({ queryKey: ["members", projectId] });
    },
    onError: () => toast.error(t("projectMembers.deactivateError")),
  });

  const columns = [
    {
      key: "name",
      label: t("projectMembers.name"),
      render: (row: ProjectMember) => (
        <span
          className={row.status === "inactive" ? "line-through opacity-60" : ""}
        >
          {row.full_name}
        </span>
      ),
    },
    {
      key: "roles",
      label: t("projectMembers.roles"),
      render: (row: ProjectMember) => {
        const shown = row.roles.slice(0, 2);
        const extra = row.roles.length - 2;
        return (
          <div className='flex flex-wrap gap-1'>
            {shown.map((r) => (
              <Badge key={r} variant='info' label={formatRoleLabel(r, t)} />
            ))}
            {extra > 0 ? <Badge variant='neutral' label={`+${extra}`} /> : null}
          </div>
        );
      },
    },
    {
      key: "status",
      label: t("projectMembers.status"),
      render: (row: ProjectMember) => (
        <Badge
          variant={row.status === "active" ? "success" : "neutral"}
          label={
            row.status === "active"
              ? t("projectMembers.active")
              : t("projectMembers.inactive")
          }
        />
      ),
    },
    {
      key: "joined_at",
      label: t("projectMembers.joinedAt"),
      render: (r: ProjectMember) =>
        formatDisplayDate(r.joined_at?.slice(0, 10)),
    },
    {
      key: "last_login",
      label: t("projectMembers.lastLogin"),
      render: (r: ProjectMember) =>
        formatDisplayDate(r.last_login?.slice(0, 10)),
    },
    {
      key: "actions",
      label: t("projectMembers.actions"),
      render: (row: ProjectMember) =>
        canManageMembers && row.user_id ? (
          <div className='flex gap-1'>
            <Button
              variant='ghost'
              size='sm'
              onClick={() => {
                setEditMember(row);
                setDrawerOpen(true);
              }}
            >
              {t("projectMembers.edit")}
            </Button>
            {row.status === "active" ? (
              <Button
                variant='ghost'
                size='sm'
                onClick={() => setDeactivateTarget(row)}
              >
                {t("projectMembers.deactivate")}
              </Button>
            ) : null}
          </div>
        ) : null,
    },
  ];

  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <Breadcrumb
        items={[
          { label: t("project.title"), href: `/${PATHS.PROJECT}` },
          { label: t("projectMembers.breadcrumb") },
        ]}
      />
      <PageHeader
        title={t("projectMembers.title")}
        actions={canManageMembers ? (
          <Button
            variant='primary'
            onClick={() => {
              setEditMember(null);
              setDrawerOpen(true);
            }}
          >
            {t("projectMembers.add")}
          </Button>
        ) : undefined}
      />

      {canManageMembers || changes.length > 0 ? <section className="mb-6 rounded-lg border border-border p-4">
        {canManageMembers ? <h2 className="mb-2 text-sm font-medium">{t("projectMembers.localRole")}</h2> : null}
        {canManageMembers ? <form
          className="flex flex-wrap gap-2"
          onSubmit={(event) => {
            event.preventDefault();
            if (localRoleName.trim()) createRoleMutation.mutate();
          }}
        >
          <input
            className="rounded border border-border px-3 py-2 text-sm"
            value={localRoleName}
            placeholder={t("projectMembers.localRolePlaceholder")}
            onChange={(event) => setLocalRoleName(event.target.value)}
          />
          <Button type="submit" variant="secondary" loading={createRoleMutation.isPending}>
            {t("projectMembers.createLocalRole")}
          </Button>
        </form> : null}
        <ul className="mt-3 space-y-1 text-sm">
          {roles.filter((role) => role.project_id).map((role) => (
            <li key={role.id} className="rounded border border-border px-3 py-2">
              <div className="flex items-center justify-between gap-2">
                <span>{formatRoleLabel(role.role_name, t)}</span>
                {canManageMembers ? (
                  <Button
                    variant="ghost"
                    onClick={async () => {
                      try {
                        const impact = await fetchLocalRoleImpact(projectId, role.id);
                        if (impact.assignment_count > 0) {
                          toast.error(t("roles.deleteBlocked", { count: impact.assignment_count }));
                          return;
                        }
                        await deleteLocalRole(projectId, role.id);
                        toast.success(t("roles.deleteSuccess"));
                        void qc.invalidateQueries({ queryKey: ["roles", projectId] });
                      } catch (error) {
                        const count =
                          error instanceof ApiRequestError &&
                          error.code === "role_in_use" &&
                          typeof error.details === "object" &&
                          error.details !== null &&
                          "assignment_count" in error.details
                            ? Number((error.details as { assignment_count?: number }).assignment_count)
                            : null;
                        toast.error(
                          count !== null && Number.isFinite(count)
                            ? t("roles.deleteBlocked", { count })
                            : error instanceof Error
                              ? error.message
                              : t("projectMembers.deactivateError"),
                        );
                      }
                    }}
                  >
                    {t("projectMembers.deleteLocalRole")}
                  </Button>
                ) : null}
              </div>
              {canManageMembers ? (
                <details className="mt-2">
                  <summary className="cursor-pointer text-xs text-primary">{t("projectMembers.advancedPermissions")}</summary>
                  <form
                    className="mt-2 max-h-40 space-y-1 overflow-auto"
                    onSubmit={async (event) => {
                      event.preventDefault();
                      const form = event.currentTarget;
                      const selected = [...form.querySelectorAll<HTMLInputElement>("input[type=checkbox]:checked")].map(
                        (input) => input.value,
                      );
                      const nextName = form.querySelector<HTMLInputElement>("input[name=role_name]")?.value.trim() ?? "";
                      const nextDescription = form.querySelector<HTMLInputElement>("input[name=description]")?.value.trim() ?? "";
                      if (!nextName) return;
                      try {
                        const impact = await fetchLocalRoleImpact(projectId, role.id);
                        const permissionsChanged =
                          selected.length !== role.permissions.length ||
                          selected.some((code) => !role.permissions.includes(code));
                        if (permissionsChanged && impact.assignment_count > 0) {
                          const proceed = window.confirm(
                            t("roles.impactConfirm", { count: impact.assignment_count }),
                          );
                          if (!proceed) return;
                        }
                        if (nextName !== role.role_name || nextDescription !== (role.description ?? "")) {
                          await updateLocalRole(projectId, role.id, {
                            role_name: nextName,
                            description: nextDescription,
                          });
                        }
                        await setLocalRolePermissions(projectId, role.id, selected);
                        toast.success(t("roles.updateSuccess"));
                        void qc.invalidateQueries({ queryKey: ["roles", projectId] });
                        void qc.invalidateQueries({ queryKey: ["access-changes", projectId] });
                      } catch (error) {
                        toast.error(error instanceof Error ? error.message : t("projectMembers.deactivateError"));
                      }
                    }}
                  >
                    <input
                      name="role_name"
                      className="w-full rounded border border-border px-2 py-1 text-xs"
                      defaultValue={role.role_name}
                      aria-label={t("projectMembers.localRolePlaceholder")}
                    />
                    <input
                      name="description"
                      className="w-full rounded border border-border px-2 py-1 text-xs"
                      defaultValue={role.description ?? ""}
                      aria-label={t("roles.description")}
                    />
                    {catalog.map((item) => (
                      <label key={item.codename} className="flex items-center gap-2 text-xs">
                        <input
                          type="checkbox"
                          value={item.codename}
                          defaultChecked={role.permissions.includes(item.codename)}
                        />
                        <span>{formatPermissionLabel(item.codename, item.label, t)}</span>
                      </label>
                    ))}
                    <Button type="submit" variant="secondary">{t("roles.savePermissions")}</Button>
                  </form>
                </details>
              ) : null}
            </li>
          ))}
        </ul>
        {changes.length > 0 ? (
          <div className="mt-4">
            <h3 className="mb-1 text-sm font-medium">{t("projectMembers.recentChanges")}</h3>
            <ul className="space-y-1 text-xs text-muted-foreground">
              {changes.slice(0, 5).map((change) => (
                <li key={change.id}>
                  {change.created_at} — {change.actor_name || "—"} — {change.subject_name || change.role_name} — {change.action}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </section> : null}

      {isError ? (
        <QueryErrorState onRetry={() => void refetch()} />
      ) : !isLoading && members.length === 0 ? (
        <EmptyState
          title={t("projectMembers.empty")}
          action={canManageMembers ? (
            <Button
              variant="primary"
              onClick={() => {
                setEditMember(null);
                setDrawerOpen(true);
              }}
            >
              {t("projectMembers.add")}
            </Button>
          ) : undefined}
        />
      ) : (
        <DataTable
          columns={canManageMembers ? columns : columns.filter((column) => column.key !== "actions")}
          data={members}
          loading={isLoading}
          rowKey={(r) => r.user_id ?? r.invited_email ?? r.full_name}
          emptyMessage={t("projectMembers.empty")}
        />
      )}

      <AddMemberDrawer
        projectId={projectId}
        isOpen={drawerOpen && canManageMembers}
        onClose={() => {
          setDrawerOpen(false);
          setEditMember(null);
        }}
        editMember={editMember}
        roles={roles as Role[]}
      />

      <Modal
        open={canManageMembers && Boolean(deactivateTarget)}
        onOpenChange={(o) => !o && setDeactivateTarget(null)}
        title={t("projectMembers.deactivateTitle")}
        idBase='deactivateMember'
      >
        <p className='mb-4 text-sm'>
          {t("projectMembers.deactivateConfirm", {
            name: deactivateTarget?.full_name,
          })}
        </p>
        <div className='flex justify-end gap-2'>
          <Button variant='ghost' onClick={() => setDeactivateTarget(null)}>
            {t("common.cancel")}
          </Button>
          <Button
            variant='danger'
            loading={deactivateMutation.isPending}
            onClick={() =>
              deactivateTarget?.user_id &&
              deactivateMutation.mutate(deactivateTarget.user_id)
            }
          >
            {t("projectMembers.deactivate")}
          </Button>
        </div>
      </Modal>
    </main>
  );
}
