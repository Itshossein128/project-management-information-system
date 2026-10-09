import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router";
import { useAuth } from "@/app/contexts/auth-context";
import {
  ProjectProvider,
  usePermission,
  useProject,
} from "@/app/contexts/project-context";
import {
  asList,
  createCommunicationPlan,
  createStakeholder,
  fetchCommunicationPlans,
  fetchStakeholderMatrix,
  fetchStakeholders,
} from "@/app/lib/api/central-data";
import { PATHS } from "@/app/routeVars";
import { Input, Label } from "@/components/form";
import { AccessDenied, NotFoundState } from "@/components/layout/empty-state";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

function StakeholdersContent() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_project");
  const canEdit = has("edit_project");
  const toast = useToast();
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const [org, setOrg] = useState("");
  const [influence, setInfluence] = useState("");
  const [interest, setInterest] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [relationshipOwner, setRelationshipOwner] = useState(user?.id ?? "");
  const [planAudience, setPlanAudience] = useState("");
  const [planMessage, setPlanMessage] = useState("");
  const [planFrequency, setPlanFrequency] = useState("");
  const [planChannel, setPlanChannel] = useState("");
  const [planStakeholderId, setPlanStakeholderId] = useState("");

  const { data, isLoading: listLoading } = useQuery({
    queryKey: ["stakeholders", projectId],
    queryFn: () => fetchStakeholders(projectId),
    enabled: canView && Boolean(projectId),
  });

  const { data: matrixData, isLoading: matrixLoading } = useQuery({
    queryKey: ["stakeholder-matrix", projectId],
    queryFn: () => fetchStakeholderMatrix(projectId),
    enabled: canView && Boolean(projectId),
  });

  const { data: plansData, isLoading: plansLoading } = useQuery({
    queryKey: ["communication-plans", projectId],
    queryFn: () => fetchCommunicationPlans(projectId),
    enabled: canView && Boolean(projectId),
  });

  const create = useMutation({
    mutationFn: () =>
      createStakeholder(projectId, {
        name,
        organization_name: org,
        influence: influence ? Number(influence) : null,
        interest: interest ? Number(interest) : null,
        email: email || "",
        phone: phone || "",
        relationship_owner: relationshipOwner || null,
      }),
    onSuccess: () => {
      toast.success(t("centralData.stakeholderCreated", "ذینفع ثبت شد"));
      setName("");
      setOrg("");
      setInfluence("");
      setInterest("");
      setEmail("");
      setPhone("");
      void qc.invalidateQueries({ queryKey: ["stakeholders", projectId] });
      void qc.invalidateQueries({ queryKey: ["stakeholder-matrix", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const createPlan = useMutation({
    mutationFn: () =>
      createCommunicationPlan(projectId, {
        audience: planAudience,
        message: planMessage,
        frequency: planFrequency,
        channel_type: planChannel,
        owner: user?.id ?? null,
        stakeholder: planStakeholderId || null,
      }),
    onSuccess: () => {
      toast.success(t("collab.communicationPlanCreated", "Communication plan saved"));
      setPlanAudience("");
      setPlanMessage("");
      setPlanFrequency("");
      setPlanChannel("");
      setPlanStakeholderId("");
      void qc.invalidateQueries({ queryKey: ["communication-plans", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (isLoading || listLoading || matrixLoading || plansLoading) {
    return <LoadingSkeleton rows={8} />;
  }
  if (!project) return <NotFoundState title={t("common.projectNotFound")} />;
  if (!canView) return <AccessDenied />;

  const rows = asList(data ?? []);
  const matrixCells = matrixData?.cells ?? [];
  const plans = plansData?.results ?? [];

  return (
    <div className="space-y-8">
      <PageHeader
        title={t("centralData.stakeholders", "ذینفعان")}
        subtitle={project.project_name}
      />

      <ul className="divide-y rounded border">
        {rows.map((s) => (
          <li key={s.id} className="space-y-1 px-3 py-2 text-sm">
            <div className="flex flex-wrap justify-between gap-2">
              <span>
                {s.name}
                {s.organization_name ? ` — ${s.organization_name}` : ""}
              </span>
              <span className="text-muted-foreground">
                {s.influence != null ? `I=${s.influence}` : ""}
                {s.interest != null ? ` · Int=${s.interest}` : ""}
              </span>
            </div>
            <div className="text-xs text-muted-foreground">
              {s.relationship_owner
                ? `${t("collab.relationshipOwner", "Relationship owner")}: ${s.relationship_owner}`
                : null}
            </div>
            <div className="text-xs text-muted-foreground">
              {s.contacts_redacted ? (
                <span>{t("collab.contactsRedacted", "Contact details hidden")}</span>
              ) : (
                <>
                  {s.email ? `${t("common.email", "Email")}: ${s.email}` : ""}
                  {s.email && s.phone ? " · " : ""}
                  {s.phone ? `${t("common.phoneNumber", "Phone")}: ${s.phone}` : ""}
                </>
              )}
            </div>
          </li>
        ))}
        {rows.length === 0 ? (
          <li className="px-3 py-4 text-sm text-muted-foreground">
            {t("centralData.noStakeholders", "ذینفعی ثبت نشده است.")}
          </li>
        ) : null}
      </ul>

      {matrixCells.length > 0 ? (
        <section className="space-y-2">
          <h2 className="text-sm font-medium">{t("collab.stakeholderMatrix", "Influence / interest matrix")}</h2>
          <div className="overflow-x-auto rounded border">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  <th className="px-3 py-2 text-start">{t("centralData.influence", "Influence")}</th>
                  <th className="px-3 py-2 text-start">{t("collab.interest", "Interest")}</th>
                  <th className="px-3 py-2 text-start">{t("centralData.stakeholders", "Stakeholders")}</th>
                </tr>
              </thead>
              <tbody>
                {matrixCells.map((cell) => (
                  <tr key={`${cell.influence}-${cell.interest}`} className="border-t">
                    <td className="px-3 py-2">{cell.influence}</td>
                    <td className="px-3 py-2">{cell.interest}</td>
                    <td className="px-3 py-2">
                      {cell.stakeholders.map((st) => st.name).join(", ") || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}

      <section className="space-y-3">
        <h2 className="text-sm font-medium">{t("collab.communicationPlans", "Communication plans")}</h2>
        <ul className="divide-y rounded border text-sm">
          {plans.map((p) => (
            <li key={p.id} className="space-y-1 px-3 py-2">
              <p className="font-medium">{p.audience}</p>
              <p className="text-muted-foreground">{p.message}</p>
              <p className="text-xs text-muted-foreground">
                {p.frequency}
                {p.channel_type ? ` · ${p.channel_type}` : ""}
              </p>
            </li>
          ))}
          {plans.length === 0 ? (
            <li className="px-3 py-4 text-muted-foreground">
              {t("collab.noCommunicationPlans", "No communication plans yet.")}
            </li>
          ) : null}
        </ul>
        {canEdit ? (
          <div className="grid max-w-xl gap-2">
            <Label>{t("collab.planAudience", "Audience")}</Label>
            <Input value={planAudience} onChange={(e) => setPlanAudience(e.target.value)} />
            <Label>{t("collab.planMessage", "Message")}</Label>
            <Input value={planMessage} onChange={(e) => setPlanMessage(e.target.value)} />
            <Label>{t("collab.planFrequency", "Frequency")}</Label>
            <Input value={planFrequency} onChange={(e) => setPlanFrequency(e.target.value)} />
            <Label>{t("collab.planChannel", "Channel")}</Label>
            <Input value={planChannel} onChange={(e) => setPlanChannel(e.target.value)} />
            <Label>{t("collab.planStakeholder", "Linked stakeholder (optional ID)")}</Label>
            <Input
              value={planStakeholderId}
              onChange={(e) => setPlanStakeholderId(e.target.value)}
            />
            <Button
              variant="primary"
              loading={createPlan.isPending}
              disabled={!planAudience || !planMessage || !planFrequency}
              onClick={() => createPlan.mutate()}
            >
              {t("common.add", "افزودن")}
            </Button>
          </div>
        ) : null}
      </section>

      {canEdit ? (
        <div className="grid max-w-xl gap-2">
          <h2 className="text-sm font-medium">{t("collab.addStakeholder", "Add stakeholder")}</h2>
          <Label>{t("centralData.name", "نام")}</Label>
          <Input value={name} onChange={(e) => setName(e.target.value)} />
          <Label>{t("centralData.organization", "سازمان")}</Label>
          <Input value={org} onChange={(e) => setOrg(e.target.value)} />
          <Label>{t("centralData.influence", "نفوذ (۱–۵)")}</Label>
          <Input
            value={influence}
            onChange={(e) => setInfluence(e.target.value)}
            inputMode="numeric"
          />
          <Label>{t("collab.interest", "Interest (1–5)")}</Label>
          <Input
            value={interest}
            onChange={(e) => setInterest(e.target.value)}
            inputMode="numeric"
          />
          <Label>{t("common.email", "Email")}</Label>
          <Input value={email} onChange={(e) => setEmail(e.target.value)} />
          <Label>{t("common.phoneNumber", "Phone number")}</Label>
          <Input value={phone} onChange={(e) => setPhone(e.target.value)} />
          <Label>{t("collab.relationshipOwnerId", "Relationship owner (user ID)")}</Label>
          <Input
            value={relationshipOwner}
            onChange={(e) => setRelationshipOwner(e.target.value)}
          />
          <Button
            variant="primary"
            loading={create.isPending}
            disabled={!name}
            onClick={() => create.mutate()}
          >
            {t("common.add", "افزودن")}
          </Button>
        </div>
      ) : null}
    </div>
  );
}

export default function ProjectStakeholdersPage() {
  const { t } = useTranslation();
  const { projectId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto px-4 py-8">
        <Breadcrumb
          items={[
            { label: t("project.title"), href: `/${PATHS.PROJECT}` },
            {
              label: t("centralData.stakeholders", "ذینفعان"),
            },
          ]}
        />
        <StakeholdersContent />
      </main>
    </ProjectProvider>
  );
}
