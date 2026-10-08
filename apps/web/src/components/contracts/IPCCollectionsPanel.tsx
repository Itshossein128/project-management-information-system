import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  addIPCCollection,
  fetchIPCCollections,
} from "@/app/lib/api/central-data";
import { formatFaAmount } from "@/app/lib/api/contracts";
import { Input, Label } from "@/components/form";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

export function IPCCollectionsPanel({
  projectId,
  ipcId,
  canEdit,
}: {
  projectId: string;
  ipcId: string;
  canEdit: boolean;
}) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const [amount, setAmount] = useState("");
  const [collectedAt, setCollectedAt] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["ipc-collections", projectId, ipcId],
    queryFn: () => fetchIPCCollections(projectId, ipcId),
    enabled: Boolean(projectId && ipcId),
  });

  const add = useMutation({
    mutationFn: () =>
      addIPCCollection(projectId, ipcId, {
        amount,
        collected_at: collectedAt,
      }),
    onSuccess: () => {
      toast.success(t("centralData.collectionAdded", "وصول ثبت شد"));
      setAmount("");
      setCollectedAt("");
      void qc.invalidateQueries({ queryKey: ["ipc-collections", projectId, ipcId] });
      void qc.invalidateQueries({ queryKey: ["ipc", projectId, ipcId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (isLoading) return null;

  return (
    <section className="space-y-3">
      <h2 className="text-lg font-medium">
        {t("centralData.collections", "وصول‌های جزئی")}
      </h2>
      <p className="text-sm text-muted-foreground">
        {t("centralData.collectionsHint", "مبالغ اصلی IPC تغییر نمی‌کند.")}{" "}
        {t("centralData.remaining", "مانده")}:{" "}
        {formatFaAmount(Number(data?.remaining_receivable ?? 0))}
      </p>
      <ul className="space-y-1 text-sm">
        {(data?.results ?? []).map((row) => (
          <li key={row.id} className="flex justify-between border-b py-1">
            <span>{row.collected_at}</span>
            <span>{formatFaAmount(Number(row.amount))}</span>
          </li>
        ))}
      </ul>
      {canEdit ? (
        <div className="flex flex-wrap items-end gap-2">
          <div>
            <Label>{t("centralData.amount", "مبلغ")}</Label>
            <Input value={amount} onChange={(e) => setAmount(e.target.value)} />
          </div>
          <div>
            <Label>{t("centralData.collectedAt", "تاریخ وصول")}</Label>
            <Input
              type="date"
              value={collectedAt}
              onChange={(e) => setCollectedAt(e.target.value)}
            />
          </div>
          <Button
            variant="primary"
            loading={add.isPending}
            disabled={!amount || !collectedAt}
            onClick={() => add.mutate()}
          >
            {t("centralData.addCollection", "ثبت وصول")}
          </Button>
        </div>
      ) : null}
    </section>
  );
}
