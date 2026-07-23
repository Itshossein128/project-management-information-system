import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import {
  createInventoryTransaction,
  createMaterialRequest,
  fetchInventoryTransactions,
  fetchMaterialBalance,
  fetchMaterialConsumption,
  fetchMaterialRequests,
  fetchMaterials,
} from "@/app/lib/api/materials";
import { fetchSuppliers } from "@/app/lib/api/costs";
import { PATHS } from "@/app/routeVars";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { EmptyState } from "@/components/layout/empty-state";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";
import { Tabs, TabsContent as ShadcnTabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

type Tab = "balance" | "requests" | "transactions";

const TABS: { id: Tab; label: string }[] = [
  { id: "balance", label: "بالانس" },
  { id: "requests", label: "درخواست‌ها" },
  { id: "transactions", label: "تراکنش‌ها" },
];

function BalanceTab({ projectId }: { projectId: string }) {
  const [discipline, setDiscipline] = useState("");
  const [lowStock, setLowStock] = useState(false);

  const { data = [], isLoading, isError, refetch } = useQuery({
    queryKey: ["material-balance", projectId, discipline, lowStock],
    queryFn: () =>
      fetchMaterialBalance(projectId, {
        discipline: discipline || undefined,
        low_stock: lowStock || undefined,
      }),
  });

  const { data: consumption } = useQuery({
    queryKey: ["material-consumption", projectId],
    queryFn: () => fetchMaterialConsumption(projectId),
  });

  const consumptionById = new Map(
    (consumption?.materials ?? []).map((m) => [m.material_id, m]),
  );

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <label className="flex flex-col gap-1 text-sm">
          <span>رشته</span>
          <input
            className="rounded-md border px-3 py-2"
            value={discipline}
            onChange={(e) => setDiscipline(e.target.value)}
            placeholder="فیلتر رشته…"
          />
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={lowStock} onChange={(e) => setLowStock(e.target.checked)} />
          فقط کمبود موجودی
        </label>
      </div>
      {isLoading ? (
        <LoadingSkeleton rows={6} />
      ) : isError ? (
        <QueryErrorState onRetry={() => void refetch()} />
      ) : data.length === 0 ? (
        <EmptyState
          title="موردی یافت نشد"
          description="بالانس مصالح برای این فیلتر خالی است."
        />
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                {["کد", "مصالح", "واحد", "درخواست", "ورود", "خروج", "موجودی", "مصرف%", "حداقل", "وضعیت"].map(
                  (h) => (
                    <th key={h} className="px-3 py-2 text-start">
                      {h}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody>
              {data.map((r) => {
                  const cons = consumptionById.get(r.material_id);
                  return (
                  <tr
                    key={r.material_id}
                    className={`border-t border-border ${r.is_low_stock ? "bg-danger-50 dark:bg-danger-950/20" : ""}`}
                  >
                    <td className="px-3 py-2 font-mono text-xs">{r.material_code}</td>
                    <td className="px-3 py-2">{r.material_name}</td>
                    <td className="px-3 py-2">{r.unit}</td>
                    <td className="px-3 py-2">{r.total_requested}</td>
                    <td className="px-3 py-2">{r.total_received}</td>
                    <td className="px-3 py-2">{r.total_issued}</td>
                    <td className="px-3 py-2 font-medium">{r.current_balance}</td>
                    <td className="px-3 py-2">
                      {cons?.consumption_pct != null ? `${cons.consumption_pct}%` : "—"}
                    </td>
                    <td className="px-3 py-2">{r.min_stock_level ?? "—"}</td>
                    <td className="px-3 py-2">
                      {r.is_low_stock ? (
                        <Link
                          to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_ALERTS}?type=low_stock`}
                          className="text-xs text-danger-600 hover:underline"
                        >
                          کمبود
                        </Link>
                      ) : (
                        <span className="text-xs text-success-600">عادی</span>
                      )}
                    </td>
                  </tr>
                );
                })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function RequestsTab({ projectId, canEdit }: { projectId: string; canEdit: boolean }) {
  const toast = useToast();
  const qc = useQueryClient();
  const [materialId, setMaterialId] = useState("");
  const [qty, setQty] = useState("");

  const { data: requests = [], isLoading, isError, refetch } = useQuery({
    queryKey: ["material-requests", projectId],
    queryFn: () => fetchMaterialRequests(projectId),
  });

  const { data: materials = [] } = useQuery({
    queryKey: ["materials", projectId],
    queryFn: () => fetchMaterials(projectId),
    enabled: canEdit,
  });

  const create = useMutation({
    mutationFn: () =>
      createMaterialRequest(projectId, {
        material: materialId,
        requested_qty: Number(qty),
      }),
    onSuccess: () => {
      toast.success("درخواست ثبت شد");
      setMaterialId("");
      setQty("");
      void qc.invalidateQueries({ queryKey: ["material-requests", projectId] });
      void qc.invalidateQueries({ queryKey: ["material-balance", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <div className="space-y-4">
      {canEdit ? (
        <div className="flex flex-wrap items-end gap-2 rounded-lg border border-border p-3">
          <label className="flex flex-col gap-1 text-sm">
            <span>مصالح</span>
            <select
              className="rounded-md border px-3 py-2"
              value={materialId}
              onChange={(e) => setMaterialId(e.target.value)}
            >
              <option value="">انتخاب…</option>
              {materials.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.material_code} — {m.material_name}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span>مقدار</span>
            <input
              type="number"
              className="rounded-md border px-3 py-2"
              value={qty}
              onChange={(e) => setQty(e.target.value)}
            />
          </label>
          <Button
            variant="primary"
            size="sm"
            disabled={!materialId || !qty}
            loading={create.isPending}
            onClick={() => create.mutate()}
          >
            ثبت درخواست
          </Button>
        </div>
      ) : null}
      {isLoading ? (
        <LoadingSkeleton rows={6} />
      ) : isError ? (
        <QueryErrorState onRetry={() => void refetch()} />
      ) : requests.length === 0 ? (
        <EmptyState title="درخواستی ثبت نشده" description="درخواست مصالح اینجا نمایش داده می‌شود." />
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                {["شماره", "مصالح", "مقدار", "واحد", "تاریخ", "نیاز تا", "وضعیت"].map((h) => (
                  <th key={h} className="px-3 py-2 text-start">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {requests.map((r) => (
                  <tr key={r.id} className="border-t border-border">
                    <td className="px-3 py-2">{r.request_number}</td>
                    <td className="px-3 py-2">{r.material_name}</td>
                    <td className="px-3 py-2">{r.requested_qty}</td>
                    <td className="px-3 py-2">{r.unit}</td>
                    <td className="px-3 py-2">{r.request_date ?? "—"}</td>
                    <td className="px-3 py-2">{r.required_by_date ?? "—"}</td>
                    <td className="px-3 py-2">{r.status}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function TransactionsTab({ projectId, canEdit }: { projectId: string; canEdit: boolean }) {
  const toast = useToast();
  const qc = useQueryClient();
  const [materialId, setMaterialId] = useState("");
  const [txDate, setTxDate] = useState("");
  const [txType, setTxType] = useState("in");
  const [quantity, setQuantity] = useState("");
  const [supplierId, setSupplierId] = useState("");

  const { data: suppliers = [] } = useQuery({
    queryKey: ["suppliers", projectId],
    queryFn: () => fetchSuppliers(projectId),
    enabled: canEdit,
  });

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["inventory-transactions", projectId],
    queryFn: async () => {
      const res = await fetchInventoryTransactions(projectId);
      return Array.isArray(res) ? res : res.results;
    },
  });

  const { data: materials = [] } = useQuery({
    queryKey: ["materials", projectId],
    queryFn: () => fetchMaterials(projectId),
    enabled: canEdit,
  });

  const create = useMutation({
    mutationFn: () =>
      createInventoryTransaction(projectId, {
        material: materialId,
        tx_date: txDate,
        tx_type: txType,
        quantity: Number(quantity),
        supplier: supplierId || undefined,
      }),
    onSuccess: () => {
      toast.success("تراکنش ثبت شد");
      setMaterialId("");
      setTxDate("");
      setQuantity("");
      void qc.invalidateQueries({ queryKey: ["inventory-transactions", projectId] });
      void qc.invalidateQueries({ queryKey: ["material-balance", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const rows = data ?? [];

  return (
    <div className="space-y-4">
      {canEdit ? (
        <div className="flex flex-wrap items-end gap-2 rounded-lg border border-border p-3">
          <label className="flex flex-col gap-1 text-sm">
            <span>مصالح</span>
            <select
              className="rounded-md border px-3 py-2"
              value={materialId}
              onChange={(e) => setMaterialId(e.target.value)}
            >
              <option value="">انتخاب…</option>
              {materials.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.material_code} — {m.material_name}
                </option>
              ))}
            </select>
          </label>
          <JalaliDatePicker name="tx_date" label="تاریخ" value={txDate} onChange={setTxDate} />
          <label className="flex flex-col gap-1 text-sm">
            <span>نوع</span>
            <select
              className="rounded-md border px-3 py-2"
              value={txType}
              onChange={(e) => setTxType(e.target.value)}
            >
              <option value="in">ورود</option>
              <option value="out">خروج</option>
              <option value="waste">ضایعات</option>
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span>مقدار</span>
            <input
              type="number"
              className="rounded-md border px-3 py-2"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span>تأمین‌کننده</span>
            <select
              className="rounded-md border px-3 py-2"
              value={supplierId}
              onChange={(e) => setSupplierId(e.target.value)}
            >
              <option value="">—</option>
              {suppliers.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.supplier_name}
                </option>
              ))}
            </select>
          </label>
          <Button
            variant="primary"
            size="sm"
            disabled={!materialId || !txDate || !quantity}
            loading={create.isPending}
            onClick={() => create.mutate()}
          >
            ثبت تراکنش
          </Button>
        </div>
      ) : null}
      {isLoading ? (
        <LoadingSkeleton rows={6} />
      ) : isError ? (
        <QueryErrorState onRetry={() => void refetch()} />
      ) : rows.length === 0 ? (
        <EmptyState title="تراکنشی ثبت نشده" description="ورود و خروج مصالح اینجا نمایش داده می‌شود." />
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                {["تاریخ", "مصالح", "نوع", "مقدار", "بلوک", "سند", "منبع"].map((h) => (
                  <th key={h} className="px-3 py-2 text-start">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                  <tr key={r.id} className="border-t border-border">
                    <td className="px-3 py-2">{r.tx_date}</td>
                    <td className="px-3 py-2">{r.material_name}</td>
                    <td className="px-3 py-2">{r.tx_type}</td>
                    <td className="px-3 py-2">{r.quantity}</td>
                    <td className="px-3 py-2">{r.block_ref || "—"}</td>
                    <td className="px-3 py-2">{r.document_ref || "—"}</td>
                    <td className="px-3 py-2">
                      {r.daily_report ? (
                        <span className="text-xs text-info-600">گزارش روزانه</span>
                      ) : (
                        <span className="text-xs text-success-600">دستی</span>
                      )}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function MaterialBalanceContent() {
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_reports");
  const canEdit = has("edit_reports");
  const [tab, setTab] = useState<Tab>("balance");

  if (isLoading) return <LoadingSkeleton rows={8} />;
  if (!project) return <EmptyState title="پروژه یافت نشد" />;

  if (!canView) {
    return (
      <EmptyState
        title="دسترسی ندارید"
        description="نقش شما مجوز مشاهده گزارش‌ها را ندارد."
      />
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader title="بالانس مصالح" subtitle={project.project_name} />

      <Tabs value={tab} onValueChange={(v) => setTab(v as Tab)} className="w-full" dir="rtl">
        <TabsList className="mb-4">
          {TABS.map((t) => (
            <TabsTrigger key={t.id} value={t.id}>
              {t.label}
            </TabsTrigger>
          ))}
        </TabsList>

        <ShadcnTabsContent value="balance" className="mt-0">
          <BalanceTab projectId={projectId} />
        </ShadcnTabsContent>

        <ShadcnTabsContent value="requests" className="mt-0">
          <RequestsTab projectId={projectId} canEdit={canEdit} />
        </ShadcnTabsContent>

        <ShadcnTabsContent value="transactions" className="mt-0">
          <TransactionsTab projectId={projectId} canEdit={canEdit} />
        </ShadcnTabsContent>
      </Tabs>
    </div>
  );
}

export default function ProjectMaterialBalancePage() {
  const { projectId = "" } = useParams();

  return (
    <main className="page-main page-shell mx-auto max-w-7xl px-4 py-8">
      <ProjectProvider projectId={projectId}>
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "بالانس مصالح" },
          ]}
        />
        <MaterialBalanceContent />
      </ProjectProvider>
    </main>
  );
}
