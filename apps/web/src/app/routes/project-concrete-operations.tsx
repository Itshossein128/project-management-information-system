import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import { PATHS } from "@/app/routeVars";
import { fetchSuppliers } from "@/app/lib/api/costs";
import { formatDisplayDate } from "@/app/lib/jalali-utils";
import {
  createConcreteBatch, createReadyMixDelivery, deleteConcreteBatch, deleteReadyMixDelivery,
  exportConcreteOperations, fetchConcreteBatches, fetchConcreteTotals, fetchReadyMixDeliveries,
  type ConcreteBatch, type ReadyMixDelivery,
} from "@/app/lib/api/concrete-operations";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { JalaliDateRangePicker } from "@/components/form/JalaliDateRangePicker";
import { AccessDenied, NotFoundState } from "@/components/layout/empty-state";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";

const emptyBatch = { date: "", volume_m3: "", cement_kg: "", sand_kg: "", aggregate_kg: "", water_l: "", plasticizer_l: "" };
const emptyDelivery = { date: "", volume_m3: "", supplier: "", ticket_number: "" };
const batchFields = [
  ["volume_m3", "حجم تولید (m³)"], ["cement_kg", "سیمان (kg)"], ["sand_kg", "ماسه (kg)"],
  ["aggregate_kg", "سنگدانه (kg)"], ["water_l", "آب (L)"], ["plasticizer_l", "روان‌کننده (L)"],
] as const;
const inputClass = "rounded-md border border-input bg-background px-3 py-2 w-full";
const buttonClass = "rounded-md bg-primary px-4 py-2 text-primary-foreground disabled:opacity-50";

function Content() {
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_reports");
  const canEdit = has("edit_reports");
  const client = useQueryClient();
  const [range, setRange] = useState({ from: "", to: "" });
  const [batch, setBatch] = useState(emptyBatch);
  const [delivery, setDelivery] = useState(emptyDelivery);
  const [error, setError] = useState("");
  const [exporting, setExporting] = useState(false);
  const batches = useQuery({ queryKey: ["concrete-batches", projectId], queryFn: () => fetchConcreteBatches(projectId), enabled: canView && !!projectId });
  const deliveries = useQuery({ queryKey: ["ready-mix-deliveries", projectId], queryFn: () => fetchReadyMixDeliveries(projectId), enabled: canView && !!projectId });
  const suppliers = useQuery({ queryKey: ["suppliers", projectId], queryFn: () => fetchSuppliers(projectId), enabled: canEdit && !!projectId });
  const filter = { date_from: range.from, date_to: range.to };
  const totals = useQuery({ queryKey: ["concrete-totals", projectId, range], queryFn: () => fetchConcreteTotals(projectId, filter), enabled: canView && !!projectId });
  const refresh = () => void client.invalidateQueries({ queryKey: ["concrete-batches", projectId] }).then(() => {
    void client.invalidateQueries({ queryKey: ["ready-mix-deliveries", projectId] });
    void client.invalidateQueries({ queryKey: ["concrete-totals", projectId] });
  });
  const saveBatch = useMutation({ mutationFn: () => createConcreteBatch(projectId, batch), onSuccess: () => { setBatch(emptyBatch); setError(""); refresh(); }, onError: (e: Error) => setError(e.message) });
  const saveDelivery = useMutation({ mutationFn: () => createReadyMixDelivery(projectId, delivery), onSuccess: () => { setDelivery(emptyDelivery); setError(""); refresh(); }, onError: (e: Error) => setError(e.message) });
  const removeBatch = useMutation({ mutationFn: (id: string) => deleteConcreteBatch(projectId, id), onSuccess: refresh, onError: (e: Error) => setError(e.message) });
  const removeDelivery = useMutation({ mutationFn: (id: string) => deleteReadyMixDelivery(projectId, id), onSuccess: refresh, onError: (e: Error) => setError(e.message) });
  if (isLoading) return <LoadingSkeleton rows={5} />;
  if (!project) return <NotFoundState title="پروژه یافت نشد" />;
  if (!canView) return <AccessDenied title="دسترسی غیرمجاز" description="مجوز مشاهده گزارش‌های پروژه را ندارید." />;
  const inRange = <T extends { date: string }>(rows: T[]) => rows.filter(row => (!range.from || row.date >= range.from) && (!range.to || row.date <= range.to));
  const shownBatches = inRange(batches.data?.results ?? []);
  const shownDeliveries = inRange(deliveries.data?.results ?? []);
  const download = async () => {
    setExporting(true);
    try {
      const blob = await exportConcreteOperations(projectId, filter);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "concrete-operations.csv";
      anchor.click();
      URL.revokeObjectURL(url);
      setError("");
    } catch (e) { setError(e instanceof Error ? e.message : "خطا در خروجی"); }
    finally { setExporting(false); }
  };
  return <div className="space-y-6" dir="rtl">
    <PageHeader title="عملیات بتن پروژه" subtitle={project.project_name} />
    <div className="flex flex-wrap items-end gap-4">
      <div className="min-w-64 flex-1"><JalaliDateRangePicker name="concrete_range" label="بازه تاریخ" value={range} onChange={setRange} /></div>
      <button className={buttonClass} disabled={exporting} onClick={() => void download()}>خروجی CSV</button>
    </div>
    {error && <p role="alert" className="text-destructive">{error}</p>}
    {(batches.isError || deliveries.isError || totals.isError) && <p role="alert" className="text-destructive">خطا در دریافت اطلاعات بتن</p>}
    <div className="grid gap-3 sm:grid-cols-3">
      {[["تولید شده", totals.data?.produced_m3], ["تحویل شده", totals.data?.delivered_m3], ["بتن‌ریزی شده", totals.data?.poured_m3]].map(([label, value]) =>
        <div key={label} className="rounded-lg border p-4"><p>{label}</p><strong>{value ?? "…"} m³</strong></div>)}
    </div>
    {canEdit && <div className="grid gap-6 lg:grid-cols-2">
      <form className="space-y-3 rounded-lg border p-4" onSubmit={e => { e.preventDefault(); saveBatch.mutate(); }}>
        <h2 className="font-semibold">ثبت تولید بتن</h2>
        <JalaliDatePicker name="batch_date" label="تاریخ" required value={batch.date} onChange={date => setBatch({ ...batch, date })} />
        <div className="grid gap-3 sm:grid-cols-2">{batchFields.map(([key, label]) => <label key={key} className="text-sm">{label}<input className={inputClass} type="number" min={key === "volume_m3" ? "0.001" : "0"} step="0.001" required value={batch[key]} onChange={e => setBatch({ ...batch, [key]: e.target.value })} /></label>)}</div>
        <button className={buttonClass} disabled={saveBatch.isPending || !batch.date}>ثبت بچ</button>
      </form>
      <form className="space-y-3 rounded-lg border p-4" onSubmit={e => { e.preventDefault(); saveDelivery.mutate(); }}>
        <h2 className="font-semibold">ثبت بتن آماده خریداری‌شده</h2>
        <JalaliDatePicker name="delivery_date" label="تاریخ" required value={delivery.date} onChange={date => setDelivery({ ...delivery, date })} />
        <label className="block text-sm">حجم تحویل (m³)<input className={inputClass} type="number" min="0.001" step="0.001" required value={delivery.volume_m3} onChange={e => setDelivery({ ...delivery, volume_m3: e.target.value })} /></label>
        <label className="block text-sm">تأمین‌کننده<select className={inputClass} required value={delivery.supplier} onChange={e => setDelivery({ ...delivery, supplier: e.target.value })}><option value="">انتخاب کنید</option>{suppliers.data?.map(s => <option key={s.id} value={s.id}>{s.supplier_name}</option>)}</select></label>
        <label className="block text-sm">شماره بارنامه (اختیاری)<input className={inputClass} value={delivery.ticket_number} onChange={e => setDelivery({ ...delivery, ticket_number: e.target.value })} /></label>
        <button className={buttonClass} disabled={saveDelivery.isPending || !delivery.date}>ثبت تحویل</button>
      </form>
    </div>}
    <section className="space-y-3"><h2 className="font-semibold">تولید بتن</h2>
      {shownBatches.length === 0 ? <p>رکوردی ثبت نشده است.</p> : <div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr>{["تاریخ", "حجم (m³)", "سیمان (kg)", "ماسه (kg)", "سنگدانه (kg)", "آب (L)", "روان‌کننده (L)", ""].map(h => <th key={h} className="p-2 text-start">{h}</th>)}</tr></thead><tbody>{shownBatches.map((row: ConcreteBatch) => <tr key={row.id} className="border-t"><td className="p-2">{formatDisplayDate(row.date)}</td>{[row.volume_m3, row.cement_kg, row.sand_kg, row.aggregate_kg, row.water_l, row.plasticizer_l].map((value, i) => <td className="p-2" key={i}>{value}</td>)}<td>{canEdit && <button onClick={() => removeBatch.mutate(row.id)}>حذف</button>}</td></tr>)}</tbody></table></div>}
    </section>
    <section className="space-y-3"><h2 className="font-semibold">تحویل بتن آماده</h2>
      {shownDeliveries.length === 0 ? <p>رکوردی ثبت نشده است.</p> : <div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr>{["تاریخ", "حجم (m³)", "تأمین‌کننده", "شماره بارنامه", ""].map(h => <th key={h} className="p-2 text-start">{h}</th>)}</tr></thead><tbody>{shownDeliveries.map((row: ReadyMixDelivery) => <tr key={row.id} className="border-t"><td className="p-2">{formatDisplayDate(row.date)}</td><td className="p-2">{row.volume_m3}</td><td className="p-2">{row.supplier_name}</td><td className="p-2">{row.ticket_number}</td><td>{canEdit && <button onClick={() => removeDelivery.mutate(row.id)}>حذف</button>}</td></tr>)}</tbody></table></div>}
    </section>
  </div>;
}
export default function ProjectConcreteOperationsPage() {
  const { projectId = "" } = useParams();
  return <main className="page-main page-shell mx-auto px-4 py-8"><ProjectProvider projectId={projectId}>
    <Breadcrumb items={[{ label: "پروژه‌ها", href: `/${PATHS.PROJECT}` }, { label: "عملیات بتن" }]} />
    <Content />
  </ProjectProvider></main>;
}
