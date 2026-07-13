import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import { fetchContracts } from "@/app/lib/api/contracts";
import {
  createSubcontractor,
  fetchSubcontractors,
  formatFaAmount,
  scoreColor,
  STATUS_COLORS,
  STATUS_LABELS,
} from "@/app/lib/api/subcontractors";
import { PATHS } from "@/app/routeVars";
import { RiskBadgeTooltip } from "@/components/subcontractors/RiskBadgeTooltip";
import { LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

function SubcontractorsContent() {
  const { projectId, project, isLoading } = useProject();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const toast = useToast();
  const { has } = usePermission(projectId);
  const canView = has("view_contracts");
  const canEdit = has("edit_contracts");

  const [statusFilter, setStatusFilter] = useState("");
  const [riskOnly, setRiskOnly] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [form, setForm] = useState({
    company_name: "",
    discipline: "",
    responsible_person: "",
    phone: "",
    contract: "",
    status: "active",
  });

  const params: Record<string, string> = {};
  if (statusFilter) params.status = statusFilter;
  if (riskOnly) params.risk_only = "true";

  const { data, isLoading: loading } = useQuery({
    queryKey: ["subcontractors", projectId, params],
    queryFn: () => fetchSubcontractors(projectId, params),
    enabled: canView,
  });

  const { data: contracts } = useQuery({
    queryKey: ["contracts", projectId, "subcontract"],
    queryFn: () => fetchContracts(projectId, { contract_type: "subcontract" }),
    enabled: canEdit && drawerOpen,
  });

  const createMut = useMutation({
    mutationFn: () =>
      createSubcontractor(projectId, {
        ...form,
        contract: form.contract || null,
      }),
    onSuccess: (row) => {
      toast.success("پیمانکار ثبت شد");
      setDrawerOpen(false);
      void qc.invalidateQueries({ queryKey: ["subcontractors", projectId] });
      navigate(`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_SUBCONTRACTORS}/${row.id}`);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (isLoading || loading) return <LoadingSkeleton rows={8} />;
  if (!project) return <p>پروژه یافت نشد</p>;
  if (!canView) {
    return <p className="rounded-lg border p-8 text-center text-muted-foreground">دسترسی ندارید.</p>;
  }

  const rows = data?.results ?? [];
  const atRisk = rows.filter((r) => r.risk_flag).length;
  const active = rows.filter((r) => r.status === "active").length;
  const suspended = rows.filter((r) => r.status === "suspended").length;

  return (
    <div className="space-y-6">
      <PageHeader
        title="پیمانکاران فرعی"
        subtitle={project.project_name}
        actions={
          canEdit ? (
            <Button variant="primary" onClick={() => setDrawerOpen(true)}>
              افزودن پیمانکار فرعی
            </Button>
          ) : null
        }
      />

      {atRisk > 0 ? (
        <div className="rounded-lg border border-amber-300 bg-amber-50 p-4 text-amber-900">
          ⚠ {atRisk} پیمانکار در وضعیت ریسک قرار دارند{" "}
          <button type="button" className="underline" onClick={() => setRiskOnly(true)}>
            مشاهده جزئیات
          </button>
        </div>
      ) : null}

      <div className="grid gap-4 md:grid-cols-4">
        <div className="rounded-lg border p-4"><p className="text-sm text-muted-foreground">کل پیمانکاران</p><p className="text-xl font-semibold">{rows.length}</p></div>
        <div className="rounded-lg border p-4"><p className="text-sm text-muted-foreground">فعال</p><p className="text-xl font-semibold text-emerald-600">{active}</p></div>
        <div className="rounded-lg border p-4"><p className="text-sm text-muted-foreground">در خطر</p><p className="text-xl font-semibold text-red-600">{atRisk}</p></div>
        <div className="rounded-lg border p-4"><p className="text-sm text-muted-foreground">تعلیق‌شده</p><p className="text-xl font-semibold text-amber-600">{suspended}</p></div>
      </div>

      <div className="flex flex-wrap gap-3">
        <select className="rounded border px-3 py-1.5 text-sm" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">همه وضعیت‌ها</option>
          {Object.entries(STATUS_LABELS).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={riskOnly} onChange={(e) => setRiskOnly(e.target.checked)} />
          فقط در خطر
        </label>
      </div>

      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              {["نام شرکت", "حوزه کاری", "وضعیت", "آخرین نمره", "طلب معوق", "هشدارها", "ریسک", "عملیات"].map((h) => (
                <th key={h} className="px-3 py-2 text-start">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => {
              const hasSeriousWarning = r.active_warning_types?.some((t) =>
                ["written", "final", "contract_suspension"].includes(t),
              );
              return (
                <tr
                  key={r.id}
                  className="cursor-pointer border-t hover:bg-muted/30"
                  onClick={() => navigate(`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_SUBCONTRACTORS}/${r.id}`)}
                >
                  <td className="px-3 py-2 font-medium">{r.company_name}</td>
                  <td className="px-3 py-2">{r.discipline || "—"}</td>
                  <td className="px-3 py-2">
                    <span className={`rounded px-2 py-0.5 text-xs ${STATUS_COLORS[r.status] ?? ""}`}>
                      {STATUS_LABELS[r.status] ?? r.status}
                    </span>
                  </td>
                  <td className={`px-3 py-2 font-medium ${scoreColor(r.latest_score)}`}>
                    {r.latest_score?.toFixed(1) ?? "—"}
                  </td>
                  <td className="px-3 py-2">{formatFaAmount(r.financial_summary.outstanding)}</td>
                  <td className="px-3 py-2">
                    <span className={`rounded px-2 py-0.5 text-xs ${hasSeriousWarning ? "bg-red-100 text-red-800" : "bg-gray-100 text-gray-700"}`}>
                      {r.warning_count}
                    </span>
                  </td>
                  <td className="px-3 py-2">
                    <RiskBadgeTooltip riskFlag={r.risk_flag} reasons={r.risk_reasons} />
                  </td>
                  <td className="px-3 py-2" onClick={(e) => e.stopPropagation()}>
                    <Link
                      to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_SUBCONTRACTORS}/${r.id}`}
                      className="text-primary underline"
                    >
                      جزئیات
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <Drawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title="افزودن پیمانکار فرعی"
        footer={
          <Button variant="primary" onClick={() => createMut.mutate()} disabled={createMut.isPending || !form.company_name}>
            ذخیره
          </Button>
        }
      >
        <div className="space-y-3">
          <input className="w-full rounded border px-3 py-2 text-sm" placeholder="نام شرکت" value={form.company_name} onChange={(e) => setForm({ ...form, company_name: e.target.value })} />
          <input className="w-full rounded border px-3 py-2 text-sm" placeholder="حوزه کاری" value={form.discipline} onChange={(e) => setForm({ ...form, discipline: e.target.value })} />
          <input className="w-full rounded border px-3 py-2 text-sm" placeholder="مسئول" value={form.responsible_person} onChange={(e) => setForm({ ...form, responsible_person: e.target.value })} />
          <input className="w-full rounded border px-3 py-2 text-sm" placeholder="تلفن" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          <select className="w-full rounded border px-3 py-2 text-sm" value={form.contract} onChange={(e) => setForm({ ...form, contract: e.target.value })}>
            <option value="">بدون قرارداد</option>
            {(contracts?.results ?? []).map((c) => (
              <option key={c.id} value={c.id}>{c.contract_number || c.counterparty}</option>
            ))}
          </select>
          <select className="w-full rounded border px-3 py-2 text-sm" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
            {Object.entries(STATUS_LABELS).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
        </div>
      </Drawer>
    </div>
  );
}

export default function ProjectSubcontractorsPage() {
  const { projectId = "" } = useParams();
  return (
    <ProjectProvider projectId={projectId}>
      <SubcontractorsContent />
    </ProjectProvider>
  );
}
