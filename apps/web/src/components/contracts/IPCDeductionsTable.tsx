import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import {
  addIPCDeduction,
  deleteIPCDeduction,
  DEDUCTION_TYPE_LABELS,
  formatFaAmount,
  type IPCDetail,
} from "@/app/lib/api/contracts";
import { Input } from "@/components/form";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

const AUTO_TYPES = new Set(["retention", "tax", "insurance", "advance_recovery"]);

export function IPCDeductionsTable({
  projectId,
  ipc,
  canEdit,
  onUpdated,
}: {
  projectId: string;
  ipc: IPCDetail;
  canEdit: boolean;
  onUpdated: () => void;
}) {
  const toast = useToast();
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [deductionType, setDeductionType] = useState("other");

  const add = useMutation({
    mutationFn: () =>
      addIPCDeduction(projectId, ipc.id, {
        deduction_type: deductionType,
        amount: Number(amount) || 0,
        description,
      }),
    onSuccess: () => {
      toast.success("کسر اضافه شد");
      setAmount("");
      setDescription("");
      onUpdated();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const remove = useMutation({
    mutationFn: (id: string) => deleteIPCDeduction(projectId, ipc.id, id),
    onSuccess: () => {
      toast.success("کسر حذف شد");
      onUpdated();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              {["نوع", "شرح", "مبلغ", "عملیات"].map((h) => (
                <th key={h} className="px-3 py-2 text-start">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ipc.deductions.map((d) => (
              <tr key={d.id} className="border-t">
                <td className="px-3 py-2">{DEDUCTION_TYPE_LABELS[d.deduction_type] ?? d.deduction_type}</td>
                <td className="px-3 py-2">{d.description}</td>
                <td className="px-3 py-2">{formatFaAmount(d.amount)}</td>
                <td className="px-3 py-2">
                  {!AUTO_TYPES.has(d.deduction_type) && canEdit ? (
                    <Button
                      size="sm"
                      variant="secondary"
                      loading={remove.isPending}
                      onClick={() => remove.mutate(d.id)}
                    >
                      حذف
                    </Button>
                  ) : (
                    "—"
                  )}
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot className="border-t bg-muted/30 font-semibold">
            <tr>
              <td colSpan={2} className="px-3 py-2">
                جمع کسورات
              </td>
              <td className="px-3 py-2">{formatFaAmount(ipc.deductions_total)}</td>
              <td />
            </tr>
          </tfoot>
        </table>
      </div>

      {canEdit ? (
        <div className="rounded-lg border p-4 grid gap-3 md:grid-cols-4 items-end">
          <div>
            <Label className="mb-1 block text-sm">نوع کسر دستی</Label>
            <select
              className="w-full rounded border px-2 py-2 text-sm"
              value={deductionType}
              onChange={(e) => setDeductionType(e.target.value)}
            >
              <option value="material_price_diff">اختلاف قیمت مصالح</option>
              <option value="other">سایر</option>
            </select>
          </div>
          <div>
            <Label className="mb-1 block text-sm">مبلغ</Label>
            <Input
              name="ded_amount"
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
          </div>
          <div>
            <Label className="mb-1 block text-sm">شرح</Label>
            <Input
              name="ded_desc"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <Button variant="primary" size="sm" loading={add.isPending} onClick={() => add.mutate()}>
            افزودن کسر
          </Button>
        </div>
      ) : null}
    </div>
  );
}
