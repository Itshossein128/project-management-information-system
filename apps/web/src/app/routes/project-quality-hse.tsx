import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import { useAuth } from "@/app/contexts/auth-context";
import {
  ProjectProvider,
  usePermission,
  useProject,
} from "@/app/contexts/project-context";
import {
  createCorrectiveAction,
  createHseEvent,
  createInspection,
  createNonconformity,
  createSafetyTraining,
  createWorkPermit,
  fetchQualitySafetyReport,
} from "@/app/lib/api/quality-hse";
import { fetchWBSFlat } from "@/app/lib/api/wbs";
import { PATHS } from "@/app/routeVars";
import { EmptyState } from "@/components/layout/empty-state";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";

function QualityHseContent() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canEdit = has("edit_reports");
  const toast = useToast();
  const qc = useQueryClient();
  const [dateFrom, setDateFrom] = useState("2026-10-01");
  const [dateTo, setDateTo] = useState("2026-10-31");
  const [insp, setInsp] = useState({
    wbs: "",
    inspection_date: "",
    description: "",
    result: "fail",
  });
  const [ncr, setNcr] = useState({
    inspectionId: "",
    description: "",
    raised_date: "",
    caDescription: "",
    caDueDate: "",
  });
  const [hse, setHse] = useState({
    kind: "incident" as "incident" | "near_miss",
    event_date: "",
    description: "",
    wbs: "",
  });
  const [permit, setPermit] = useState({
    permit_date: "",
    permit_type: "",
    description: "",
  });
  const [train, setTrain] = useState({ training_date: "", topic: "" });

  const wbsQuery = useQuery({
    queryKey: ["wbs-flat", projectId],
    queryFn: () => fetchWBSFlat(projectId),
    enabled: Boolean(projectId),
  });

  const reportQuery = useQuery({
    queryKey: ["quality-safety-report", projectId, dateFrom, dateTo],
    queryFn: () => fetchQualitySafetyReport(projectId, dateFrom, dateTo),
    enabled: Boolean(projectId && dateFrom && dateTo),
  });

  const invalidateReport = () => {
    void qc.invalidateQueries({ queryKey: ["quality-safety-report", projectId] });
  };

  const saveInspection = useMutation({
    mutationFn: () => {
      if (!user?.id) throw new Error(t("pages.qualityHse.missingUser"));
      return createInspection(projectId, {
        wbs: insp.wbs,
        responsible_user: user.id,
        inspection_date: insp.inspection_date,
        description: insp.description,
        result: insp.result,
        stage: "result",
      });
    },
    onSuccess: (created) => {
      toast.success(t("pages.qualityHse.saved"));
      setNcr((f) => ({
        ...f,
        inspectionId: created.id,
        raised_date: insp.inspection_date || f.raised_date,
        description: insp.description || f.description,
      }));
      invalidateReport();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const saveNcrCa = useMutation({
    mutationFn: async () => {
      if (!user?.id) throw new Error(t("pages.qualityHse.missingUser"));
      const ncrRow = await createNonconformity(projectId, {
        inspection: ncr.inspectionId || null,
        description: ncr.description,
        raised_date: ncr.raised_date,
        status: "open",
      });
      const ca = await createCorrectiveAction(projectId, {
        nonconformity: ncrRow.id,
        description: ncr.caDescription,
        responsible_user: user.id,
        due_date: ncr.caDueDate || null,
        status: "open",
      });
      return { ncrRow, ca };
    },
    onSuccess: () => {
      toast.success(t("pages.qualityHse.ncrSaved"));
      invalidateReport();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const saveHse = useMutation({
    mutationFn: () =>
      createHseEvent(projectId, {
        kind: hse.kind,
        event_date: hse.event_date,
        description: hse.description,
        wbs: hse.wbs || null,
      }),
    onSuccess: () => {
      toast.success(t("pages.qualityHse.saved"));
      invalidateReport();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const savePermit = useMutation({
    mutationFn: () => createWorkPermit(projectId, permit),
    onSuccess: () => {
      toast.success(t("pages.qualityHse.saved"));
      invalidateReport();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const saveTrain = useMutation({
    mutationFn: () => createSafetyTraining(projectId, train),
    onSuccess: () => {
      toast.success(t("pages.qualityHse.saved"));
      invalidateReport();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (isLoading) return <LoadingSkeleton rows={8} />;
  if (!project) return <EmptyState title={t("common.projectNotFound")} />;

  const counts = reportQuery.data?.counts;
  const emptyReport = counts && Object.values(counts).every((n) => n === 0);
  const wbsOptions = wbsQuery.data ?? [];

  return (
    <div className="space-y-8">
      <PageHeader
        title={t("pages.qualityHse.title")}
        subtitle={t("pages.qualityHse.subtitle")}
      />

      <section className="space-y-3">
        <h2 className="text-lg font-medium">{t("pages.qualityHse.periodReport")}</h2>
        <div className="flex flex-wrap gap-2">
          <JalaliDatePicker
            name="date_from"
            label={t("pages.qualityHse.dateFrom")}
            value={dateFrom}
            onChange={setDateFrom}
          />
          <JalaliDatePicker
            name="date_to"
            label={t("pages.qualityHse.dateTo")}
            value={dateTo}
            onChange={setDateTo}
          />
        </div>
        {reportQuery.isLoading ? (
          <LoadingSkeleton rows={3} />
        ) : emptyReport ? (
          <EmptyState
            title={t("pages.qualityHse.emptyReport")}
            description={t("pages.qualityHse.emptyReportDescription")}
          />
        ) : (
          <ul className="grid gap-2 text-sm sm:grid-cols-2 lg:grid-cols-4">
            {counts &&
              Object.entries(counts).map(([k, v]) => (
                <li key={k} className="rounded border px-3 py-2">
                  <span className="text-muted-foreground">
                    {t(`pages.qualityHse.counts.${k}`, { defaultValue: k })}
                  </span>
                  <div className="text-xl font-semibold">{v}</div>
                </li>
              ))}
          </ul>
        )}
      </section>

      {canEdit ? (
        <>
          <section className="space-y-3 rounded border p-4">
            <h2 className="font-medium">{t("pages.qualityHse.newInspection")}</h2>
            <select
              className="w-full rounded border px-2 py-1"
              value={insp.wbs}
              onChange={(e) => setInsp((f) => ({ ...f, wbs: e.target.value }))}
            >
              <option value="">{t("pages.qualityHse.selectWbs")}</option>
              {wbsOptions.map((n) => (
                <option key={n.wbs_id} value={n.wbs_id}>
                  {n.wbs_code} — {n.wbs_name}
                </option>
              ))}
            </select>
            <JalaliDatePicker
              name="inspection_date"
              label={t("pages.qualityHse.date")}
              value={insp.inspection_date}
              onChange={(v) => setInsp((f) => ({ ...f, inspection_date: v }))}
            />
            <select
              className="w-full rounded border px-2 py-1"
              value={insp.result}
              onChange={(e) => setInsp((f) => ({ ...f, result: e.target.value }))}
            >
              <option value="fail">{t("pages.qualityHse.resultFail")}</option>
              <option value="pass">{t("pages.qualityHse.resultPass")}</option>
              <option value="conditional">{t("pages.qualityHse.resultConditional")}</option>
              <option value="pending">{t("pages.qualityHse.resultPending")}</option>
            </select>
            <textarea
              className="w-full rounded border px-2 py-1"
              placeholder={t("pages.qualityHse.description")}
              value={insp.description}
              onChange={(e) =>
                setInsp((f) => ({ ...f, description: e.target.value }))
              }
            />
            <Button
              size="sm"
              onClick={() => saveInspection.mutate()}
              loading={saveInspection.isPending}
            >
              {t("common.save")}
            </Button>
          </section>

          <section className="space-y-3 rounded border p-4">
            <h2 className="font-medium">{t("pages.qualityHse.newNcr")}</h2>
            <p className="text-sm text-muted-foreground">
              {t("pages.qualityHse.ncrHint")}
            </p>
            <input
              className="w-full rounded border px-2 py-1 text-sm"
              placeholder={t("pages.qualityHse.inspectionId")}
              value={ncr.inspectionId}
              onChange={(e) =>
                setNcr((f) => ({ ...f, inspectionId: e.target.value }))
              }
            />
            <JalaliDatePicker
              name="ncr_date"
              label={t("pages.qualityHse.date")}
              value={ncr.raised_date}
              onChange={(v) => setNcr((f) => ({ ...f, raised_date: v }))}
            />
            <textarea
              className="w-full rounded border px-2 py-1"
              placeholder={t("pages.qualityHse.ncrDescription")}
              value={ncr.description}
              onChange={(e) =>
                setNcr((f) => ({ ...f, description: e.target.value }))
              }
            />
            <textarea
              className="w-full rounded border px-2 py-1"
              placeholder={t("pages.qualityHse.caDescription")}
              value={ncr.caDescription}
              onChange={(e) =>
                setNcr((f) => ({ ...f, caDescription: e.target.value }))
              }
            />
            <JalaliDatePicker
              name="ca_due"
              label={t("pages.qualityHse.caDueDate")}
              value={ncr.caDueDate}
              onChange={(v) => setNcr((f) => ({ ...f, caDueDate: v }))}
            />
            <Button
              size="sm"
              onClick={() => saveNcrCa.mutate()}
              loading={saveNcrCa.isPending}
              disabled={!ncr.inspectionId || !ncr.description || !ncr.caDescription}
            >
              {t("pages.qualityHse.saveNcrCa")}
            </Button>
          </section>

          <section className="space-y-3 rounded border p-4">
            <h2 className="font-medium">{t("pages.qualityHse.newHse")}</h2>
            <select
              className="w-full rounded border px-2 py-1"
              value={hse.kind}
              onChange={(e) =>
                setHse((f) => ({
                  ...f,
                  kind: e.target.value as "incident" | "near_miss",
                }))
              }
            >
              <option value="incident">{t("pages.qualityHse.incident")}</option>
              <option value="near_miss">{t("pages.qualityHse.nearMiss")}</option>
            </select>
            <select
              className="w-full rounded border px-2 py-1"
              value={hse.wbs}
              onChange={(e) => setHse((f) => ({ ...f, wbs: e.target.value }))}
            >
              <option value="">{t("pages.qualityHse.wbsOptional")}</option>
              {wbsOptions.map((n) => (
                <option key={n.wbs_id} value={n.wbs_id}>
                  {n.wbs_code} — {n.wbs_name}
                </option>
              ))}
            </select>
            <JalaliDatePicker
              name="hse_date"
              label={t("pages.qualityHse.date")}
              value={hse.event_date}
              onChange={(v) => setHse((f) => ({ ...f, event_date: v }))}
            />
            <textarea
              className="w-full rounded border px-2 py-1"
              placeholder={t("pages.qualityHse.description")}
              value={hse.description}
              onChange={(e) =>
                setHse((f) => ({ ...f, description: e.target.value }))
              }
            />
            <Button size="sm" onClick={() => saveHse.mutate()} loading={saveHse.isPending}>
              {t("common.save")}
            </Button>
          </section>

          <section className="space-y-3 rounded border p-4">
            <h2 className="font-medium">{t("pages.qualityHse.permitTraining")}</h2>
            <JalaliDatePicker
              name="permit_date"
              label={t("pages.qualityHse.permitDate")}
              value={permit.permit_date}
              onChange={(v) => setPermit((f) => ({ ...f, permit_date: v }))}
            />
            <input
              className="w-full rounded border px-2 py-1"
              placeholder={t("pages.qualityHse.permitType")}
              value={permit.permit_type}
              onChange={(e) =>
                setPermit((f) => ({ ...f, permit_type: e.target.value }))
              }
            />
            <Button
              size="sm"
              onClick={() => savePermit.mutate()}
              loading={savePermit.isPending}
            >
              {t("pages.qualityHse.savePermit")}
            </Button>
            <JalaliDatePicker
              name="training_date"
              label={t("pages.qualityHse.trainingDate")}
              value={train.training_date}
              onChange={(v) => setTrain((f) => ({ ...f, training_date: v }))}
            />
            <input
              className="w-full rounded border px-2 py-1"
              placeholder={t("pages.qualityHse.topic")}
              value={train.topic}
              onChange={(e) => setTrain((f) => ({ ...f, topic: e.target.value }))}
            />
            <Button
              size="sm"
              onClick={() => saveTrain.mutate()}
              loading={saveTrain.isPending}
            >
              {t("pages.qualityHse.saveTraining")}
            </Button>
          </section>
        </>
      ) : null}
    </div>
  );
}

export default function ProjectQualityHsePage() {
  const { t } = useTranslation();
  const { projectId = "" } = useParams();
  return (
    <main className="page-main page-shell mx-auto px-4 py-8">
      <ProjectProvider projectId={projectId}>
        <Breadcrumb
          items={[
            { label: t("pages.qualityHse.projectsCrumb"), href: `/${PATHS.PROJECT}` },
            { label: t("pages.qualityHse.title") },
          ]}
        />
        <QualityHseContent />
      </ProjectProvider>
    </main>
  );
}
