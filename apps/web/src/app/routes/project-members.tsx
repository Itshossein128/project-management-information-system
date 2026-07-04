import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import {
  fetchMembers,
  fetchRoles,
  updateMember,
  type ProjectMember,
  type Role,
} from "@/app/lib/api/members";
import { PATHS } from "@/app/routeVars";
import { AddMemberDrawer } from "@/components/projects/add-member-drawer";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/sprint-button";
import { DataTable } from "@/components/ui/data-table";
import { Modal } from "@/components/overlay/modal";
import { Breadcrumb, PageHeader } from "@/components/layout/page-header";
import { useToast } from "@/components/ui/toast";

export default function ProjectMembersPage() {
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
      toast.success("عضو غیرفعال شد");
      setDeactivateTarget(null);
      void qc.invalidateQueries({ queryKey: ["members", projectId] });
    },
    onError: () => toast.error("خطا در غیرفعال‌سازی"),
  });

  const columns = [
    {
      key: "name",
      label: "نام",
      render: (row: ProjectMember) => (
        <span className={row.status === "inactive" ? "line-through opacity-60" : ""}>
          {row.full_name}
        </span>
      ),
    },
    {
      key: "roles",
      label: "نقش‌ها",
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
      label: "وضعیت",
      render: (row: ProjectMember) => (
        <Badge
          variant={row.status === "active" ? "success" : "neutral"}
          label={row.status === "active" ? "فعال" : "غیرفعال"}
        />
      ),
    },
    { key: "joined_at", label: "تاریخ عضویت", render: (r: ProjectMember) => r.joined_at?.slice(0, 10) ?? "—" },
    { key: "last_login", label: "آخرین ورود", render: (r: ProjectMember) => r.last_login?.slice(0, 10) ?? "—" },
    {
      key: "actions",
      label: "عملیات",
      render: (row: ProjectMember) =>
        row.user_id ? (
          <div className="flex gap-1">
            <Button variant="ghost" size="sm" onClick={() => { setEditMember(row); setDrawerOpen(true); }}>
              ویرایش
            </Button>
            {row.status === "active" ? (
              <Button variant="ghost" size="sm" onClick={() => setDeactivateTarget(row)}>
                غیرفعال
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
          { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
          { label: "اعضا" },
        ]}
      />
      <PageHeader
        title="مدیریت اعضا"
        actions={
          <Button variant="primary" onClick={() => { setEditMember(null); setDrawerOpen(true); }}>
            افزودن عضو
          </Button>
        }
      />

      <DataTable
        columns={columns}
        data={members}
        loading={isLoading}
        rowKey={(r) => r.user_id ?? r.invited_email ?? r.full_name}
        emptyMessage="عضوی ثبت نشده است"
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
        title="غیرفعال‌سازی عضو"
        idBase="deactivateMember"
      >
        <p className="mb-4 text-sm">آیا از غیرفعال کردن {deactivateTarget?.full_name} مطمئن هستید؟</p>
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setDeactivateTarget(null)}>انصراف</Button>
          <Button
            variant="danger"
            loading={deactivateMutation.isPending}
            onClick={() => deactivateTarget?.user_id && deactivateMutation.mutate(deactivateTarget.user_id)}
          >
            غیرفعال‌سازی
          </Button>
        </div>
      </Modal>
    </main>
  );
}
