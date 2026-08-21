import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate, useParams, Link } from "react-router";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { PageHeader, Breadcrumb, LoadingSkeleton } from "@/components/layout/page-header";
import { ProjectProvider, useProject } from "~/contexts/project-context";
import { fetchBlocks, createRequisition } from "~/lib/api/procurement";
import { fetchMaterials } from "~/lib/api/materials";
import { PATHS } from "~/routeVars";
import { useToast } from "@/components/ui/toast";

function ProcurementNewContent() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const toast = useToast();
  const qc = useQueryClient();
  const { projectId, project } = useProject();

  const [block, setBlock] = useState("");
  const [reqType, setReqType] = useState("planned");
  const [priority, setPriority] = useState("normal");
  const [urgency, setUrgency] = useState("");
  const [notes, setNotes] = useState("");
  const [isGrnProvisional, setIsGrnProvisional] = useState(false);
  const [items, setItems] = useState([{ material: "", requested_qty: "", notes: "" }]);

  const { data: blocks = [] } = useQuery({
    queryKey: ["blocks", projectId],
    queryFn: () => fetchBlocks(projectId),
  });

  const { data: rawMaterials = [] } = useQuery({
    queryKey: ["materials", projectId],
    queryFn: () => fetchMaterials(projectId),
  });

  const materials = Array.isArray(rawMaterials) ? rawMaterials : ((rawMaterials as any)?.results ?? []);

  const createMut = useMutation({
    mutationFn: (payload: any) => createRequisition(projectId, payload),
    onSuccess: () => {
      toast.success("درخواست با موفقیت ثبت شد (پیش‌نویس)");
      void qc.invalidateQueries({ queryKey: ["procurement", projectId] });
      navigate(`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT}`);
    },
    onError: (e: any) => toast.error(e.message || "خطا در ثبت درخواست"),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!block) return toast.error("انتخاب بلوک الزامی است.");
    
    const validItems = items.filter((i: any) => i.material && i.requested_qty);
    if (validItems.length === 0) return toast.error("حداقل یک آیتم با متریال و مقدار وارد کنید.");

    const payload = {
      project: projectId,
      block,
      requisition_type: reqType,
      priority,
      urgency,
      request_date: new Date().toISOString().split('T')[0], // today
      is_grn_provisional: isGrnProvisional,
      notes,
      items: validItems.map((i: any) => ({
        material: i.material,
        requested_qty: parseFloat(i.requested_qty),
        notes: i.notes
      }))
    };

    createMut.mutate(payload);
  };

  const addItem = () => setItems([...items, { material: "", requested_qty: "", notes: "" }]);
  const removeItem = (idx: number) => setItems(items.filter((_, i) => i !== idx));

  if (!project) return null;

  return (
    <div className="space-y-6">
      <PageHeader title="ثبت درخواست خرید جدید" subtitle={project.project_name} />

      <form onSubmit={handleSubmit} className="space-y-8 rounded-lg border border-border bg-card p-6">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <label className="flex flex-col gap-1 text-sm">
            <span>بلوک/فاز (الزامی)</span>
            <select className="rounded-md border px-3 py-2" value={block} onChange={(e: any) => setBlock(e.target.value)} required>
              <option value="">انتخاب بلوک...</option>
              {blocks.map((b: any) => <option key={b.id} value={b.id}>{b.block_code} - {b.block_name}</option>)}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span>نوع درخواست</span>
            <select className="rounded-md border px-3 py-2" value={reqType} onChange={(e: any) => setReqType(e.target.value)}>
              <option value="planned">عادی (Planned)</option>
              <option value="fast_track">فورس‌ماژور (Fast-Track)</option>
              <option value="post_facto">پس‌نگر (Post-Facto)</option>
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span>اولویت</span>
            <select className="rounded-md border px-3 py-2" value={priority} onChange={(e: any) => setPriority(e.target.value)}>
              <option value="normal">عادی</option>
              <option value="high">بالا</option>
              <option value="emergency">اضطراری</option>
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span>دلیل فوریت</span>
            <input type="text" className="rounded-md border px-3 py-2" value={urgency} onChange={(e: any) => setUrgency(e.target.value)} placeholder="اختیاری..." />
          </label>
        </div>

        {reqType === 'post_facto' && (
          <label className="flex items-center gap-2 text-sm text-amber-600 bg-amber-50 p-3 rounded border border-amber-200">
            <input type="checkbox" checked={isGrnProvisional} onChange={(e: any) => setIsGrnProvisional(e.target.checked)} />
            <span>صدور رسید انبار موقت (به‌دلیل خرید پس‌نگر)</span>
          </label>
        )}

        <div>
          <h3 className="mb-4 text-lg font-medium">ردیف‌های درخواستی</h3>
          <div className="space-y-4">
            {items.map((item, idx) => (
              <div key={idx} className="flex flex-wrap items-start gap-4 rounded border p-4 bg-muted/20">
                <label className="flex flex-1 flex-col gap-1 text-sm min-w-[200px]">
                  <span>متریال</span>
                  <select className="rounded-md border px-3 py-2" value={item.material} onChange={(e: any) => {
                    const newItems = [...items];
                    newItems[idx].material = e.target.value;
                    setItems(newItems);
                  }} required>
                    <option value="">انتخاب متریال...</option>
                    {materials.map((m: any) => <option key={m.id} value={m.id}>{m.material_code} - {m.material_name}</option>)}
                  </select>
                </label>
                <label className="flex flex-col gap-1 text-sm w-32">
                  <span>مقدار</span>
                  <input type="number" step="any" min="0.0001" className="rounded-md border px-3 py-2" value={item.requested_qty} onChange={(e: any) => {
                    const newItems = [...items];
                    newItems[idx].requested_qty = e.target.value;
                    setItems(newItems);
                  }} required />
                </label>
                <label className="flex flex-1 flex-col gap-1 text-sm min-w-[200px]">
                  <span>توضیحات</span>
                  <input type="text" className="rounded-md border px-3 py-2" value={item.notes} onChange={(e: any) => {
                    const newItems = [...items];
                    newItems[idx].notes = e.target.value;
                    setItems(newItems);
                  }} />
                </label>
                <div className="pt-6">
                  <Button type="button" variant="outline" onClick={() => removeItem(idx)} disabled={items.length === 1} className="text-red-500 hover:text-red-700">حذف</Button>
                </div>
              </div>
            ))}
          </div>
          <Button type="button" variant="outline" className="mt-4" onClick={addItem}>+ افزودن ردیف جدید</Button>
        </div>

        <label className="flex flex-col gap-1 text-sm">
          <span>توضیحات کلی درخواست</span>
          <textarea className="rounded-md border px-3 py-2" rows={3} value={notes} onChange={(e: any) => setNotes(e.target.value)} />
        </label>

        <div className="flex gap-4 pt-4 border-t border-border">
          <Button type="submit" variant="default" disabled={createMut.isPending}>
            ثبت پیش‌نویس
          </Button>
          <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT}`}>
            <Button type="button" variant="outline">انصراف</Button>
          </Link>
        </div>
      </form>
    </div>
  );
}

export default function ProcurementNewPage() {
  const { projectId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto px-4 py-8">
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "تدارکات", href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT}` },
            { label: "درخواست جدید" },
          ]}
        />
        <ProcurementNewContent />
      </main>
    </ProjectProvider>
  );
}
