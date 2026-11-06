import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  addMember,
  cancelInvitation,
  clearMemberPermissionOverride,
  connectInvitation,
  createOrganizationalUser,
  fetchMemberPermissions,
  fetchSelectablePositions,
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
import {
  formatRoleDescription,
  formatRoleLabel,
} from "@/app/lib/role-labels";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { Input } from "@/components/form";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/toast";
import {
  useActiveProjectPermission,
  usePermission,
} from "@/app/contexts/project-context";
import { formatPermissionLabel } from "@/app/lib/permission-labels";

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
  const { has: activeHas } = useActiveProjectPermission(projectId);

  const [search, setSearch] = useState("");
  const [results, setResults] = useState<UserLookupResult[]>([]);
  const [selectedUser, setSelectedUser] = useState<UserLookupResult | null>(null);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteMobile, setInviteMobile] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [createError, setCreateError] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [username, setUsername] = useState("");
  const [accountStatus, setAccountStatus] = useState<"active" | "inactive" | "suspended">("active");
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);
  const [selectedPositions, setSelectedPositions] = useState<string[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const { data: selectablePositions = [] } = useQuery({
    queryKey: ["selectable-positions", projectId],
    queryFn: async () => {
      const payload = await fetchSelectablePositions(projectId);
      return Array.isArray(payload) ? payload : payload.results;
    },
    enabled: isOpen,
  });

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
    if (!isOpen) {
      setSelectedRoles([]);
      setSelectedPositions([]);
      setSelectedUser(null);
      setInviteEmail("");
      setInviteMobile("");
      setShowCreate(false);
      setCreateError("");
      setSearch("");
      setResults([]);
      setFirstName("");
      setLastName("");
      setPhone("");
      setEmail("");
      setPassword("");
      setPasswordConfirm("");
      setUsername("");
      setAccountStatus("active");
      return;
    }
    if (editMember) {
      const roleIds = roles.filter((r) => editMember.roles.includes(r.role_name)).map((r) => r.id);
      setSelectedRoles(roleIds);
      setSelectedPositions(editMember.position_ids ?? []);
      setSelectedUser(null);
      setSearch("");
      setResults([]);
    } else {
      setSelectedRoles([]);
      setSelectedPositions([]);
      setSelectedUser(null);
      setInviteEmail("");
      setInviteMobile("");
      setShowCreate(false);
      setCreateError("");
      setSearch("");
      setResults([]);
    }
  }, [isOpen, editMember, roles]);

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (editMember?.user_id) {
        return updateMember(projectId, editMember.user_id, {
          role_ids: selectedRoles,
          position_ids: selectedPositions,
        });
      }
      if (editMember && !editMember.user_id && selectedUser) {
        return connectInvitation(projectId, editMember.id, selectedUser.user_id, {
          role_ids: selectedRoles,
          position_ids: selectedPositions,
        });
      }
      if (selectedUser) {
        return addMember(projectId, {
          user_id: selectedUser.user_id,
          role_ids: selectedRoles,
          position_ids: selectedPositions,
        });
      }
      return addMember(projectId, {
        email: inviteEmail,
        mobile: inviteMobile,
        role_ids: selectedRoles,
        position_ids: selectedPositions,
      });
    },
    onSuccess: () => {
      toast.success(t("projectMembers.saved"));
      void qc.invalidateQueries({ queryKey: ["members", projectId] });
      void qc.invalidateQueries({ queryKey: ["access-changes", projectId] });
      onClose();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const handleSearch = async () => {
    if (search.length < 2) return;
    setResults(await lookupUsers(search, projectId));
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
    if (!entry || entry.origin === "inherit" || entry.granted === null) return "inherit";
    if (entry.origin === "grant" || entry.origin === "deny") return entry.origin;
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
            disabled={editMember && !editMember.user_id ? !selectedUser : selectedRoles.length === 0}
            onClick={() => saveMutation.mutate()}
          >
            {t("wbs.save")}
          </Button>
        </div>
      }
    >
      {(!editMember || !editMember.user_id) && (
        <div className="mb-4 space-y-2">
          <Label>{t("projectMembers.searchUser")}</Label>
          <div className="flex gap-2">
            <Input value={search} onChange={(e) => setSearch(e.target.value)} />
            <Button variant="secondary" onClick={handleSearch}>{t("projectWizard.search")}</Button>
          </div>
          {results.map((u) => {
            const contactHint =
              u.email && u.mobile
                ? `${u.email} · ${u.mobile}`
                : u.email || u.mobile || u.organization_label || "";
            return (
              <button
                key={u.user_id}
                type="button"
                className="block w-full rounded border border-border px-3 py-2 text-start text-sm hover:bg-muted"
                onClick={() => setSelectedUser(u)}
              >
                {contactHint ? `${u.full_name} — ${contactHint}` : u.full_name}
              </button>
            );
          })}
          {editMember && !editMember.user_id && !editMember.invite_cancelled_at ? (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                {t(`projectMembers.delivery.${editMember.delivery_status || "not_configured"}`)}
              </p>
              <Button
                type="button"
                variant="secondary"
                onClick={() => {
                  void cancelInvitation(projectId, editMember.id).then(() => {
                    toast.success(t("projectMembers.invitationCancelled"));
                    void qc.invalidateQueries({ queryKey: ["members", projectId] });
                    void qc.invalidateQueries({ queryKey: ["access-changes", projectId] });
                    onClose();
                  }).catch((error: Error) => toast.error(error.message));
                }}
              >
                {t("projectMembers.cancelInvitation")}
              </Button>
            </div>
          ) : null}
          {(!editMember || !editMember.user_id) && !editMember?.invite_cancelled_at ? (
            <Button
              type="button"
              variant="secondary"
              disabled={!activeHas("manage_members")}
              onClick={() => setShowCreate((open) => !open)}
            >
              {t("projectMembers.createPerson")}
            </Button>
          ) : null}
          {!editMember && !selectedUser && search.length >= 2 && results.length === 0 && (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">{t("projectWizard.userNotFound")}</p>
              <Input
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                placeholder={t("projectWizard.email")}
              />
              <Input
                value={inviteMobile}
                onChange={(e) => setInviteMobile(e.target.value)}
                placeholder={t("common.phoneNumber")}
              />
            </div>
          )}
          {showCreate ? (
            <div className="space-y-2 rounded border border-border p-3">
              {createError ? <p className="text-sm text-destructive">{createError}</p> : null}
              <Input value={firstName} onChange={(e) => setFirstName(e.target.value)} placeholder={t("common.firstName")} />
              <Input value={lastName} onChange={(e) => setLastName(e.target.value)} placeholder={t("common.lastName")} />
              <Input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder={t("common.phoneNumber")} />
              <Input value={username} onChange={(e) => setUsername(e.target.value)} placeholder={t("common.username")} maxLength={60} />
              <Input value={email} onChange={(e) => setEmail(e.target.value)} placeholder={t("projectWizard.email")} />
              <select aria-label={t("projectMembers.status")} value={accountStatus} onChange={(event) => setAccountStatus(event.target.value as "active" | "inactive" | "suspended")}>
                <option value="active">{t("projectMembers.statuses.active")}</option>
                <option value="inactive">{t("projectMembers.statuses.inactive")}</option>
                <option value="suspended">{t("projectMembers.statuses.suspended")}</option>
              </select>
              <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder={t("common.password")} />
              <Input type="password" value={passwordConfirm} onChange={(e) => setPasswordConfirm(e.target.value)} placeholder={t("common.confirmPassword")} />
              <Button
                type="button"
                variant="primary"
                onClick={() => {
                  setCreateError("");
                  if (password !== passwordConfirm) {
                    setCreateError(t("common.confirmPassword"));
                    return;
                  }
                  void createOrganizationalUser({
                    phone_number: phone.trim(),
                    first_name: firstName.trim(),
                    last_name: lastName.trim(),
                    username: username.trim() || undefined,
                    email: email.trim() || undefined,
                    password,
                    password_confirm: passwordConfirm,
                    status: accountStatus,
                  }).then((created) => {
                    setSelectedUser({
                      user_id: created.id,
                      full_name: `${firstName} ${lastName}`.trim(),
                      email,
                      mobile: phone,
                    });
                    setShowCreate(false);
                  }).catch((error: Error) => {
                    setCreateError(error.message);
                  });
                }}
              >
                {t("projectMembers.createPerson")}
              </Button>
            </div>
          ) : null}
        </div>
      )}

      {selectablePositions.length > 0 ? (
        <div className="mb-4 space-y-2">
          <Label>{t("projectMembers.positions")}</Label>
          {selectablePositions.map((position) => (
            <label key={position.id} className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={selectedPositions.includes(position.id)}
                onChange={() =>
                  setSelectedPositions((current) =>
                    current.includes(position.id)
                      ? current.filter((id) => id !== position.id)
                      : [...current, position.id],
                  )
                }
              />
              <span>{position.label || position.position_name}</span>
            </label>
          ))}
        </div>
      ) : null}

      <div className="space-y-2">
        <Label>{t("projectMembers.rolesRequired")} *</Label>
        {roles.map((r) => {
          const description = formatRoleDescription(
            r.role_name,
            r.description,
            t,
          );
          return (
          <label key={r.id} className="flex items-start gap-2 text-sm">
            <input
              type="checkbox"
              checked={selectedRoles.includes(r.id)}
              onChange={() => toggleRole(r.id)}
            />
            <span>
              <span className="font-medium">
                {formatRoleLabel(r.role_name, t)}
              </span>
              {description ? (
                <span className="block text-muted-foreground">
                  {description}
                </span>
              ) : null}
            </span>
          </label>
          );
        })}
      </div>

      {activeHas("manage_members") && editMember && permData && (
        <div className="mt-6 space-y-3">
          <div>
            <p className="text-sm font-medium">{t("projectMembers.effectiveSummary")}</p>
            <p className="mt-1 text-xs text-muted-foreground">
              {grantedSummary.length > 0
                ? grantedSummary.map((p) => formatPermissionLabel(p.codename, p.label, t)).join(" · ")
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
                              <td className="py-1">{formatPermissionLabel(p.codename, p.label, t)}</td>
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
