import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { usePermission } from "@/app/contexts/project-context";
import { fetchKickoffCharter, saveKickoffCharter, type KickoffCharter } from "@/app/lib/api/projects";
import { useToast } from "@/components/ui/toast";

const EMPTY: KickoffCharter = {
  justification: "",
  success_criteria: "",
  constraints: "",
  assumptions: "",
  key_stakeholders_summary: "",
  pm_authority: "",
};

interface Props {
  projectId: string;
}

export function KickoffCharterPanel({ projectId }: Props) {
  const { t } = useTranslation();
  const toast = useToast();
  const queryClient = useQueryClient();
  const { has } = usePermission(projectId);
  const canEdit = has("edit_project");
  const [form, setForm] = useState<KickoffCharter>(EMPTY);

  const query = useQuery({
    queryKey: ["kickoff-charter", projectId],
    queryFn: async () => {
      try {
        return await fetchKickoffCharter(projectId);
      } catch {
        return EMPTY;
      }
    },
  });

  const loaded = query.data ?? EMPTY;
  const values = {
    justification: form.justification || loaded.justification,
    success_criteria: form.success_criteria || loaded.success_criteria,
    constraints: form.constraints || loaded.constraints,
    assumptions: form.assumptions || loaded.assumptions,
    key_stakeholders_summary: form.key_stakeholders_summary || loaded.key_stakeholders_summary,
    pm_authority: form.pm_authority || loaded.pm_authority,
  };

  const save = useMutation({
    mutationFn: () => saveKickoffCharter(projectId, values),
    onSuccess: () => {
      toast.success(t("common.saved", "ذخیره شد"));
      void queryClient.invalidateQueries({ queryKey: ["kickoff-charter", projectId] });
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const fields: { key: keyof KickoffCharter; label: string }[] = [
    { key: "justification", label: t("project.charterJustification", "توجیه") },
    { key: "success_criteria", label: t("project.charterSuccess", "معیار موفقیت") },
    { key: "constraints", label: t("project.charterConstraints", "محدودیت‌ها") },
    { key: "assumptions", label: t("project.charterAssumptions", "فرضیات") },
    { key: "key_stakeholders_summary", label: t("project.charterStakeholders", "ذی‌نفعان کلیدی") },
    { key: "pm_authority", label: t("project.charterAuthority", "اختیار مدیر پروژه") },
  ];

  return (
    <div className="mb-8 rounded-lg border border-border p-4" data-testid="kickoff-charter-panel">
      <h2 className="mb-3 text-lg font-semibold">{t("project.charter")}</h2>
      <div className="space-y-3">
        {fields.map(({ key, label }) => (
          <div key={key}>
            <label className="mb-1 block text-sm text-muted-foreground">{label}</label>
            <textarea
              className="min-h-[64px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm"
              disabled={!canEdit}
              value={values[key]}
              onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
            />
          </div>
        ))}
      </div>
      {canEdit ? (
        <div className="mt-3 flex justify-end">
          <button
            type="button"
            disabled={save.isPending}
            className="rounded-md bg-primary px-3 py-1.5 text-sm text-primary-foreground disabled:opacity-50"
            onClick={() => save.mutate()}
          >
            {t("common.save", "ذخیره")}
          </button>
        </div>
      ) : null}
    </div>
  );
}
