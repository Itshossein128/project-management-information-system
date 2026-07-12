import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate } from "react-router";
import {
  createIPC,
  populateIPC,
  type ContractDetail,
} from "@/app/lib/api/contracts";
import { PATHS } from "@/app/routeVars";
import { JalaliDatePicker } from "@/components/form";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

type Step = 1 | 2;

export function IPCWizard({
  projectId,
  contract,
  isOpen,
  onClose,
}: {
  projectId: string;
  contract: ContractDetail;
  isOpen: boolean;
  onClose: () => void;
}) {
  const toast = useToast();
  const navigate = useNavigate();
  const [step, setStep] = useState<Step>(1);
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");
  const [notes, setNotes] = useState("");

  const create = useMutation({
    mutationFn: async () => {
      const ipc = await createIPC(projectId, {
        contract_id: contract.id,
        period_start: periodStart || null,
        period_end: periodEnd || null,
        notes,
      });
      return populateIPC(projectId, ipc.id);
    },
    onSuccess: (ipc) => {
      toast.success("صدور موقت ایجاد شد");
      onClose();
      navigate(`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_IPCS}/${ipc.id}`);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const reset = () => {
    setStep(1);
    setPeriodStart("");
    setPeriodEnd("");
    setNotes("");
  };

  return (
    <Drawer
      isOpen={isOpen}
      onClose={() => {
        reset();
        onClose();
      }}
      title={`صدور موقت — ${contract.contract_number || contract.counterparty}`}
      footer={
        <div className="flex justify-between gap-2">
          {step === 2 ? (
            <Button variant="secondary" onClick={() => setStep(1)}>
              قبلی
            </Button>
          ) : (
            <span />
          )}
          {step === 1 ? (
            <Button
              variant="primary"
              disabled={!periodStart || !periodEnd}
              onClick={() => setStep(2)}
            >
              بعدی
            </Button>
          ) : (
            <Button variant="primary" loading={create.isPending} onClick={() => create.mutate()}>
              ایجاد و پر کردن خودکار
            </Button>
          )}
        </div>
      }
    >
      {step === 1 ? (
        <div className="space-y-4 p-4">
          <p className="text-sm text-muted-foreground">
            بازه دوره صورت‌وضعیت را انتخاب کنید. مقادیر از پیشرفت تأییدشده فعالیت‌های مرتبط با فهرست بها
            پر می‌شوند.
          </p>
          <JalaliDatePicker
            name="period_start"
            label="شروع دوره"
            value={periodStart}
            onChange={setPeriodStart}
          />
          <JalaliDatePicker
            name="period_end"
            label="پایان دوره"
            value={periodEnd}
            onChange={setPeriodEnd}
          />
        </div>
      ) : (
        <div className="space-y-4 p-4">
          <p className="text-sm">
            قرارداد: <strong>{contract.contract_number}</strong> — {contract.counterparty}
          </p>
          <p className="text-sm text-muted-foreground">
            دوره: {periodStart} تا {periodEnd}
          </p>
          <label className="block text-sm">
            یادداشت
            <textarea
              className="mt-1 w-full rounded border px-3 py-2 text-sm"
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </label>
        </div>
      )}
    </Drawer>
  );
}
