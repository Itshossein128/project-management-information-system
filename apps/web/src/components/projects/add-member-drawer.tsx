import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  addMember,
  clearMemberPermissionOverride,
  fetchMemberPermissions,
  lookupUsers,
  setMemberPermissionOverride,
  updateMember,
  type ProjectMember,
  type Role,
  type UserLookupResult,
} from "@/app/lib/api/members";
import {
  groupPermissionsByModule,
  PERMISSION_MODULE_ORDER,
} from "@/app/lib/api/roles";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { Input } from "@/components/form";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/toast";
import { usePermission } from "@/app/contexts/project-context";

interface AddMemberDrawerProps {
  projectId: string;
  isOpen: boolean;
  onClose: () => void;
  editMember: ProjectMember | null;
  roles: Role[];
}

export function AddMemberDrawer({
  projectId,
  isOpen,
  onClose,
  editMember,
  roles,
}: AddMemberDrawerProps) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const { has } = usePermission(projectId);

  const [search, setSearch] = useState("");
  const [results, setResults] = useState<UserLookupResult[]>([]);
  const [selectedUser, setSelectedUser] = useState<UserLookupResult | null>(null);
  const [inviteEmail, setInviteEmail] = useState("");
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const { data: permData } = useQuery({
    queryKey: ["member-permissions", projectId, editMember?.user_id],
    queryFn: () => fetchMemberPermissions(projectId, editMember!.user_id!),
    enabled: Boolean(editMember?.user_id && isOpen),
  });

  const groupedPermissions = useMemo(
    () => groupPermissionsByModule(permData?.permissions.map((p) => ({ codename: p.codename, label: p.label })) ?? []),
    [permData?.permissions],
  );

  const grantedSummary = useMemo(() => {
    if (!permData?.permissions) return [];
    return permData.permissions.filter((p) => p.granted === true);
  }, [permData?.permissions]);

  useEffect(() => {
    if (!isOpen) return;
    if (editMember) {
      const roleIds = roles.filter((r) => editMember.roles.includes(r.role_name)).map((r) => r.id);
      setSelectedRoles(roleIds);
    } else {
      setSelectedRoles([]);
      setSelectedUser(null);
      setInviteEmail("");
      setSearch("");
      setResults([]);
    }
  }, [isOpen, editMember, roles]);

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (editMember?.user_id) {
        return updateMember(projectId, editMember.user_id, { role_ids: selectedRoles });
      }
      if (selectedUser) {
        return addMember(projectId, { user_id: selectedUser.user_id, role_ids: selectedRoles });
      }
      return addMember(projectId, { email: inviteEmail, role_ids: selectedRoles });
    },
    onSuccess: () => {
      toast.success(t("projectMembers.saved"));
      void qc.invalidateQueries({ queryKey: ["members", projectId] });
      onClose();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const handleSearch = async () => {
    if (search.length < 2) return;
    setResults(await lookupUsers(search));
  };

  const toggleRole = (roleId: string) => {
    setSelectedRoles((prev) =>
      prev.includes(roleId) ? prev.filter((id) => id !== roleId) : [...prev, roleId],
    );
  };

  const handleOverride = async (codename: string, state: "inherit" | "grant" | "deny") => {
    if (!editMember?.user_id) return;
    if (state === "inherit") {
      await clearMemberPermissionOverride(projectId, editMember.user_id, codename);
      toast.success(t("projectMembers.overrideReset"));
    } else {
      await setMemberPermissionOverride(projectId, editMember.user_id, {
        permission_codename: codename,
        is_granted: state === "grant",
      });
    }
    void qc.invalidateQueries({ queryKey: ["member-permissions", projectId, editMember.user_id] });
  };

  const overrideState = (codename: string): "inherit" | "grant" | "deny" => {
    const entry = permData?.permissions.find((p) => p.codename === codename);
    if (!entry || entry.granted === null) return "inherit";
    return entry.granted ? "grant" : "deny";
  };

  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      title={editMember ? t("projectMembers.drawerEdit") : t("projectMembers.drawerAdd")}
      footer={
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={onClose}>{t("common.cancel")}</Button>
          <Button
            variant="primary"
            loading={saveMutation.isPending}
            disabled={selectedRoles.length === 0}
            onClick={() => saveMutation.mutate()}
          >
            {t("wbs.save")}
          </Button>
        </div>
      }
    >
      {!editMember && (
        <div className="mb-4 space-y-2">
          <Label>{t("projectMembers.searchUser")}</Label>
          <div className="flex gap-2">
            <Input value={search} onChange={(e) => setSearch(e.target.value)} />
            <Button variant="secondary" onClick={handleSearch}>{t("projectWizard.search")}</Button>
          </div>
          {results.map((u) => (
            <button
              key={u.user_id}
              type="button"
              className="block w-full rounded border border-border px-3 py-2 text-start text-sm hover:bg-muted"
              onClick={() => setSelectedUser(u)}
            >
              {u.full_name} — {u.email || u.mobile}
            </button>
          ))}
          {!selectedUser && search.length >= 2 && results.length === 0 && (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">{t("projectWizard.userNotFound")}</p>
              <Input
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                placeholder={t("projectWizard.email")}
              />
            </div>
          )}
        </div>
      )}

      <div className="space-y-2">
        <Label>{t("projectMembers.rolesRequired")} *</Label>
        {roles.map((r) => (
          <label key={r.id} className="flex items-start gap-2 text-sm">
            <input
              type="checkbox"
              checked={selectedRoles.includes(r.id)}
              onChange={() => toggleRole(r.id)}
            />
            <span>
              <span className="font-medium">{r.role_name}</span>
              {r.description ? <span className="block text-muted-foreground">{r.description}</span> : null}
            </span>
          </label>
        ))}
      </div>

      {has("manage_members") && editMember && permData && (
        <div className="mt-6 space-y-3">
          <div>
            <p className="text-sm font-medium">{t("projectMembers.effectiveSummary")}</p>
            <p className="mt-1 text-xs text-muted-foreground">
              {grantedSummary.length > 0
                ? grantedSummary.map((p) => p.label).join(" · ")
                : "—"}
            </p>
          </div>

          <button
            type="button"
            className="text-sm font-medium text-primary"
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            {t("projectMembers.advancedPermissions")} {showAdvanced ? "▲" : "▼"}
          </button>
          {showAdvanced && permData.permissions && (
            <div className="space-y-4">
              {PERMISSION_MODULE_ORDER.map((mod) => {
                const items = groupedPermissions[mod];
                if (!items?.length) return null;
                return (
                  <div key={mod}>
                    <p className="mb-1 text-xs font-medium text-muted-foreground">
                      {t(`roles.modules.${mod}`)}
                    </p>
                    <table className="w-full text-xs">
                      <thead>
                        <tr>
                          <th className="text-start">{t("projectMembers.permission")}</th>
                          <th>{t("projectMembers.inherit")}</th>
                          <th>{t("projectMembers.grant")}</th>
                          <th>{t("projectMembers.deny")}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {items.map((p) => {
                          const state = overrideState(p.codename);
                          return (
                            <tr key={p.codename}>
                              <td className="py-1">{p.label}</td>
                              <td>
                                <input
                                  type="radio"
                                  name={p.codename}
                                  checked={state === "inherit"}
                                  onChange={() => handleOverride(p.codename, "inherit")}
                                />
                              </td>
                              <td>
                                <input
                                  type="radio"
                                  name={p.codename}
                                  checked={state === "grant"}
                                  onChange={() => handleOverride(p.codename, "grant")}
                                />
                              </td>
                              <td>
                                <input
                                  type="radio"
                                  name={p.codename}
                                  checked={state === "deny"}
                                  onChange={() => handleOverride(p.codename, "deny")}
                                />
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </Drawer>
  );
}
