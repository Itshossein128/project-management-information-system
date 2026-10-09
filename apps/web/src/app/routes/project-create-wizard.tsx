import { useMutation, useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router";
import { useTranslation } from "react-i18next";
import { addMember } from "@/app/lib/api/members";
import {
  asList,
  fetchContractTypes,
  fetchOrganizationUnits,
} from "@/app/lib/api/central-data";
import {
  createProject,
  type CreateProjectPayload,
  type ProjectCurrency,
} from "@/app/lib/api/projects";
import {
  applyProjectTemplate,
  fetchProjectTemplate,
  fetchProjectTemplates,
  projectTypeLabels,
  type ProjectTemplateListItem,
} from "@/app/lib/api/templates";
import { fetchRoles, lookupUsers, type Role, type UserLookupResult } from "@/app/lib/api/members";
import { formatRoleLabel } from "@/app/lib/role-labels";
import { PATHS } from "@/app/routeVars";
import { TemplateWBSPreviewTree } from "@/components/templates/template-wbs-preview-tree";
import { Breadcrumb, PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";
import { Input } from "@/components/form";
import { formatWithCommas, toRawNumericString } from "@/app/lib/utils";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { Label } from "@/components/ui/label";
import { LayoutTemplate } from "lucide-react";

interface DraftMember {
  user?: UserLookupResult;
  email?: string;
  roleId: string;
}

function suggestCode(name: string) {
  return name
    .trim()
    .replace(/\s+/g, "-")
    .replace(/[^a-zA-Z0-9\u0600-\u06FF-]/g, "")
    .slice(0, 20)
    .toLowerCase();
}

export default function ProjectCreateWizardPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const toast = useToast();
  const [step, setStep] = useState(1);

  const [form, setForm] = useState<CreateProjectPayload>({
    project_name: "",
    project_code: "",
    employer: "",
    contractor: "",
    consultant: "",
    contract_type: "",
    contract_number: "",
    purpose: "",
    scope_description: "",
    main_deliverables: "",
    location: "",
    start_date: "",
    planned_finish_date: "",
    contract_amount: "",
    currency: "IRR",
    owning_unit: null,
    project_manager: null,
  });

  const [members, setMembers] = useState<DraftMember[]>([]);
  const [search, setSearch] = useState("");
  const [searchResults, setSearchResults] = useState<UserLookupResult[]>([]);
  const [pmSearch, setPmSearch] = useState("");
  const [pmResults, setPmResults] = useState<UserLookupResult[]>([]);
  const [pmLabel, setPmLabel] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [selectedRoleId, setSelectedRoleId] = useState("");
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);

  const { data: roles = [] } = useQuery({ queryKey: ["roles"], queryFn: fetchRoles });
  const { data: templates = [] } = useQuery({
    queryKey: ["project-templates"],
    queryFn: () => fetchProjectTemplates(),
  });
  const { data: selectedTemplateDetail } = useQuery({
    queryKey: ["project-template", selectedTemplateId],
    queryFn: () => fetchProjectTemplate(selectedTemplateId!),
    enabled: Boolean(selectedTemplateId),
  });
  const { data: contractTypesRaw } = useQuery({
    queryKey: ["contract-types"],
    queryFn: fetchContractTypes,
  });
  const contractTypes = asList(contractTypesRaw ?? []);
  const { data: orgUnitsRaw } = useQuery({
    queryKey: ["organization-units"],
    queryFn: fetchOrganizationUnits,
  });
  const orgUnits = asList(orgUnitsRaw ?? []);

  const durationDays = useMemo(() => {
    if (!form.start_date || !form.planned_finish_date) return null;
    const start = new Date(form.start_date);
    const end = new Date(form.planned_finish_date);
    const diff = Math.round((end.getTime() - start.getTime()) / 86400000);
    return diff >= 0 ? diff : null;
  }, [form.start_date, form.planned_finish_date]);

  const createMutation = useMutation({
    mutationFn: async () => {
      const payload: CreateProjectPayload = {
        project_code: form.project_code.trim(),
        project_name: form.project_name.trim(),
        employer: form.employer.trim(),
        start_date: form.start_date,
        ...(form.contractor?.trim() ? { contractor: form.contractor.trim() } : {}),
        ...(form.consultant?.trim() ? { consultant: form.consultant.trim() } : {}),
        ...(form.contract_type?.trim() ? { contract_type: form.contract_type.trim() } : {}),
        ...(form.contract_number?.trim()
          ? { contract_number: form.contract_number.trim() }
          : {}),
        ...(form.purpose?.trim() ? { purpose: form.purpose.trim() } : {}),
        ...(form.scope_description?.trim()
          ? { scope_description: form.scope_description.trim() }
          : {}),
        ...(form.main_deliverables?.trim()
          ? { main_deliverables: form.main_deliverables.trim() }
          : {}),
        ...(form.location?.trim() ? { location: form.location.trim() } : {}),
        ...(form.planned_finish_date
          ? { planned_finish_date: form.planned_finish_date }
          : {}),
        ...(form.contract_amount?.trim()
          ? { contract_amount: form.contract_amount.trim() }
          : {}),
        ...(form.currency ? { currency: form.currency } : {}),
        ...(form.owning_unit ? { owning_unit: form.owning_unit } : {}),
        ...(form.project_manager ? { project_manager: form.project_manager } : {}),
      };
      const project = await createProject(payload);
      for (const m of members) {
        if (m.user) {
          await addMember(project.project_id, { user_id: m.user.user_id, role_ids: [m.roleId] });
        } else if (m.email) {
          await addMember(project.project_id, { email: m.email, role_ids: [m.roleId] });
        }
      }
      if (selectedTemplateId) {
        await applyProjectTemplate(selectedTemplateId, project.project_id);
      }
      return project;
    },
    onSuccess: (project) => {
      if (selectedTemplateId) {
        toast.success(t("projectWizard.wbsLoaded"));
        navigate(`/${PATHS.PROJECT}/${project.project_id}/${PATHS.PROJECT_WBS}`);
      } else {
        toast.success(t("project.draftCreated", t("projectWizard.createSuccess")));
        navigate(`/${PATHS.PROJECT}/${project.project_id}/${PATHS.PROJECT_OVERVIEW}`);
      }
    },
    onError: (err: Error) => {
      toast.error(err.message || t("projectWizard.createError"));
    },
  });

  const handleSearch = async () => {
    if (search.length < 2) return;
    const results = await lookupUsers(search);
    setSearchResults(results);
  };

  const handlePmSearch = async () => {
    if (pmSearch.length < 2) return;
    const results = await lookupUsers(pmSearch);
    setPmResults(results);
  };

  const addSearchedMember = (user: UserLookupResult) => {

    if (!selectedRoleId) return;
    setMembers((prev) => [...prev, { user, roleId: selectedRoleId }]);
    setSearch("");
    setSearchResults([]);
  };

  const addInviteMember = () => {
    if (!inviteEmail || !selectedRoleId) return;
    setMembers((prev) => [...prev, { email: inviteEmail, roleId: selectedRoleId }]);
    setInviteEmail("");
  };

  const selectTemplate = (template: ProjectTemplateListItem | null) => {

    setSelectedTemplateId(template?.template_id ?? null);
    if (template) {
      setForm((f) => ({
        ...f,
        contract_type: template.project_type === "epc" ? "EPC" : f.contract_type,
      }));
    }
  };

  const steps = [
    t("projectWizard.stepBasic"),
    t("projectWizard.stepDates"),
    t("projectWizard.stepTeam"),
  ];

  return (
    <main className="page-main page-shell mx-auto max-w-3xl px-4 py-8">
      <Breadcrumb
        items={[
          { label: t("project.title"), href: `/${PATHS.PROJECT}` },
          { label: t("projectWizard.breadcrumb") },
        ]}
      />
      <PageHeader title={t("projectWizard.title")} />

      <div className="mb-8 flex gap-2">
        {steps.map((label, i) => (
          <div
            key={label}
            className={`flex-1 rounded-md border px-3 py-2 text-center text-sm ${
              step === i + 1 ? "border-primary bg-primary/5 font-medium" : "border-border text-muted-foreground"
            }`}
          >
            {i + 1}. {label}
          </div>
        ))}
      </div>

      {step === 1 && (
        <div className="space-y-4">
          <div className="space-y-3">
            <Label>{t("projectWizard.useTemplate")}</Label>
            <div className="grid gap-3 sm:grid-cols-2">
              {templates.map((tpl) => (
                <button
                  key={tpl.template_id}
                  type="button"
                  onClick={() =>
                    selectTemplate(
                      selectedTemplateId === tpl.template_id ? null : tpl,
                    )
                  }
                  className={`rounded-lg border p-3 text-start transition-colors ${
                    selectedTemplateId === tpl.template_id
                      ? "border-primary bg-primary/5"
                      : "border-border hover:bg-muted/50"
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <LayoutTemplate className="mt-0.5 size-5 shrink-0 text-muted-foreground" />
                    <div className="min-w-0 flex-1">
                      <p className="font-medium">{tpl.template_name}</p>
                      {tpl.description ? (
                        <p className="mt-1 text-xs text-muted-foreground line-clamp-2">
                          {tpl.description}
                        </p>
                      ) : null}
                      <div className="mt-2">
                        <Badge
                          variant="info"
                          label={projectTypeLabels[tpl.project_type]}
                        />
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
            {selectedTemplateDetail?.wbs_tree?.length ? (
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">{t("projectWizard.wbsPreview")}</p>
                <TemplateWBSPreviewTree nodes={selectedTemplateDetail.wbs_tree} />
              </div>
            ) : null}
          </div>

          <div>
            <Label htmlFor="wizard-project-name">نام پروژه *</Label>
            <Input
              id="wizard-project-name"
              value={form.project_name}
              onChange={(e) => {
                const name = e.target.value;
                setForm((f) => ({
                  ...f,
                  project_name: name,
                  project_code: f.project_code || suggestCode(name),
                }));
              }}
            />
          </div>
          <div>
            <Label htmlFor="wizard-project-code">کد پروژه *</Label>
            <Input
              id="wizard-project-code"
              value={form.project_code}
              onChange={(e) => setForm((f) => ({ ...f, project_code: e.target.value }))}
            />
          </div>
          <div>
            <Label htmlFor="wizard-employer">کارفرما *</Label>
            <Input
              id="wizard-employer"
              value={form.employer}
              onChange={(e) => setForm((f) => ({ ...f, employer: e.target.value }))}
            />
          </div>
          <div>
            <Label>{t("project.purpose", "هدف پروژه")}</Label>
            <Input
              value={form.purpose ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, purpose: e.target.value }))}
            />
          </div>
          <div>
            <Label>{t("project.scope", "شرح محدوده")}</Label>
            <Input
              value={form.scope_description ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, scope_description: e.target.value }))}
            />
          </div>
          <div>
            <Label>{t("project.deliverables", "خروجی‌های اصلی")}</Label>
            <Input
              value={form.main_deliverables ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, main_deliverables: e.target.value }))}
            />
          </div>
          <div>
            <Label>پیمانکار</Label>
            <Input
              value={form.contractor}
              onChange={(e) => setForm((f) => ({ ...f, contractor: e.target.value }))}
            />
          </div>
          <div>
            <Label>مشاور</Label>
            <Input
              value={form.consultant}
              onChange={(e) => setForm((f) => ({ ...f, consultant: e.target.value }))}
            />
          </div>
          <div>
            <Label>{t("project.contractNumber", "شماره قرارداد")}</Label>
            <Input
              data-testid="wizard-contract-number"
              value={form.contract_number ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, contract_number: e.target.value }))}
            />
          </div>
          <div>
            <Label>نوع قرارداد</Label>
            <select
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
              data-testid="wizard-contract-type"
              value={form.contract_type}
              onChange={(e) => setForm((f) => ({ ...f, contract_type: e.target.value }))}
            >
              <option value="">—</option>
              {contractTypes.map((ct) => (
                <option key={ct.id} value={ct.code}>
                  {ct.code} — {ct.name_fa || ct.name_en}
                </option>
              ))}
            </select>
          </div>
          <div>
            <Label>{t("projectSettings.currency", "واحد پول")}</Label>
            <select
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
              data-testid="wizard-currency"
              value={form.currency ?? "IRR"}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  currency: e.target.value as ProjectCurrency,
                }))
              }
            >
              <option value="IRR">{t("projectSettings.currencyIrr", "ریال (IRR)")}</option>
              <option value="IRT">{t("projectSettings.currencyIrt", "تومان (IRT)")}</option>
            </select>
          </div>
          <div>
            <Label>{t("centralData.owningUnit", "واحد سازمانی مالک")}</Label>
            <select
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
              data-testid="wizard-owning-unit"
              value={form.owning_unit ?? ""}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  owning_unit: e.target.value || null,
                }))
              }
            >
              <option value="">—</option>
              {orgUnits.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.code} — {u.name}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-2" data-testid="wizard-project-manager">
            <Label>{t("project.projectManager", "مدیر پروژه")}</Label>
            <div className="flex gap-2">
              <Input
                placeholder={t("projectWizard.searchPm", "جستجوی مدیر پروژه")}
                value={pmSearch}
                onChange={(e) => setPmSearch(e.target.value)}
              />
              <Button type="button" variant="secondary" onClick={handlePmSearch}>
                {t("common.search", "جستجو")}
              </Button>
            </div>
            {pmLabel ? (
              <p className="text-sm text-muted-foreground">
                {t("project.selectedPm", "انتخاب‌شده")}: {pmLabel}
              </p>
            ) : null}
            {pmResults.length > 0 ? (
              <ul className="rounded-md border border-border">
                {pmResults.map((u) => (
                  <li key={u.user_id}>
                    <button
                      type="button"
                      className="w-full px-3 py-2 text-start text-sm hover:bg-muted"
                      onClick={() => {
                        setForm((f) => ({ ...f, project_manager: u.user_id }));
                        setPmLabel(u.full_name || u.email || u.user_id);
                        setPmResults([]);
                        setPmSearch("");
                      }}
                    >
                      {u.full_name} — {u.email || u.mobile}
                    </button>
                  </li>
                ))}
              </ul>
            ) : null}
          </div>
          <div>
            <Label>موقعیت</Label>
            <Input
              value={form.location}
              onChange={(e) => setForm((f) => ({ ...f, location: e.target.value }))}
            />
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Link to={`/${PATHS.PROJECT}`}>
              <Button variant="ghost">انصراف</Button>
            </Link>
            <Button
              variant="primary"
              onClick={() => setStep(2)}
              disabled={!form.project_name || !form.project_code || !form.employer}
            >
              بعدی
            </Button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-4">
          <JalaliDatePicker
            name="start_date"
            label="تاریخ شروع *"
            value={form.start_date}
            onChange={(v) => setForm((f) => ({ ...f, start_date: v }))}
          />
          <JalaliDatePicker
            name="planned_finish_date"
            label="تاریخ پایان برنامه‌ای"
            value={form.planned_finish_date ?? ""}
            onChange={(v) => setForm((f) => ({ ...f, planned_finish_date: v }))}
          />
          <div>
            <Label>مبلغ قرارداد</Label>
            <Input
              type="text"
              inputMode="decimal"
              value={formatWithCommas(form.contract_amount ?? "")}
              onChange={(e) => setForm((f) => ({ ...f, contract_amount: toRawNumericString(e.target.value) }))}
            />
          </div>
          {durationDays != null ? (
            <p className="text-sm text-muted-foreground">مدت قرارداد: {durationDays} روز</p>
          ) : null}
          <div className="flex justify-between gap-2 pt-4">
            <Button variant="ghost" onClick={() => setStep(1)}>
              قبلی
            </Button>
            <Button variant="primary" onClick={() => setStep(3)} disabled={!form.start_date}>
              بعدی
            </Button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="space-y-4">
          <div className="rounded-lg border border-border p-3 text-sm">
            <p className="font-medium">شما — مدیر پروژه</p>
            <p className="text-muted-foreground">به‌صورت خودکار اضافه می‌شوید</p>
          </div>

          <div className="space-y-2">
            <Label>افزودن عضو (اختیاری)</Label>
            <div className="flex gap-2">
              <Input
                placeholder="جستجو با نام یا ایمیل"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <Button variant="secondary" onClick={handleSearch}>
                جستجو
              </Button>
            </div>
            {searchResults.length > 0 && (
              <ul className="rounded-md border border-border">
                {searchResults.map((u) => (
                  <li key={u.user_id}>
                    <button
                      type="button"
                      className="w-full px-3 py-2 text-start text-sm hover:bg-muted"
                      onClick={() => addSearchedMember(u)}
                    >
                      {u.full_name} — {u.email || u.mobile}
                    </button>
                  </li>
                ))}
              </ul>
            )}
            {search.length >= 2 && searchResults.length === 0 && (
              <div className="space-y-2 rounded-md border border-dashed border-border p-3">
                <p className="text-sm text-muted-foreground">کاربر یافت نشد — دعوت‌نامه ارسال کنید</p>
                <Input
                  placeholder="ایمیل"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                />
                <Button variant="secondary" size="sm" onClick={addInviteMember}>
                  افزودن دعوت‌نامه
                </Button>
              </div>
            )}
            <select
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
              value={selectedRoleId}
              onChange={(e) => setSelectedRoleId(e.target.value)}
            >
              <option value="">نقش عضو</option>
              {roles.map((r: Role) => (
                <option key={r.id} value={r.id}>
                  {formatRoleLabel(r.role_name, t)}
                </option>
              ))}
            </select>
          </div>

          {members.length > 0 && (
            <ul className="space-y-1 text-sm">
              {members.map((m, i) => (
                <li key={i} className="rounded border border-border px-3 py-2">
                  {m.user?.full_name ?? m.email} —{" "}
                  {(() => {
                    const roleName = roles.find((r) => r.id === m.roleId)?.role_name;
                    return roleName ? formatRoleLabel(roleName, t) : null;
                  })()}
                </li>
              ))}
            </ul>
          )}

          <div className="flex flex-wrap justify-between gap-2 pt-4">
            <Button variant="ghost" onClick={() => setStep(2)}>
              قبلی
            </Button>
            <div className="flex gap-2">
              <Button variant="ghost" onClick={() => createMutation.mutate()} loading={createMutation.isPending}>
                ادامه بدون افزودن عضو
              </Button>
              <Button variant="primary" loading={createMutation.isPending} onClick={() => createMutation.mutate()}>
                ایجاد پروژه
              </Button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
