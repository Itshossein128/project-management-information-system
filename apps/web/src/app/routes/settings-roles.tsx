import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Lock, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  createProjectRole,
  deleteProjectRole,
  fetchPermissionCatalog,
  fetchProjectRoles,
  groupPermissionsByModule,
  PERMISSION_MODULE_ORDER,
  setProjectRolePermissions,
  type ProjectRole,
} from "@/app/lib/api/roles";
import { Breadcrumb, PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/sprint-button";
import { Input } from "@/components/form";
import { Label } from "@/components/ui/label";
import { Modal } from "@/components/overlay/modal";
import { useToast } from "@/components/ui/toast";
import { useAuth } from "@/app/contexts/auth-context";
import { ROLES } from "@/config/roles";

export default function SettingsRolesPage() {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const { hasRole } = useAuth();
  const canManage = hasRole(ROLES.ADMIN) || hasRole(ROLES.HR);

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [draftPermissions, setDraftPermissions] = useState<Set<string>>(new Set());
  const [createOpen, setCreateOpen] = useState(false);
  const [roleName, setRoleName] = useState("");
  const [description, setDescription] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<ProjectRole | null>(null);

  const { data: roles = [], isLoading: rolesLoading } = useQuery({
    queryKey: ["project-roles"],
    queryFn: fetchProjectRoles,
  });

  const { data: catalog = [] } = useQuery({
    queryKey: ["permission-catalog"],
    queryFn: fetchPermissionCatalog,
  });

  const selectedRole = roles.find((r) => r.id === selectedId) ?? null;
  const grouped = useMemo(() => groupPermissionsByModule(catalog), [catalog]);

  const selectRole = (role: ProjectRole) => {
    setSelectedId(role.id);
    setDraftPermissions(new Set(role.permissions));
  };

  const togglePermission = (codename: string) => {
    if (selectedRole?.is_system) return;
    setDraftPermissions((prev) => {
      const next = new Set(prev);
      if (next.has(codename)) next.delete(codename);
      else next.add(codename);
      return next;
    });
  };

  const createMutation = useMutation({
    mutationFn: () =>
      createProjectRole({
        role_name: roleName.trim(),
        description: description.trim(),
        permissions: [],
      }),
    onSuccess: (role) => {
      toast.success(t("roles.createSuccess"));
      setCreateOpen(false);
      setRoleName("");
      setDescription("");
      void qc.invalidateQueries({ queryKey: ["project-roles"] });
      selectRole(role);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const savePermissionsMutation = useMutation({
    mutationFn: () => setProjectRolePermissions(selectedId!, [...draftPermissions]),
    onSuccess: () => {
      toast.success(t("roles.updateSuccess"));
      void qc.invalidateQueries({ queryKey: ["project-roles"] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteProjectRole(id),
    onSuccess: () => {
      toast.success(t("roles.deleteSuccess"));
      setDeleteTarget(null);
      setSelectedId(null);
      void qc.invalidateQueries({ queryKey: ["project-roles"] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (!canManage) {
    return (
      <main className="page-main page-shell mx-auto max-w-4xl px-4 py-8">
        <p className="text-muted-foreground">{t("hrUsers.forbiddenBody")}</p>
      </main>
    );
  }

  return (
    <main className="page-main page-shell mx-auto max-w-6xl px-4 py-8">
      <Breadcrumb
        items={[
          { label: t("settings.title") },
          { label: t("roles.breadcrumb") },
        ]}
      />
      <PageHeader
        title={t("roles.title")}
        subtitle={t("roles.subtitle")}
        actions={
          <Button variant="primary" onClick={() => setCreateOpen(true)}>
            {t("roles.create")}
          </Button>
        }
      />

      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        <aside className="rounded-lg border border-border">
          {rolesLoading ? (
            <p className="p-4 text-sm text-muted-foreground">{t("templates.loading")}</p>
          ) : (
            <ul className="divide-y divide-border">
              {roles.map((role) => (
                <li key={role.id}>
                  <button
                    type="button"
                    onClick={() => selectRole(role)}
                    className={`flex w-full items-start gap-2 px-4 py-3 text-start text-sm transition-colors hover:bg-muted/50 ${
                      selectedId === role.id ? "bg-primary/5" : ""
                    }`}
                  >
                    {role.is_system ? (
                      <Lock className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
                    ) : null}
                    <span className="min-w-0 flex-1">
                      <span className="font-medium">{role.role_name}</span>
                      {role.description ? (
                        <span className="mt-0.5 block text-xs text-muted-foreground line-clamp-2">
                          {role.description}
                        </span>
                      ) : null}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </aside>

        <section className="rounded-lg border border-border p-4">
          {!selectedRole ? (
            <p className="text-sm text-muted-foreground">{t("roles.selectRole")}</p>
          ) : (
            <div className="space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <h2 className="text-lg font-semibold">{selectedRole.role_name}</h2>
                  <Badge
                    variant={selectedRole.is_system ? "neutral" : "info"}
                    label={
                      selectedRole.is_system
                        ? t("roles.systemRole")
                        : t("roles.customRole")
                    }
                  />
                </div>
                {!selectedRole.is_system ? (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setDeleteTarget(selectedRole)}
                  >
                    <Trash2 className="size-4 text-destructive" />
                    {t("roles.delete")}
                  </Button>
                ) : null}
              </div>

              {selectedRole.is_system ? (
                <p className="text-sm text-muted-foreground">{t("roles.systemReadOnly")}</p>
              ) : null}

              <h3 className="font-medium">{t("roles.permissions")}</h3>
              <div className="space-y-4">
                {PERMISSION_MODULE_ORDER.map((mod) => {
                  const items = grouped[mod];
                  if (!items?.length) return null;
                  return (
                    <div key={mod}>
                      <p className="mb-2 text-sm font-medium text-muted-foreground">
                        {t(`roles.modules.${mod}`)}
                      </p>
                      <div className="grid gap-2 sm:grid-cols-2">
                        {items.map((p) => (
                          <label
                            key={p.codename}
                            className={`flex items-center gap-2 rounded border border-border px-3 py-2 text-sm ${
                              selectedRole.is_system ? "opacity-60" : "cursor-pointer"
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={draftPermissions.has(p.codename)}
                              disabled={selectedRole.is_system}
                              onChange={() => togglePermission(p.codename)}
                            />
                            <span>{p.label}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>

              {!selectedRole.is_system ? (
                <div className="flex justify-end pt-2">
                  <Button
                    variant="primary"
                    loading={savePermissionsMutation.isPending}
                    onClick={() => savePermissionsMutation.mutate()}
                  >
                    {t("roles.savePermissions")}
                  </Button>
                </div>
              ) : null}
            </div>
          )}
        </section>
      </div>

      <Modal
        open={createOpen}
        onOpenChange={setCreateOpen}
        title={t("roles.createTitle")}
        idBase="createRole"
        className="max-w-lg"
      >
        <div className="space-y-4">
          <div>
            <Label>{t("roles.roleName")} *</Label>
            <Input
              value={roleName}
              onChange={(e) => setRoleName(e.target.value)}
              placeholder="custom_role"
            />
          </div>
          <div>
            <Label>{t("roles.description")}</Label>
            <Input value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setCreateOpen(false)}>
              {t("common.cancel")}
            </Button>
            <Button
              variant="primary"
              loading={createMutation.isPending}
              disabled={!roleName.trim()}
              onClick={() => createMutation.mutate()}
            >
              {t("templates.create")}
            </Button>
          </div>
        </div>
      </Modal>

      <Modal
        open={Boolean(deleteTarget)}
        onOpenChange={(o) => !o && setDeleteTarget(null)}
        title={t("roles.delete")}
        idBase="deleteRole"
      >
        <p className="mb-4 text-sm">
          {t("roles.deleteConfirm", { name: deleteTarget?.role_name })}
        </p>
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setDeleteTarget(null)}>
            {t("common.cancel")}
          </Button>
          <Button
            variant="danger"
            loading={deleteMutation.isPending}
            onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
          >
            {t("roles.delete")}
          </Button>
        </div>
      </Modal>
    </main>
  );
}
