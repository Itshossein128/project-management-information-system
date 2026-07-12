import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import {
  formatFaAmount,
  updateIPCItem,
  type IPCDetail,
} from "@/app/lib/api/contracts";
import { useToast } from "@/components/ui/toast";

export function IPCLineItemsTable({
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
  const [editingId, setEditingId] = useState<string | null>(null);
  const [draftQty, setDraftQty] = useState("");

  const save = useMutation({
    mutationFn: ({ itemId, qty }: { itemId: string; qty: number }) =>
      updateIPCItem(projectId, ipc.id, itemId, qty),
    onSuccess: () => {
      toast.success("مقدار به‌روز شد");
      setEditingId(null);
      onUpdated();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <div className="overflow-x-auto rounded-lg border">
      <table className="w-full min-w-[700px] text-sm">
        <thead className="bg-muted/50">
          <tr>
            {["شرح", "واحد", "قیمت واحد", "قبلی", "جاری", "تجمعی", "مبلغ جاری"].map((h) => (
              <th key={h} className="px-3 py-2 text-start">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {ipc.items.map((item) => (
            <tr key={item.id} className="border-t">
              <td className="px-3 py-2">{item.description}</td>
              <td className="px-3 py-2">{item.unit}</td>
              <td className="px-3 py-2">{formatFaAmount(item.unit_price)}</td>
              <td className="px-3 py-2">{item.qty_previous}</td>
              <td className="px-3 py-2">
                {canEdit && editingId === item.id ? (
                  <input
                    autoFocus
                    className="w-20 rounded border px-1 py-0.5 text-xs"
                    type="number"
                    value={draftQty}
                    onBlur={() => {
                      save.mutate({ itemId: item.id, qty: Number(draftQty) || 0 });
                    }}
                    onChange={(e) => setDraftQty(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") (e.target as HTMLInputElement).blur();
                    }}
                  />
                ) : (
                  <button
                    type="button"
                    className="hover:underline disabled:cursor-default"
                    disabled={!canEdit}
                    onClick={() => {
                      setEditingId(item.id);
                      setDraftQty(String(item.qty_current));
                    }}
                  >
                    {item.qty_current}
                  </button>
                )}
              </td>
              <td className="px-3 py-2">{item.qty_cumulative}</td>
              <td className="px-3 py-2">{formatFaAmount(item.amount_current)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
