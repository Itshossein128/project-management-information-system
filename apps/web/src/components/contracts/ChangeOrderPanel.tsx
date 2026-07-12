import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import {
  approveChangeOrder,
  createChangeOrder,
  formatFaAmount,
  type ChangeOrderRow,
} from "@/app/lib/api/contracts";
import { Input, TextArea } from "@/components/form";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

export function ChangeOrderPanel({
  projectId,
  contractId,
  changeOrders,
  canEdit,
  onChanged,
}: {
  projectId: string;
  contractId: string;
  changeOrders: ChangeOrderRow[];
  canEdit: boolean;
  onChanged: () => void;
}) {
  const toast = useToast();
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");

  const create = useMutation({
    mutationFn: () =>
      createChangeOrder(projectId, contractId, {
        description,
        amount_change: Number(amount) || 0,
      }),
    onSuccess: () => {
      toast.success("تغییر مقادیر ثبت شد");
      setDescription("");
      setAmount("");
      onChanged();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const approve = useMutation({
    mutationFn: (id: string) => approveChangeOrder(projectId, contractId, id),
    onSuccess: () => {
      toast.success("تغییر مقادیر تأیید شد");
      onChanged();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <div className="space-y-4">
      {canEdit ? (
        <div className="rounded-lg border p-4 space-y-3">
          <h3 className="font-medium">ثبت تغییر مقادیر</h3>
          <div>
            <Label className="mb-1 block text-sm">شرح</Label>
            <TextArea
              name="co_desc"
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div>
            <Label className="mb-1 block text-sm">مبلغ تغییر</Label>
            <Input
              name="co_amount"
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
          </div>
          <Button
            variant="primary"
            size="sm"
            loading={create.isPending}
            onClick={() => create.mutate()}
          >
            ثبت
          </Button>
        </div>
      ) : null}

      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              {["شماره", "شرح", "مبلغ", "وضعیت", "عملیات"].map((h) => (
                <th key={h} className="px-3 py-2 text-start">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {changeOrders.map((co) => (
              <tr key={co.id} className="border-t">
                <td className="px-3 py-2">{co.change_number}</td>
                <td className="px-3 py-2">{co.description}</td>
                <td className="px-3 py-2">{formatFaAmount(co.amount_change)}</td>
                <td className="px-3 py-2">{co.status}</td>
                <td className="px-3 py-2">
                  {canEdit && co.status === "draft" ? (
                    <Button
                      size="sm"
                      variant="secondary"
                      loading={approve.isPending}
                      onClick={() => approve.mutate(co.id)}
                    >
                      تأیید
                    </Button>
                  ) : (
                    "—"
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
