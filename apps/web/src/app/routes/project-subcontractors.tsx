import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Users } from "lucide-react";
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
import { Checkbox, Field, Input, Select } from "@/components/form";
import { EmptyState } from "@/components/layout/empty-state";
import { LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { RiskBadgeTooltip } from "@/components/subcontractors/RiskBadgeTooltip";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

const NO_CONTRACT = "__none__";

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

  const {
    data,
    isLoading: loading,
    isError,
    refetch,
  } = useQuery({
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

  if (isLoading || (canView && loading)) return <LoadingSkeleton rows={8} />;
  if (!project) {
    return <EmptyState title="پروژه یافت نشد" />;
  }
  if (!canView) {
    return (
      <EmptyState
        title="دسترسی ندارید"
        description="برای مشاهده پیمانکاران فرعی به مجوز قراردادها نیاز است."
      />
    );
  }
  if (isError) {
    return <QueryErrorState onRetry={() => void refetch()} />;
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

      <div className="flex flex-wrap items-end gap-3">
        <Select
          name="status_filter"
          label="وضعیت"
          value={statusFilter || "all"}
          onChange={(e) =>
            setStatusFilter(e.target.value === "all" ? "" : e.target.value)
          }
          options={[
            { value: "all", label: "همه وضعیت‌ها" },
            ...Object.entries(STATUS_LABELS).map(([k, v]) => ({ value: k, label: v })),
          ]}
          fieldClassName="min-w-[10rem]"
        />
        <Checkbox
          name="risk_only"
          label="فقط در خطر"
          checked={riskOnly}
          onChange={(e) => {
            setRiskOnly(Boolean((e.target as unknown as { value: boolean }).value));
          }}
        />
      </div>

      {rows.length === 0 ? (
        <EmptyState
          icon={<Users />}
          title="پیمانکاری ثبت نشده"
          description="اولین پیمانکار فرعی را اضافه کنید یا فیلترها را تغییر دهید."
          action={
            canEdit ? (
              <Button variant="primary" onClick={() => setDrawerOpen(true)}>
                افزودن پیمانکار فرعی
              </Button>
            ) : null
          }
        />
      ) : (
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
      )}

      <Drawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title="افزودن پیمانکار فرعی"
        footer={
          <Button
            variant="primary"
            loading={createMut.isPending}
            onClick={() => createMut.mutate()}
            disabled={createMut.isPending || !form.company_name.trim()}
          >
            ذخیره
          </Button>
        }
      >
        <div className="space-y-4">
          <Field name="company_name" label="نام شرکت" htmlFor="sub-company-name">
            {() => (
              <Input
                id="sub-company-name"
                name="company_name"
                value={form.company_name}
                onChange={(e) => setForm({ ...form, company_name: e.target.value })}
                required
              />
            )}
          </Field>
          <Field name="discipline" label="حوزه کاری" htmlFor="sub-discipline">
            {() => (
              <Input
                id="sub-discipline"
                name="discipline"
                value={form.discipline}
                onChange={(e) => setForm({ ...form, discipline: e.target.value })}
              />
            )}
          </Field>
          <Field name="responsible_person" label="مسئول" htmlFor="sub-responsible">
            {() => (
              <Input
                id="sub-responsible"
                name="responsible_person"
                value={form.responsible_person}
                onChange={(e) => setForm({ ...form, responsible_person: e.target.value })}
              />
            )}
          </Field>
          <Field name="phone" label="تلفن" htmlFor="sub-phone">
            {() => (
              <Input
                id="sub-phone"
                name="phone"
                type="tel"
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
              />
            )}
          </Field>
          <Select
            name="contract"
            label="قرارداد"
            value={form.contract || NO_CONTRACT}
            onChange={(e) =>
              setForm({
                ...form,
                contract: e.target.value === NO_CONTRACT ? "" : e.target.value,
              })
            }
            options={[
              { value: NO_CONTRACT, label: "بدون قرارداد" },
              ...(contracts?.results ?? []).map((c) => ({
                value: c.id,
                label: c.contract_number || c.counterparty,
              })),
            ]}
          />
          <Select
            name="status"
            label="وضعیت"
            value={form.status}
            onChange={(e) => setForm({ ...form, status: e.target.value })}
            options={Object.entries(STATUS_LABELS).map(([k, v]) => ({
              value: k,
              label: v,
            }))}
          />
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
