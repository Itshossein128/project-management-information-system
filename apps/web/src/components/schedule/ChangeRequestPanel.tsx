import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { fetchActivities } from "@/app/lib/api/activities";
import {
  approveScheduleChangeRequest,
  createScheduleChangeRequest,
  fetchScheduleChangeRequests,
  rejectScheduleChangeRequest,
  submitScheduleChangeRequest,
  updateScheduleChangeRequest,
  type ChangeRequestStatus,
  type ScheduleChangeItem,
  type ScheduleChangeRequest,
} from "@/app/lib/api/schedule";
import { JalaliDatePicker, Input, TextArea } from "@/components/form";
import { Label } from "@/components/ui/label";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

type DraftForm = {
  reason: string;
  milestone_impact: string;
  cost_impact: string;
  contract_impact: string;
  items: ScheduleChangeItem[];
};

const emptyDraft = (): DraftForm => ({
  reason: "",
  milestone_impact: "",
  cost_impact: "",
  contract_impact: "",
  items: [],
});

function statusLabel(
  t: (key: string) => string,
  status: ChangeRequestStatus,
): string {
  switch (status) {
    case "draft":
      return t("schedule.changeRequestStatuses.draft");
    case "submitted":
      return t("schedule.changeRequestStatuses.submitted");
    case "approved":
      return t("schedule.changeRequestStatuses.approved");
    case "rejected":
      return t("schedule.changeRequestStatuses.rejected");
    default: {
      const _exhaustive: never = status;
      return _exhaustive;
    }
  }
}

export function ChangeRequestPanel({
  projectId,
  canEdit,
}: {
  projectId: string;
  canEdit: boolean;
}) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selected, setSelected] = useState<ScheduleChangeRequest | null>(null);
  const [form, setForm] = useState<DraftForm>(emptyDraft);
  const [decisionNotes, setDecisionNotes] = useState("");

  const { data: requests = [], isLoading } = useQuery({
    queryKey: ["schedule-change-requests", projectId],
    queryFn: () => fetchScheduleChangeRequests(projectId),
    enabled: Boolean(projectId),
  });

  const { data: activitiesPage } = useQuery({
    queryKey: ["activities-for-scr", projectId],
    queryFn: () => fetchActivities(projectId, { per_page: 200 }),
    enabled: drawerOpen,
  });
  const activities = activitiesPage?.results ?? [];

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["schedule-change-requests", projectId] });
    void qc.invalidateQueries({ queryKey: ["gantt", projectId] });
    void qc.invalidateQueries({ queryKey: ["baselines", projectId] });
    void qc.invalidateQueries({ queryKey: ["schedule-status", projectId] });
  };

  const createMut = useMutation({
    mutationFn: () => createScheduleChangeRequest(projectId, form),
    onSuccess: (created) => {
      toast.success(t("common.success"));
      setSelected(created);
      setForm({
        reason: created.reason,
        milestone_impact: created.milestone_impact,
        cost_impact: created.cost_impact,
        contract_impact: created.contract_impact,
        items: created.items.map((i) => ({
          activity_id: i.activity_id,
          proposed_planned_start: i.proposed_planned_start,
          proposed_planned_finish: i.proposed_planned_finish,
          proposed_duration_days: i.proposed_duration_days,
          proposed_forecast_start: i.proposed_forecast_start,
          proposed_forecast_finish: i.proposed_forecast_finish,
          notes: i.notes,
        })),
      });
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const updateMut = useMutation({
    mutationFn: () =>
      updateScheduleChangeRequest(projectId, selected!.id, form),
    onSuccess: (updated) => {
      toast.success(t("common.success"));
      setSelected(updated);
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const submitMut = useMutation({
    mutationFn: () => submitScheduleChangeRequest(projectId, selected!.id),
    onSuccess: (updated) => {
      toast.success(t("common.success"));
      setSelected(updated);
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const approveMut = useMutation({
    mutationFn: () =>
      approveScheduleChangeRequest(projectId, selected!.id, decisionNotes),
    onSuccess: (updated) => {
      toast.success(t("common.success"));
      setSelected(updated);
      setDecisionNotes("");
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const rejectMut = useMutation({
    mutationFn: () =>
      rejectScheduleChangeRequest(projectId, selected!.id, decisionNotes),
    onSuccess: (updated) => {
      toast.success(t("common.success"));
      setSelected(updated);
      setDecisionNotes("");
      invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  function openNew() {
    setSelected(null);
    setForm(emptyDraft());
    setDecisionNotes("");
    setDrawerOpen(true);
  }

  function openExisting(row: ScheduleChangeRequest) {
    setSelected(row);
    setForm({
      reason: row.reason,
      milestone_impact: row.milestone_impact,
      cost_impact: row.cost_impact,
      contract_impact: row.contract_impact,
      items: row.items.map((i) => ({
        activity_id: i.activity_id,
        proposed_planned_start: i.proposed_planned_start,
        proposed_planned_finish: i.proposed_planned_finish,
        proposed_duration_days: i.proposed_duration_days,
        proposed_forecast_start: i.proposed_forecast_start,
        proposed_forecast_finish: i.proposed_forecast_finish,
        notes: i.notes,
      })),
    });
    setDecisionNotes("");
    setDrawerOpen(true);
  }

  function addItem() {
    const first = activities[0];
    setForm((prev) => ({
      ...prev,
      items: [
        ...prev.items,
        {
          activity_id: first?.activity_id ?? "",
          proposed_planned_start: null,
          proposed_planned_finish: null,
          proposed_duration_days: null,
          proposed_forecast_finish: null,
          notes: "",
        },
      ],
    }));
  }

  function updateItem(index: number, patch: Partial<ScheduleChangeItem>) {
    setForm((prev) => ({
      ...prev,
      items: prev.items.map((item, i) => (i === index ? { ...item, ...patch } : item)),
    }));
  }

  function removeItem(index: number) {
    setForm((prev) => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index),
    }));
  }

  const isDraft = !selected || selected.status === "draft";
  const isSubmitted = selected?.status === "submitted";
  const editable = canEdit && isDraft;

  return (
    <section className="space-y-3 rounded-lg border p-4" data-testid="change-request-panel">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-base font-medium">{t("schedule.changeRequests")}</h2>
        {canEdit ? (
          <Button size="sm" onClick={openNew}>
            {t("schedule.changeRequestNew")}
          </Button>
        ) : null}
      </div>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
      ) : requests.length === 0 ? (
        <p className="text-sm text-muted-foreground">{t("schedule.changeRequestEmpty")}</p>
      ) : (
        <ul className="divide-y rounded-md border text-sm">
          {requests.map((row) => (
            <li key={row.id}>
              <button
                type="button"
                className="flex w-full items-center justify-between gap-3 px-3 py-2 text-start hover:bg-muted/40"
                onClick={() => openExisting(row)}
              >
                <span className="truncate">
                  {row.reason?.trim() || row.id.slice(0, 8)}
                </span>
                <span className="shrink-0 text-muted-foreground">
                  {statusLabel(t, row.status)}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}

      <Drawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={
          selected
            ? `${t("schedule.changeRequests")} — ${statusLabel(t, selected.status)}`
            : t("schedule.changeRequestNew")
        }
        footer={
          <div className="flex flex-wrap justify-end gap-2">
            <Button variant="secondary" onClick={() => setDrawerOpen(false)}>
              {t("common.close")}
            </Button>
            {editable && !selected ? (
              <Button
                onClick={() => createMut.mutate()}
                disabled={createMut.isPending}
              >
                {t("common.save")}
              </Button>
            ) : null}
            {editable && selected ? (
              <>
                <Button
                  variant="secondary"
                  onClick={() => updateMut.mutate()}
                  disabled={updateMut.isPending}
                >
                  {t("common.save")}
                </Button>
                <Button
                  onClick={() => submitMut.mutate()}
                  disabled={submitMut.isPending}
                >
                  {t("schedule.changeRequestSubmit")}
                </Button>
              </>
            ) : null}
            {canEdit && isSubmitted ? (
              <>
                <Button
                  variant="secondary"
                  onClick={() => rejectMut.mutate()}
                  disabled={rejectMut.isPending}
                >
                  {t("schedule.changeRequestReject")}
                </Button>
                <Button
                  onClick={() => approveMut.mutate()}
                  disabled={approveMut.isPending}
                >
                  {t("schedule.changeRequestApprove")}
                </Button>
              </>
            ) : null}
          </div>
        }
      >
        <div className="space-y-4">
          {(
            [
              ["reason", "schedule.changeRequestReason"],
              ["milestone_impact", "schedule.changeRequestMilestoneImpact"],
              ["cost_impact", "schedule.changeRequestCostImpact"],
              ["contract_impact", "schedule.changeRequestContractImpact"],
            ] as const
          ).map(([field, labelKey]) => (
            <TextArea
              key={field}
              name={`scr_${field}`}
              label={t(labelKey)}
              value={form[field]}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, [field]: e.target.value }))
              }
              disabled={!editable}
              rows={2}
            />
          ))}

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium">{t("schedule.changeRequestItems")}</h3>
              {editable ? (
                <Button size="sm" variant="secondary" onClick={addItem}>
                  {t("schedule.addItem")}
                </Button>
              ) : null}
            </div>
            {form.items.length === 0 ? (
              <p className="text-xs text-muted-foreground">{t("common.empty")}</p>
            ) : (
              form.items.map((item, index) => (
                <div
                  key={`${item.activity_id}-${index}`}
                  className="space-y-2 rounded-md border p-3"
                >
                  <div className="space-y-1">
                    <Label>{t("schedule.selectActivity")}</Label>
                    <select
                      className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
                      value={item.activity_id}
                      disabled={!editable}
                      onChange={(e) =>
                        updateItem(index, { activity_id: e.target.value })
                      }
                    >
                      <option value="">{t("schedule.selectActivity")}</option>
                      {activities.map((a) => (
                        <option key={a.activity_id} value={a.activity_id}>
                          {a.activity_code} — {a.activity_name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="space-y-1">
                      <Label>{t("schedule.proposedPlannedStart")}</Label>
                      <JalaliDatePicker
                        name={`scr_ps_${index}`}
                        value={item.proposed_planned_start ?? ""}
                        onChange={(v) =>
                          updateItem(index, { proposed_planned_start: v || null })
                        }
                        disabled={!editable}
                      />
                    </div>
                    <div className="space-y-1">
                      <Label>{t("schedule.proposedPlannedFinish")}</Label>
                      <JalaliDatePicker
                        name={`scr_pf_${index}`}
                        value={item.proposed_planned_finish ?? ""}
                        onChange={(v) =>
                          updateItem(index, { proposed_planned_finish: v || null })
                        }
                        disabled={!editable}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="space-y-1">
                      <Label>{t("schedule.proposedDuration")}</Label>
                      <Input
                        type="number"
                        value={
                          item.proposed_duration_days != null
                            ? String(item.proposed_duration_days)
                            : ""
                        }
                        disabled={!editable}
                        onChange={(e) => {
                          const raw = e.target.value;
                          updateItem(index, {
                            proposed_duration_days:
                              raw === "" ? null : Number.parseInt(raw, 10),
                          });
                        }}
                      />
                    </div>
                    <div className="space-y-1">
                      <Label>{t("schedule.proposedForecastFinish")}</Label>
                      <JalaliDatePicker
                        name={`scr_ff_${index}`}
                        value={item.proposed_forecast_finish ?? ""}
                        onChange={(v) =>
                          updateItem(index, {
                            proposed_forecast_finish: v || null,
                          })
                        }
                        disabled={!editable}
                      />
                    </div>
                  </div>
                  {editable ? (
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => removeItem(index)}
                    >
                      {t("common.delete")}
                    </Button>
                  ) : null}
                </div>
              ))
            )}
          </div>

          {canEdit && isSubmitted ? (
            <TextArea
              name="scr_decision_notes"
              label={t("schedule.changeRequestDecisionNotes")}
              value={decisionNotes}
              onChange={(e) => setDecisionNotes(e.target.value)}
              rows={2}
            />
          ) : null}

          {selected?.decision_notes ? (
            <p className="text-sm text-muted-foreground">
              {t("schedule.changeRequestDecisionNotes")}: {selected.decision_notes}
            </p>
          ) : null}
        </div>
      </Drawer>
    </section>
  );
}
