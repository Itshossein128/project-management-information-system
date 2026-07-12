import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { fetchActivities } from "@/app/lib/api/activities";
import {
  bulkContractItems,
  formatFaAmount,
  type ContractItemRow,
} from "@/app/lib/api/contracts";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

interface BoQLine {
  id?: string;
  activity: string;
  boq_code: string;
  description: string;
  unit_price: string;
  quantity: string;
}

function toLine(row: ContractItemRow): BoQLine {
  return {
    id: row.id,
    activity: row.activity ?? "",
    boq_code: row.boq_code,
    description: row.description,
    unit_price: String(row.unit_price ?? ""),
    quantity: String(row.quantity ?? ""),
  };
}

export function ContractBoQGrid({
  projectId,
  contractId,
  items,
  canEdit,
  onSaved,
}: {
  projectId: string;
  contractId: string;
  items: ContractItemRow[];
  canEdit: boolean;
  onSaved: () => void;
}) {
  const toast = useToast();
  const [lines, setLines] = useState<BoQLine[]>(() =>
    items.length ? items.map(toLine) : [{ activity: "", boq_code: "", description: "", unit_price: "", quantity: "" }],
  );

  const { data: activitiesData } = useQuery({
    queryKey: ["activities", projectId, "boq"],
    queryFn: () => fetchActivities(projectId, { per_page: 500 }),
  });
  const activities = activitiesData?.results ?? [];

  const save = useMutation({
    mutationFn: () =>
      bulkContractItems(
        projectId,
        contractId,
        lines
          .filter((l) => l.description.trim() || l.boq_code.trim())
          .map((l) => ({
            ...(l.id ? { id: l.id } : {}),
            activity: l.activity || null,
            boq_code: l.boq_code,
            description: l.description,
            unit_price: l.unit_price ? Number(l.unit_price) : 0,
            quantity: l.quantity ? Number(l.quantity) : 0,
          })),
      ),
    onSuccess: () => {
      toast.success("فهرست بها ذخیره شد");
      onSaved();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const updateLine = (idx: number, patch: Partial<BoQLine>) => {
    setLines((prev) => prev.map((l, i) => (i === idx ? { ...l, ...patch } : l)));
  };

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full min-w-[800px] text-sm">
          <thead className="bg-muted/50">
            <tr>
              {["کد BOQ", "شرح", "فعالیت", "قیمت واحد", "مقدار", "جمع"].map((h) => (
                <th key={h} className="px-3 py-2 text-start">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {lines.map((line, idx) => {
              const total =
                (Number(line.unit_price) || 0) * (Number(line.quantity) || 0);
              return (
                <tr key={line.id ?? idx} className="border-t">
                  <td className="px-2 py-1">
                    <input
                      className="w-full rounded border px-2 py-1 text-xs"
                      disabled={!canEdit}
                      value={line.boq_code}
                      onChange={(e) => updateLine(idx, { boq_code: e.target.value })}
                    />
                  </td>
                  <td className="px-2 py-1">
                    <input
                      className="w-full rounded border px-2 py-1 text-xs"
                      disabled={!canEdit}
                      value={line.description}
                      onChange={(e) => updateLine(idx, { description: e.target.value })}
                    />
                  </td>
                  <td className="px-2 py-1">
                    <select
                      className="w-full rounded border px-2 py-1 text-xs"
                      disabled={!canEdit}
                      value={line.activity}
                      onChange={(e) => updateLine(idx, { activity: e.target.value })}
                    >
                      <option value="">—</option>
                      {activities.map((a) => (
                        <option key={a.activity_id} value={a.activity_id}>
                          {a.activity_code} — {a.activity_name}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="px-2 py-1">
                    <input
                      className="w-24 rounded border px-2 py-1 text-xs"
                      type="number"
                      disabled={!canEdit}
                      value={line.unit_price}
                      onChange={(e) => updateLine(idx, { unit_price: e.target.value })}
                    />
                  </td>
                  <td className="px-2 py-1">
                    <input
                      className="w-24 rounded border px-2 py-1 text-xs"
                      type="number"
                      disabled={!canEdit}
                      value={line.quantity}
                      onChange={(e) => updateLine(idx, { quantity: e.target.value })}
                    />
                  </td>
                  <td className="px-3 py-1">{total ? formatFaAmount(total) : "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {canEdit ? (
        <div className="flex gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() =>
              setLines((prev) => [
                ...prev,
                { activity: "", boq_code: "", description: "", unit_price: "", quantity: "" },
              ])
            }
          >
            ردیف جدید
          </Button>
          <Button variant="primary" size="sm" loading={save.isPending} onClick={() => save.mutate()}>
            ذخیره فهرست بها
          </Button>
        </div>
      ) : null}
    </div>
  );
}
