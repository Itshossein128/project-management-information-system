import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  estimateLaborCost,
  listResults,
} from "@/app/lib/api/hr-capacity";
import { apiJson } from "@/app/lib/api-client";
import { PATHS } from "@/app/routeVars";
import type { ProjectMember } from "@/app/lib/api/members";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

type RateRow = {
  id: string;
  person_id: string | null;
  amount?: string;
  currency: string;
  effective_from: string;
  effective_to: string | null;
};

type Props = {
  projectId: string;
  members: ProjectMember[];
  canViewWage: boolean;
  canEditWage: boolean;
};

export function LaborRatesPanel({
  projectId,
  members,
  canViewWage,
  canEditWage,
}: Props) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const [personId, setPersonId] = useState("");
  const [hours, setHours] = useState("8");
  const [amount, setAmount] = useState("");
  const [from, setFrom] = useState("");
  const [estimateResult, setEstimateResult] = useState<string | null>(null);

  const ratesQ = useQuery({
    queryKey: ["approved-labor-rates", projectId],
    queryFn: () =>
      apiJson<{ results: RateRow[] } | RateRow[]>(
        `/${PATHS.API_PROJECTS}/${projectId}/approved-labor-rates/`,
      ),
  });

  const createRate = useMutation({
    mutationFn: () =>
      apiJson(`/${PATHS.API_PROJECTS}/${projectId}/approved-labor-rates/`, {
        method: "POST",
        body: JSON.stringify({
          person_id: personId || null,
          amount,
          currency: "IRR",
          effective_from: from,
        }),
      }),
    onSuccess: () => {
      toast.success(t("hr.capacity.rateSaved"));
      void qc.invalidateQueries({ queryKey: ["approved-labor-rates", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const estimate = useMutation({
    mutationFn: () =>
      estimateLaborCost(projectId, {
        person_id: personId,
        approved_hours: hours,
      }),
    onSuccess: (data) => {
      if (data.warning === "missing_approved_rate") {
        setEstimateResult(t("hr.capacity.missingApprovedRate"));
        return;
      }
      setEstimateResult(
        data.amount
          ? `${data.amount} ${data.currency ?? ""}`
          : t("hr.capacity.wageHidden"),
      );
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const rates = listResults(ratesQ.data);
  const people = members.filter((m) => m.user_id);

  return (
    <section className="space-y-3 rounded-md border p-3">
      <h2 className="text-lg font-semibold">{t("hr.capacity.ratesTitle")}</h2>
      {!canViewWage && (
        <p className="text-sm text-muted-foreground">{t("hr.capacity.wageHidden")}</p>
      )}
      <ul className="space-y-1 text-sm">
        {rates.map((r) => (
          <li key={r.id}>
            {r.person_id?.slice(0, 8) ?? "—"} · {r.effective_from}
            {canViewWage && r.amount != null ? ` · ${r.amount} ${r.currency}` : ""}
          </li>
        ))}
      </ul>
      <div className="grid gap-2 md:grid-cols-2">
        <select
          className="rounded-md border bg-background px-2 py-1.5 text-sm"
          value={personId}
          onChange={(e) => setPersonId(e.target.value)}
        >
          <option value="">{t("hr.capacity.selectPerson")}</option>
          {people.map((m) => (
            <option key={m.user_id!} value={m.user_id!}>
              {m.full_name || m.user_id}
            </option>
          ))}
        </select>
        <input
          type="number"
          className="rounded-md border bg-background px-2 py-1.5 text-sm"
          placeholder={t("hr.capacity.approvedHours")}
          value={hours}
          onChange={(e) => setHours(e.target.value)}
        />
      </div>
      <div className="flex flex-wrap gap-2">
        <Button
          size="sm"
          variant="secondary"
          disabled={!personId || estimate.isPending}
          onClick={() => estimate.mutate()}
        >
          {t("hr.capacity.estimate")}
        </Button>
        {estimateResult && <span className="text-sm self-center">{estimateResult}</span>}
      </div>
      {canEditWage && (
        <div className="grid gap-2 border-t pt-3 md:grid-cols-3">
          <input
            type="number"
            className="rounded-md border bg-background px-2 py-1.5 text-sm"
            placeholder={t("hr.capacity.rateAmount")}
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
          <input
            type="date"
            className="rounded-md border bg-background px-2 py-1.5 text-sm"
            value={from}
            onChange={(e) => setFrom(e.target.value)}
          />
          <Button
            size="sm"
            disabled={!amount || !from || createRate.isPending}
            onClick={() => createRate.mutate()}
          >
            {t("hr.capacity.saveRate")}
          </Button>
        </div>
      )}
    </section>
  );
}
