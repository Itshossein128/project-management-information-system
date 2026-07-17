import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { useState } from "react";
import {
  createInflationMapping,
  deleteInflationMapping,
  fetchEconomicSnapshot,
  fetchInflationMappings,
  formatFaAmount,
} from "@/app/lib/api/economic";
import { LoadingSkeleton } from "@/components/layout/page-header";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

export function InflationDetailTable({
  projectId,
  canEdit,
  asOf,
}: {
  projectId: string;
  canEdit: boolean;
  asOf?: string;
}) {
  const toast = useToast();
  const qc = useQueryClient();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [form, setForm] = useState({ cost_category: "", index_name: "", weight: "1" });

  const { data: snapshot, isLoading } = useQuery({
    queryKey: ["economic-snapshot", projectId, asOf],
    queryFn: () => fetchEconomicSnapshot(projectId, asOf),
  });

  const { data: mappings } = useQuery({
    queryKey: ["inflation-mappings", projectId],
    queryFn: () => fetchInflationMappings(projectId),
  });

  const createMut = useMutation({
    mutationFn: () =>
      createInflationMapping(projectId, {
        cost_category: form.cost_category,
        index_name: form.index_name,
        weight: Number(form.weight),
      }),
    onSuccess: () => {
      toast.success("نگاشت ثبت شد");
      setDrawerOpen(false);
      void qc.invalidateQueries({ queryKey: ["inflation-mappings", projectId] });
      void qc.invalidateQueries({ queryKey: ["economic-snapshot", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => deleteInflationMapping(projectId, id),
    onSuccess: () => {
      toast.success("حذف شد");
      void qc.invalidateQueries({ queryKey: ["inflation-mappings", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (isLoading) return <LoadingSkeleton rows={6} />;

  return (
    <div className="space-y-6">
      <div className="rounded-lg border p-4">
        <h3 className="mb-3 font-semibold">تعدیل تورم بر اساس دسته هزینه</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b">
              {["دسته", "اسمی", "تعدیل‌شده", "ضریب"].map((h) => (
                <th key={h} className="py-1 text-start">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(snapshot?.inflation_detail ?? []).map((row) => (
              <tr key={row.cost_category} className="border-b">
                <td className="py-1">{row.cost_category}</td>
                <td className="py-1">{formatFaAmount(row.nominal_cost)}</td>
                <td className="py-1">{formatFaAmount(row.adjusted_cost)}</td>
                <td className="py-1">{row.inflation_factor.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="rounded-lg border p-4">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="font-semibold">نگاشت شاخص تورم</h3>
          {canEdit ? (
            <Button variant="primary" size="sm" onClick={() => setDrawerOpen(true)}>
              <Plus className="size-4" />
              افزودن نگاشت پروژه
            </Button>
          ) : null}
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b">
              {["دسته", "شاخص", "وزن", "نوع", "عملیات"].map((h) => (
                <th key={h} className="py-1 text-start">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(mappings?.results ?? []).map((m) => (
              <tr key={m.id} className="border-b">
                <td className="py-1">{m.cost_category}</td>
                <td className="py-1">{m.index_name}</td>
                <td className="py-1">{m.weight}</td>
                <td className="py-1">{m.is_global ? "سراسری" : "پروژه"}</td>
                <td className="py-1">
                  {canEdit && !m.is_global ? (
                    <Button variant="ghost" size="sm" onClick={() => deleteMut.mutate(m.id)}>
                      حذف
                    </Button>
                  ) : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Drawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title="نگاشت تورم پروژه"
        footer={
          <Button variant="primary" loading={createMut.isPending} onClick={() => createMut.mutate()}>
            ذخیره
          </Button>
        }
      >
        <div className="flex flex-col gap-3 p-4">
          <label className="text-sm">
            دسته هزینه
            <input
              className="mt-1 w-full rounded-md border px-2 py-2"
              value={form.cost_category}
              onChange={(e) => setForm((f) => ({ ...f, cost_category: e.target.value }))}
            />
          </label>
          <label className="text-sm">
            نام شاخص
            <input
              className="mt-1 w-full rounded-md border px-2 py-2"
              value={form.index_name}
              onChange={(e) => setForm((f) => ({ ...f, index_name: e.target.value }))}
            />
          </label>
          <label className="text-sm">
            وزن
            <input
              type="number"
              step="0.01"
              className="mt-1 w-full rounded-md border px-2 py-2"
              value={form.weight}
              onChange={(e) => setForm((f) => ({ ...f, weight: e.target.value }))}
            />
          </label>
        </div>
      </Drawer>
    </div>
  );
}
