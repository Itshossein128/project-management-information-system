import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import { useTranslation } from "react-i18next";
import {
  fetchMembers,
  fetchRoles,
  updateMember,
  type ProjectMember,
  type Role,
} from "@/app/lib/api/members";
import { formatDisplayDate } from "@/app/lib/jalali-utils";
import { PATHS } from "@/app/routeVars";
import { AddMemberDrawer } from "@/components/projects/add-member-drawer";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/sprint-button";
import { DataTable } from "@/components/ui/data-table";
import { Modal } from "@/components/overlay/modal";
import { Breadcrumb, PageHeader } from "@/components/layout/page-header";
import { useToast } from "@/components/ui/toast";

export default function ProjectMembersPage() {
  const { t } = useTranslation();
  const { projectId = "" } = useParams();
  const toast = useToast();
  const qc = useQueryClient();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editMember, setEditMember] = useState<ProjectMember | null>(null);
  const [deactivateTarget, setDeactivateTarget] = useState<ProjectMember | null>(null);

  const { data: members = [], isLoading } = useQuery({
    queryKey: ["members", projectId],
    queryFn: () => fetchMembers(projectId),
  });

  const { data: roles = [] } = useQuery({ queryKey: ["roles"], queryFn: fetchRoles });

  const deactivateMutation = useMutation({
    mutationFn: (userId: string) => updateMember(projectId, userId, { status: "inactive" }),
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
        <span className={row.status === "inactive" ? "line-through opacity-60" : ""}>
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
          <div className="flex flex-wrap gap-1">
            {shown.map((r) => (
              <Badge key={r} variant="info" label={r} />
            ))}
            {extra > 0 ? <Badge variant="neutral" label={`+${extra}`} /> : null}
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
          label={row.status === "active" ? t("projectMembers.active") : t("projectMembers.inactive")}
        />
      ),
    },
    {
      key: "joined_at",
      label: t("projectMembers.joinedAt"),
      render: (r: ProjectMember) => formatDisplayDate(r.joined_at?.slice(0, 10)),
    },
    {
      key: "last_login",
      label: t("projectMembers.lastLogin"),
      render: (r: ProjectMember) => formatDisplayDate(r.last_login?.slice(0, 10)),
    },
    {
      key: "actions",
      label: t("projectMembers.actions"),
      render: (row: ProjectMember) =>
        row.user_id ? (
          <div className="flex gap-1">
            <Button variant="ghost" size="sm" onClick={() => { setEditMember(row); setDrawerOpen(true); }}>
              {t("projectMembers.edit")}
            </Button>
            {row.status === "active" ? (
              <Button variant="ghost" size="sm" onClick={() => setDeactivateTarget(row)}>
                {t("projectMembers.deactivate")}
              </Button>
            ) : null}
          </div>
        ) : null,
    },
  ];

  return (
    <main className="page-main page-shell mx-auto max-w-6xl px-4 py-8">
      <Breadcrumb
        items={[
          { label: t("project.title"), href: `/${PATHS.PROJECT}` },
          { label: t("projectMembers.breadcrumb") },
        ]}
      />
      <PageHeader
        title={t("projectMembers.title")}
        actions={
          <Button variant="primary" onClick={() => { setEditMember(null); setDrawerOpen(true); }}>
            {t("projectMembers.add")}
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={members}
        loading={isLoading}
        rowKey={(r) => r.user_id ?? r.invited_email ?? r.full_name}
        emptyMessage={t("projectMembers.empty")}
      />

      <AddMemberDrawer
        projectId={projectId}
        isOpen={drawerOpen}
        onClose={() => { setDrawerOpen(false); setEditMember(null); }}
        editMember={editMember}
        roles={roles as Role[]}
      />

      <Modal
        open={Boolean(deactivateTarget)}
        onOpenChange={(o) => !o && setDeactivateTarget(null)}
        title={t("projectMembers.deactivateTitle")}
        idBase="deactivateMember"
      >
        <p className="mb-4 text-sm">
          {t("projectMembers.deactivateConfirm", { name: deactivateTarget?.full_name })}
        </p>
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setDeactivateTarget(null)}>{t("common.cancel")}</Button>
          <Button
            variant="danger"
            loading={deactivateMutation.isPending}
            onClick={() => deactivateTarget?.user_id && deactivateMutation.mutate(deactivateTarget.user_id)}
          >
            {t("projectMembers.deactivate")}
          </Button>
        </div>
      </Modal>
    </main>
  );
}
