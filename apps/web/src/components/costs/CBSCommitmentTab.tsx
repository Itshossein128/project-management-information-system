import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  asList,
  createCBSNode,
  createCommitment,
  fetchCBS,
  fetchCommitments,
} from "@/app/lib/api/central-data";
import { formatFaAmount } from "@/app/lib/api/costs";
import { Input, Label } from "@/components/form";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

export function CBSCommitmentTab({
  projectId,
  canEdit,
}: {
  projectId: string;
  canEdit: boolean;
}) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const [cbsCode, setCbsCode] = useState("");
  const [cbsName, setCbsName] = useState("");
  const [cmNumber, setCmNumber] = useState("");
  const [cmAmount, setCmAmount] = useState("");
  const [cmDate, setCmDate] = useState("");
  const [cmCbs, setCmCbs] = useState("");
  const [cmPaymentTerms, setCmPaymentTerms] = useState("");

  const cbsQuery = useQuery({
    queryKey: ["cbs", projectId],
    queryFn: () => fetchCBS(projectId),
  });
  const cmQuery = useQuery({
    queryKey: ["commitments", projectId],
    queryFn: () => fetchCommitments(projectId),
  });

  const addCbs = useMutation({
    mutationFn: () =>
      createCBSNode(projectId, { cbs_code: cbsCode, cbs_name: cbsName }),
    onSuccess: () => {
      toast.success(t("centralData.cbsCreated", "گره CBS ایجاد شد"));
      setCbsCode("");
      setCbsName("");
      void qc.invalidateQueries({ queryKey: ["cbs", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const addCm = useMutation({
    mutationFn: () =>
      createCommitment(projectId, {
        commitment_number: cmNumber,
        amount: cmAmount,
        commitment_date: cmDate,
        cbs: cmCbs || undefined,
        payment_terms: cmPaymentTerms || undefined,
      }),
    onSuccess: () => {
      toast.success(t("centralData.commitmentCreated", "تعهد ثبت شد"));
      setCmNumber("");
      setCmAmount("");
      setCmDate("");
      setCmCbs("");
      setCmPaymentTerms("");
      void qc.invalidateQueries({ queryKey: ["commitments", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const nodes = cbsQuery.data ?? [];
  const commitments = asList(cmQuery.data ?? []);

  return (
    <div className="grid gap-8 md:grid-cols-2">
      <section className="space-y-3">
        <h3 className="font-medium">{t("glossary.cbs")}</h3>
        <ul className="space-y-1 text-sm">
          {nodes.map((n) => (
            <li key={n.id}>
              {"—".repeat(Math.max(0, n.depth - 1))} {n.cbs_code} — {n.cbs_name}
            </li>
          ))}
        </ul>
        {canEdit ? (
          <div className="flex flex-wrap gap-2">
            <Input
              placeholder={t("centralData.cbsCode", "کد")}
              value={cbsCode}
              onChange={(e) => setCbsCode(e.target.value)}
            />
            <Input
              placeholder={t("centralData.cbsName", "نام")}
              value={cbsName}
              onChange={(e) => setCbsName(e.target.value)}
            />
            <Button
              variant="secondary"
              loading={addCbs.isPending}
              disabled={!cbsCode || !cbsName}
              onClick={() => addCbs.mutate()}
            >
              {t("common.add", "افزودن")}
            </Button>
          </div>
        ) : null}
      </section>

      <section className="space-y-3">
        <h3 className="font-medium">{t("glossary.commitment")}</h3>
        <ul className="space-y-1 text-sm">
          {commitments.map((c) => (
            <li key={c.id} className="flex flex-col gap-0.5 text-sm">
              <div className="flex justify-between gap-2">
                <span>
                  {c.commitment_number} ({c.status})
                </span>
                <span>
                  {formatFaAmount(Number(c.amount))} /{" "}
                  {t("centralData.remaining", "مانده")}{" "}
                  {formatFaAmount(Number(c.remaining))}
                </span>
              </div>
              {c.payment_terms ? (
                <span className="text-muted-foreground text-xs">
                  {t("centralData.paymentTerms", "شرایط پرداخت")}: {c.payment_terms}
                </span>
              ) : null}
            </li>
          ))}
        </ul>
        {canEdit ? (
          <div className="space-y-2">
            <Label>{t("centralData.commitmentNumber", "شماره تعهد")}</Label>
            <Input value={cmNumber} onChange={(e) => setCmNumber(e.target.value)} />
            <Label>{t("centralData.amount", "مبلغ")}</Label>
            <Input value={cmAmount} onChange={(e) => setCmAmount(e.target.value)} />
            <Label>{t("centralData.date", "تاریخ")}</Label>
            <Input type="date" value={cmDate} onChange={(e) => setCmDate(e.target.value)} />
            <Label>{t("centralData.paymentTerms", "شرایط پرداخت")}</Label>
            <textarea
              className="w-full rounded border px-2 py-2 text-sm"
              rows={2}
              value={cmPaymentTerms}
              onChange={(e) => setCmPaymentTerms(e.target.value)}
            />
            <Label>{t("glossary.cbs")}</Label>
            <select
              className="w-full rounded border px-2 py-2 text-sm"
              value={cmCbs}
              onChange={(e) => setCmCbs(e.target.value)}
            >
              <option value="">{t("common.optional", "اختیاری")}</option>
              {nodes.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.cbs_code}
                </option>
              ))}
            </select>
            <Button
              variant="secondary"
              loading={addCm.isPending}
              disabled={!cmNumber || !cmAmount || !cmDate}
              onClick={() => addCm.mutate()}
            >
              {t("common.add", "افزودن")}
            </Button>
          </div>
        ) : null}
      </section>
    </div>
  );
}
