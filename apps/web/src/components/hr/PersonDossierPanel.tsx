import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import type { PersonDossier } from "@/app/lib/api/hr-capacity";
import type { ProjectMember } from "@/app/lib/api/members";
import { Button } from "@/components/ui/sprint-button";
import { LoadingSkeleton } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { useToast } from "@/components/ui/toast";

type OrgUnitOption = { id: string; name: string };

type Props = {
  projectId: string;
  userId: string;
  canEdit: boolean;
  members?: ProjectMember[];
  orgUnits?: OrgUnitOption[];
  fetchDossier: (projectId: string, userId: string) => Promise<PersonDossier>;
  updateDossier: (
    projectId: string,
    userId: string,
    body: Partial<{
      skills: string[];
      qualifications: string[];
      status: string;
      default_capacity_percent: string;
      org_unit_id: string | null;
      supervisor_id: string | null;
    }>,
  ) => Promise<PersonDossier>;
};

export function PersonDossierPanel({
  projectId,
  userId,
  canEdit,
  members = [],
  orgUnits = [],
  fetchDossier,
  updateDossier,
}: Props) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const q = useQuery({
    queryKey: ["person-dossier", projectId, userId],
    queryFn: () => fetchDossier(projectId, userId),
  });
  const [skills, setSkills] = useState("");
  const [qualifications, setQualifications] = useState("");
  const [capacity, setCapacity] = useState("100");
  const [orgUnitId, setOrgUnitId] = useState("");
  const [supervisorId, setSupervisorId] = useState("");

  useEffect(() => {
    if (!q.data) return;
    setSkills((q.data.skills ?? []).join(", "));
    setQualifications((q.data.qualifications ?? []).join(", "));
    setCapacity(String(q.data.default_capacity_percent ?? "100"));
    setOrgUnitId(q.data.org_unit_id ?? "");
    setSupervisorId(q.data.supervisor_id ?? "");
  }, [q.data]);

  const save = useMutation({
    mutationFn: () =>
      updateDossier(projectId, userId, {
        skills: skills
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        qualifications: qualifications
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        default_capacity_percent: capacity,
        org_unit_id: orgUnitId || null,
        supervisor_id: supervisorId || null,
      }),
    onSuccess: () => {
      toast.success(t("hr.capacity.dossierSaved"));
      void qc.invalidateQueries({ queryKey: ["person-dossier", projectId, userId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (q.isLoading) return <LoadingSkeleton rows={4} />;
  if (q.isError || !q.data) {
    return <QueryErrorState onRetry={() => void q.refetch()} />;
  }

  const d = q.data;
  const people = members.filter((m) => m.user_id && m.user_id !== userId);

  return (
    <div className="space-y-3 p-1 text-sm">
      <p className="font-medium">{d.full_name}</p>
      <p className="text-muted-foreground">
        {d.email || d.mobile} · {d.status}
      </p>
      <label className="block">
        <span className="mb-1 block">{t("hr.capacity.orgUnit")}</span>
        <select
          className="w-full rounded-md border bg-background px-2 py-1.5"
          disabled={!canEdit}
          value={orgUnitId}
          onChange={(e) => setOrgUnitId(e.target.value)}
        >
          <option value="">{t("hr.capacity.optional")}</option>
          {orgUnits.map((u) => (
            <option key={u.id} value={u.id}>
              {u.name}
            </option>
          ))}
          {!orgUnits.length && d.org_unit_id ? (
            <option value={d.org_unit_id}>{d.org_unit_name || d.org_unit_id}</option>
          ) : null}
        </select>
      </label>
      <label className="block">
        <span className="mb-1 block">{t("hr.capacity.supervisor")}</span>
        <select
          className="w-full rounded-md border bg-background px-2 py-1.5"
          disabled={!canEdit}
          value={supervisorId}
          onChange={(e) => setSupervisorId(e.target.value)}
        >
          <option value="">{t("hr.capacity.optional")}</option>
          {people.map((m) => (
            <option key={m.user_id!} value={m.user_id!}>
              {m.full_name || m.email || m.user_id}
            </option>
          ))}
          {d.supervisor_id && !people.some((m) => m.user_id === d.supervisor_id) ? (
            <option value={d.supervisor_id}>{d.supervisor_name || d.supervisor_id}</option>
          ) : null}
        </select>
      </label>
      <label className="block">
        <span className="mb-1 block">{t("hr.capacity.skills")}</span>
        <input
          className="w-full rounded-md border bg-background px-2 py-1.5"
          disabled={!canEdit}
          value={skills}
          onChange={(e) => setSkills(e.target.value)}
          placeholder={t("hr.capacity.commaSeparated")}
        />
      </label>
      <label className="block">
        <span className="mb-1 block">{t("hr.capacity.qualifications")}</span>
        <input
          className="w-full rounded-md border bg-background px-2 py-1.5"
          disabled={!canEdit}
          value={qualifications}
          onChange={(e) => setQualifications(e.target.value)}
          placeholder={t("hr.capacity.commaSeparated")}
        />
      </label>
      <label className="block">
        <span className="mb-1 block">{t("hr.capacity.defaultCapacity")}</span>
        <input
          type="number"
          className="w-full rounded-md border bg-background px-2 py-1.5"
          disabled={!canEdit}
          value={capacity}
          onChange={(e) => setCapacity(e.target.value)}
        />
      </label>
      {canEdit && (
        <Button size="sm" disabled={save.isPending} onClick={() => save.mutate()}>
          {t("common.save")}
        </Button>
      )}
    </div>
  );
}
