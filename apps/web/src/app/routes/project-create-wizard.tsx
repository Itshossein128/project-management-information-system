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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { LayoutTemplate, Check, Building2, CalendarDays, Users } from "lucide-react";

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
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const toast = useToast();
  const [step, setStep] = useState(1);
  const [codeEdited, setCodeEdited] = useState(false);
  const [searched, setSearched] = useState(false);

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
    try {
      const results = await lookupUsers(search.trim());
      setSearchResults(results);
      setSearched(true);
    } catch {
      toast.error(t("projectWizard.searchError", "جستجوی کاربران ناموفق بود. دوباره تلاش کنید."));
    }
  };

  const handlePmSearch = async () => {
    if (pmSearch.length < 2) return;
    try {
      const results = await lookupUsers(pmSearch.trim());
      setPmResults(results);
    } catch {
      toast.error(t("projectWizard.searchError", "جستجوی کاربران ناموفق بود. دوباره تلاش کنید."));
    }
  };

  const addSearchedMember = (user: UserLookupResult) => {

    if (!selectedRoleId) return;
    setMembers((prev) => [...prev, { user, roleId: selectedRoleId }]);
    setSearch("");
    setSearchResults([]);
    setSearched(false);
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
    <main className="page-main page-shell mx-auto px-4 py-8 sm:px-6 [&_input]:h-11 [&_input]:rounded-lg [&_input]:border-border [&_input]:bg-background [&_select]:min-h-11 [&_select]:rounded-lg [&_select]:focus-visible:outline-none [&_select]:focus-visible:ring-2 [&_select]:focus-visible:ring-ring">
      <Breadcrumb
        items={[
          { label: t("project.title"), href: `/${PATHS.PROJECT}` },
          { label: t("projectWizard.breadcrumb") },
        ]}
      />
      <div className="mb-7 flex flex-wrap items-end justify-between gap-3">
        <div>
          <PageHeader title={t("projectWizard.title")} />
          <p className="mt-1 text-sm leading-6 text-muted-foreground">اطلاعات پروژه را در سه مرحله وارد کنید. جزئیات تکمیلی را می‌توانید بعداً ویرایش کنید.</p>
        </div>
        <span className="rounded-full border border-border bg-card px-3 py-1 text-xs font-medium text-muted-foreground">مرحله {step} از ۳</span>
      </div>

      <nav aria-label="مراحل ایجاد پروژه" className="mb-6 grid grid-cols-3 gap-2 sm:gap-3">
        {steps.map((label, i) => {
          const Icon = [Building2, CalendarDays, Users][i];
          const active = step === i + 1;
          const complete = step > i + 1;
          return (
            <div key={label} aria-current={active ? "step" : undefined} className={`flex min-h-16 items-center gap-2 rounded-xl border px-3 py-3 sm:gap-3 sm:px-4 ${active ? "border-primary bg-primary text-primary-foreground shadow-sm" : "border-border bg-card text-muted-foreground"}`}>
              <span className={`flex size-9 shrink-0 items-center justify-center rounded-lg ${active ? "bg-primary-foreground/15" : "bg-muted"}`}>
                {complete ? <Check className="size-4" /> : <Icon className="size-4" />}
              </span>
              <span className="min-w-0"><span className="hidden text-xs opacity-75 sm:block">مرحله {i + 1}</span><span className="block text-xs font-semibold sm:text-sm">{label}</span></span>
            </div>
          );
        })}
      </nav>

      {step === 1 && (
        <div className="space-y-5">
          <section className="rounded-2xl border border-border bg-card p-5 shadow-sm sm:p-7">
            <div className="mb-6 border-b border-border pb-4">
              <h2 className="text-lg font-semibold">اطلاعات اصلی پروژه</h2>
              <p className="mt-1 text-sm text-muted-foreground">برای شناسایی پروژه، این اطلاعات را وارد کنید. فیلدهای ستاره‌دار الزامی هستند.</p>
            </div>
            <div className="grid gap-5 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <Label className="mb-2.5 leading-5" htmlFor="wizard-project-name">نام پروژه *</Label>
            <Input
              id="wizard-project-name"
              value={form.project_name}
              onChange={(e) => {
                const name = e.target.value;
                setForm((f) => ({
                  ...f,
                  project_name: name,
                  project_code: codeEdited ? f.project_code : suggestCode(name),
                }));
              }}
            />
          </div>
          <div>
            <Label className="mb-2.5 leading-5" htmlFor="wizard-project-code">کد پروژه *</Label>
            <Input
              id="wizard-project-code"
              value={form.project_code}
              onChange={(e) => { setCodeEdited(true); setForm((f) => ({ ...f, project_code: e.target.value })); }}
            />
          </div>
          <div>
            <Label className="mb-2.5 leading-5" htmlFor="wizard-employer">کارفرما *</Label>
            <Input
              id="wizard-employer"
              value={form.employer}
              onChange={(e) => setForm((f) => ({ ...f, employer: e.target.value }))}
            />
          </div>
            </div>
          </section>
          <details className="rounded-lg border border-border bg-card p-4">
            <summary className="cursor-pointer font-medium">{t("projectWizard.useTemplate")} <span className="text-sm font-normal text-muted-foreground">(اختیاری)</span></summary>
            <p className="mt-2 text-sm text-muted-foreground">برای شروع از ساختار آماده، یک قالب انتخاب کنید.</p>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {templates.map((tpl) => (
                <button
                  key={tpl.template_id}
                  type="button"
                  aria-pressed={selectedTemplateId === tpl.template_id}
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
          </details>

          <section className="rounded-2xl border border-border bg-card p-5 shadow-sm sm:p-7">
            <div className="mb-6 border-b border-border pb-4"><h2 className="text-lg font-semibold">جزئیات پروژه</h2><p className="mt-1 text-sm text-muted-foreground">این اطلاعات اختیاری هستند و بعداً نیز قابل تکمیل‌اند.</p></div>
            <div className="grid gap-5 sm:grid-cols-2">
          <div>
            <Label className="mb-2.5 leading-5" htmlFor="wizard-purpose">{t("project.purpose", "هدف پروژه")}</Label>
            <Input id="wizard-purpose"
              value={form.purpose ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, purpose: e.target.value }))}
            />
          </div>
          <div>
            <Label className="mb-2.5 leading-5" htmlFor="wizard-scope">{t("project.scope", "شرح محدوده")}</Label>
            <Input id="wizard-scope"
              value={form.scope_description ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, scope_description: e.target.value }))}
            />
          </div>
          <div>
            <Label className="mb-2.5 leading-5" htmlFor="wizard-deliverables">{t("project.deliverables", "خروجی‌های اصلی")}</Label>
            <Input id="wizard-deliverables"
              value={form.main_deliverables ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, main_deliverables: e.target.value }))}
            />
          </div>
          <div className="sm:col-span-2 rounded-lg bg-muted/50 p-4" data-testid="wizard-contractor-deferred">
            <Label>{t("project.contractor", "پیمانکار")}</Label>
            <p className="mt-1 text-sm text-muted-foreground">
              {t(
                "projectWizard.contractorDeferredHelp",
                "پس از ایجاد پروژه، پیمانکار را از صفحه ذینفعان با نقش پیمانکار ثبت کنید؛ سپس در تنظیمات پروژه انتخاب کنید. تایپ آزاد مجاز نیست.",
              )}
            </p>
          </div>
          <div>
            <Label className="mb-2.5 leading-5" htmlFor="wizard-consultant">مشاور</Label>
            <Input id="wizard-consultant"
              value={form.consultant}
              onChange={(e) => setForm((f) => ({ ...f, consultant: e.target.value }))}
            />
          </div>
          <div>
            <Label className="mb-2.5 leading-5" htmlFor="wizard-contract-number">{t("project.contractNumber", "شماره قرارداد")}</Label>
            <Input
              id="wizard-contract-number"
              data-testid="wizard-contract-number"
              value={form.contract_number ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, contract_number: e.target.value }))}
            />
          </div>
          <div>
            <Label className="mb-2.5 leading-5" htmlFor="wizard-contract-type">نوع قرارداد</Label>
            <Select dir={i18n.dir()} value={form.contract_type || "__none__"} onValueChange={(value) => setForm((f) => ({ ...f, contract_type: value === "__none__" ? "" : value }))}>
              <SelectTrigger id="wizard-contract-type" data-testid="wizard-contract-type" className="h-11 w-full rounded-lg border-border bg-background data-[size=default]:h-11"><SelectValue /></SelectTrigger>
              <SelectContent position="popper"><SelectItem value="__none__">انتخاب نشده</SelectItem>{contractTypes.map((ct) => <SelectItem key={ct.id} value={ct.code}>{ct.code} — {ct.name_fa || ct.name_en}</SelectItem>)}</SelectContent>
            </Select>
          </div>
          <div>
            <Label className="mb-2.5 leading-5" htmlFor="wizard-currency">{t("projectSettings.currency", "واحد پول")}</Label>
            <Select dir={i18n.dir()} value={form.currency ?? "IRR"} onValueChange={(value) => setForm((f) => ({ ...f, currency: value as ProjectCurrency }))}>
              <SelectTrigger id="wizard-currency" data-testid="wizard-currency" className="h-11 w-full rounded-lg border-border bg-background data-[size=default]:h-11"><SelectValue /></SelectTrigger>
              <SelectContent position="popper"><SelectItem value="IRR">{t("projectSettings.currencyIrr", "ریال (IRR)")}</SelectItem><SelectItem value="IRT">{t("projectSettings.currencyIrt", "تومان (IRT)")}</SelectItem></SelectContent>
            </Select>
          </div>
          <div>
            <Label className="mb-2.5 leading-5" htmlFor="wizard-owning-unit">{t("centralData.owningUnit", "واحد سازمانی مالک")}</Label>
            <Select dir={i18n.dir()} value={form.owning_unit || "__none__"} onValueChange={(value) => setForm((f) => ({ ...f, owning_unit: value === "__none__" ? null : value }))}>
              <SelectTrigger id="wizard-owning-unit" data-testid="wizard-owning-unit" className="h-11 w-full rounded-lg border-border bg-background data-[size=default]:h-11"><SelectValue /></SelectTrigger>
              <SelectContent position="popper"><SelectItem value="__none__">انتخاب نشده</SelectItem>{orgUnits.map((u) => <SelectItem key={u.id} value={u.id}>{u.code} — {u.name}</SelectItem>)}</SelectContent>
            </Select>
          </div>
          <div className="space-y-2" data-testid="wizard-project-manager">
            <Label className="mb-2.5 leading-5" htmlFor="wizard-pm-search">{t("project.projectManager", "مدیر پروژه")}</Label>
            <div className="flex gap-2">
              <Input
                id="wizard-pm-search"
                placeholder={t("projectWizard.searchPm", "جستجوی مدیر پروژه")}
                value={pmSearch}
                onChange={(e) => setPmSearch(e.target.value)}
              />
              <Button type="button" variant="secondary" className="h-11 rounded-lg" onClick={handlePmSearch}>
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
            <Label className="mb-2.5 leading-5" htmlFor="wizard-location">موقعیت</Label>
            <Input id="wizard-location"
              value={form.location}
              onChange={(e) => setForm((f) => ({ ...f, location: e.target.value }))}
            />
          </div>
            </div>
          </section>
          <div className="flex justify-end gap-2 border-t border-border pt-5">
            <Link to={`/${PATHS.PROJECT}`}>
              <Button variant="ghost">انصراف</Button>
            </Link>
            <Button
              variant="primary"
              onClick={() => setStep(2)}
              disabled={!form.project_name.trim() || !form.project_code.trim() || !form.employer.trim()}
            >
              بعدی
            </Button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-5 rounded-2xl border border-border bg-card p-5 shadow-sm sm:p-7">
          <div className="border-b border-border pb-4"><h2 className="text-lg font-semibold">زمان‌بندی و مبلغ قرارداد</h2><p className="mt-1 text-sm text-muted-foreground">تاریخ شروع الزامی است؛ سایر موارد را می‌توانید بعداً تکمیل کنید.</p></div>
          <JalaliDatePicker
            name="start_date"
            fieldClassName="gap-2.5"
            label="تاریخ شروع *"
            value={form.start_date}
            onChange={(v) => setForm((f) => ({ ...f, start_date: v }))}
          />
          <JalaliDatePicker
            name="planned_finish_date"
            fieldClassName="gap-2.5"
            label="تاریخ پایان برنامه‌ای"
            value={form.planned_finish_date ?? ""}
            onChange={(v) => setForm((f) => ({ ...f, planned_finish_date: v }))}
          />
          <div>
            <Label className="mb-2.5 leading-5" htmlFor="wizard-amount">مبلغ قرارداد</Label>
            <Input id="wizard-amount"
              type="text"
              inputMode="decimal"
              value={formatWithCommas(form.contract_amount ?? "")}
              onChange={(e) => setForm((f) => ({ ...f, contract_amount: toRawNumericString(e.target.value) }))}
            />
          </div>
          {form.start_date && form.planned_finish_date && durationDays === null ? (
            <p role="alert" className="text-sm text-destructive">تاریخ پایان نمی‌تواند پیش از تاریخ شروع باشد.</p>
          ) : null}
          {durationDays != null ? (
            <p className="text-sm text-muted-foreground">مدت قرارداد: {durationDays} روز</p>
          ) : null}
          <div className="flex justify-between gap-2 pt-4">
            <Button variant="ghost" onClick={() => setStep(1)}>
              قبلی
            </Button>
            <Button variant="primary" onClick={() => setStep(3)} disabled={!form.start_date || (Boolean(form.planned_finish_date) && durationDays === null)}>
              بعدی
            </Button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="space-y-5 rounded-2xl border border-border bg-card p-5 shadow-sm sm:p-7">
          <div className="border-b border-border pb-4"><h2 className="text-lg font-semibold">تیم اولیه پروژه</h2><p className="mt-1 text-sm text-muted-foreground">افزودن اعضا اختیاری است و می‌توانید بعداً هم تیم را تکمیل کنید.</p></div>
          <div className="rounded-lg border border-border p-3 text-sm">
            <p className="font-medium">شما — مدیر پروژه</p>
            <p className="text-muted-foreground">به‌صورت خودکار اضافه می‌شوید</p>
          </div>

          <div className="space-y-2">
            <p className="font-medium">افزودن عضو (اختیاری)</p>
            <Label className="mb-2.5 leading-5" htmlFor="wizard-member-role">نقش عضو</Label>
            <Select dir={i18n.dir()} value={selectedRoleId} onValueChange={setSelectedRoleId}>
              <SelectTrigger id="wizard-member-role" className="h-11 w-full rounded-lg border-border bg-background data-[size=default]:h-11"><SelectValue placeholder="نقش عضو را انتخاب کنید" /></SelectTrigger>
              <SelectContent position="popper">{roles.map((r: Role) => <SelectItem key={r.id} value={r.id}>{formatRoleLabel(r.role_name, t)}</SelectItem>)}</SelectContent>
            </Select>
            <Label className="mb-2.5 leading-5" htmlFor="wizard-member-search">جستجوی عضو</Label>
            <div className="flex gap-2">
              <Input
                id="wizard-member-search"
                placeholder="جستجو با نام یا ایمیل"
                value={search}
                onChange={(e) => { setSearch(e.target.value); setSearchResults([]); setSearched(false); }}
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
                      className="w-full px-3 py-2 text-start text-sm hover:bg-muted disabled:opacity-50"
                      disabled={!selectedRoleId}
                      onClick={() => addSearchedMember(u)}
                    >
                      {u.full_name} — {u.email || u.mobile}
                    </button>
                  </li>
                ))}
              </ul>
            )}
            {searched && searchResults.length === 0 && (
              <div className="space-y-2 rounded-md border border-dashed border-border p-3">
                <p className="text-sm text-muted-foreground">کاربر یافت نشد — دعوت‌نامه ارسال کنید</p>
                <Label className="mb-2.5 leading-5" htmlFor="wizard-invite-email">ایمیل دعوت‌شونده</Label>
                <Input
                  id="wizard-invite-email"
                  type="email"
                  placeholder="ایمیل"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                />
                <Button variant="secondary" size="sm" disabled={!selectedRoleId || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(inviteEmail)} onClick={addInviteMember}>
                  افزودن دعوت‌نامه
                </Button>
              </div>
            )}

          </div>

          {members.length > 0 && (
            <ul className="space-y-1 text-sm">
              {members.map((m, i) => (
                <li key={i} className="flex items-center justify-between gap-2 rounded border border-border px-3 py-2">
                  <span>
                  {m.user?.full_name ?? m.email} —{" "}
                  {(() => {
                    const roleName = roles.find((r) => r.id === m.roleId)?.role_name;
                    return roleName ? formatRoleLabel(roleName, t) : null;
                  })()}</span>
                  <Button type="button" variant="ghost" size="sm" onClick={() => setMembers((prev) => prev.filter((_, index) => index !== i))} aria-label={`حذف ${m.user?.full_name || m.email || "عضو"}`}>حذف</Button>
                </li>
              ))}
            </ul>
          )}

          <div className="flex flex-wrap justify-between gap-2 pt-4">
            <Button variant="ghost" onClick={() => setStep(2)}>
              قبلی
            </Button>
            <div className="flex gap-2">

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
