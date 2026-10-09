import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  asList,
  createPayment,
  fetchCommitments,
  fetchLedgerReport,
  fetchPayments,
} from "@/app/lib/api/central-data";
import { formatFaAmount } from "@/app/lib/api/costs";
import { Input, Label } from "@/components/form";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

export function CostPaymentsLedgerPanel({
  projectId,
  canEdit,
}: {
  projectId: string;
  canEdit: boolean;
}) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const [commitmentId, setCommitmentId] = useState("");
  const [amount, setAmount] = useState("");
  const [paidAt, setPaidAt] = useState("");
  const [documentRef, setDocumentRef] = useState("");
  const [exceptionReason, setExceptionReason] = useState("");
  const [needsException, setNeedsException] = useState(false);

  const cmQuery = useQuery({
    queryKey: ["commitments", projectId],
    queryFn: () => fetchCommitments(projectId),
  });
  const payQuery = useQuery({
    queryKey: ["payments", projectId],
    queryFn: () => fetchPayments(projectId),
  });
  const ledgerQuery = useQuery({
    queryKey: ["ledger-report", projectId],
    queryFn: () => fetchLedgerReport(projectId),
  });

  const addPay = useMutation({
    mutationFn: () =>
      createPayment(projectId, {
        commitment: commitmentId || undefined,
        amount,
        paid_at: paidAt,
        document_ref: documentRef || undefined,
        acknowledge_duplicate_exception: needsException || undefined,
        exception_reason: needsException ? exceptionReason : undefined,
      }),
    onSuccess: () => {
      toast.success(t("centralData.paymentCreated", "پرداخت ثبت شد"));
      setAmount("");
      setPaidAt("");
      setDocumentRef("");
      setExceptionReason("");
      setNeedsException(false);
      void qc.invalidateQueries({ queryKey: ["payments", projectId] });
      void qc.invalidateQueries({ queryKey: ["commitments", projectId] });
      void qc.invalidateQueries({ queryKey: ["ledger-report", projectId] });
    },
    onError: (e: Error) => {
      const msg = e.message || "";
      if (msg.includes("duplicate_payment_document")) {
        setNeedsException(true);
        toast.error(
          t(
            "centralData.duplicatePayment",
            "پرداخت تکراری برای این مدرک — در صورت تأیید استثنا، دلیل را وارد کنید",
          ),
        );
        return;
      }
      toast.error(msg);
    },
  });

  const commitments = asList(cmQuery.data ?? []);
  const payments = payQuery.data ?? [];
  const ledgerRows = ledgerQuery.data?.rows ?? [];

  return (
    <div className="grid gap-8 md:grid-cols-2">
      <section className="space-y-3">
        <h3 className="font-medium">{t("centralData.payments", "پرداخت‌ها")}</h3>
        <ul className="space-y-1 text-sm">
          {payments.map((p) => (
            <li key={p.id} className="flex justify-between gap-2">
              <span>
                {p.document_ref || "—"} ({p.status})
              </span>
              <span>{formatFaAmount(Number(p.amount))}</span>
            </li>
          ))}
        </ul>
        {canEdit ? (
          <div className="space-y-2">
            <Label>{t("glossary.commitment")}</Label>
            <select
              className="w-full rounded border px-2 py-2 text-sm"
              value={commitmentId}
              onChange={(e) => setCommitmentId(e.target.value)}
            >
              <option value="">{t("common.select", "انتخاب")}</option>
              {commitments.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.commitment_number}
                </option>
              ))}
            </select>
            <Label>{t("centralData.amount", "مبلغ")}</Label>
            <Input value={amount} onChange={(e) => setAmount(e.target.value)} />
            <Label>{t("centralData.date", "تاریخ")}</Label>
            <Input
              type="date"
              value={paidAt}
              onChange={(e) => setPaidAt(e.target.value)}
            />
            <Label>{t("centralData.documentRef", "شماره مدرک")}</Label>
            <Input
              value={documentRef}
              onChange={(e) => setDocumentRef(e.target.value)}
            />
            {needsException ? (
              <>
                <Label>
                  {t("centralData.exceptionReason", "دلیل استثنای تکراری")}
                </Label>
                <textarea
                  className="w-full rounded border px-2 py-2 text-sm"
                  rows={2}
                  value={exceptionReason}
                  onChange={(e) => setExceptionReason(e.target.value)}
                />
              </>
            ) : null}
            <Button
              variant="secondary"
              loading={addPay.isPending}
              disabled={
                !commitmentId ||
                !amount ||
                !paidAt ||
                (needsException && !exceptionReason)
              }
              onClick={() => addPay.mutate()}
            >
              {t("centralData.recordPayment", "ثبت پرداخت")}
            </Button>
          </div>
        ) : null}
      </section>

      <section className="space-y-3">
        <h3 className="font-medium">
          {t("centralData.ledgerReport", "گزارش تعهد / هزینه / پرداخت")}
        </h3>
        <ul className="max-h-80 space-y-1 overflow-auto text-sm">
          {ledgerRows.map((r) => (
            <li key={`${r.row_type}-${r.id}`} className="flex justify-between gap-2">
              <span>
                [{r.row_type}] {r.document_ref || "—"} ({r.status})
              </span>
              <span>{formatFaAmount(r.amount)}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
