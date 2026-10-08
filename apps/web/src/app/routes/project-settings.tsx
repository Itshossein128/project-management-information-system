import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams, useNavigate } from "react-router";
import { useTranslation } from "react-i18next";
import { ProjectProvider, usePermission } from "@/app/contexts/project-context";
import {
  asList,
  fetchOrganizationUnits,
} from "@/app/lib/api/central-data";
import {
  fetchProject,
  updateProject,
  deleteProject,
  type CreateProjectPayload,
  type ProjectCurrency,
} from "@/app/lib/api/projects";
import {
  createFiscalLock,
  listCapabilities,
  listFiscalLocks,
  updateCapability,
} from "@/app/lib/api/project-core";
import { PATHS } from "@/app/routeVars";
import { EmptyState } from "@/components/layout/empty-state";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { ProjectChangeRequestPanel } from "@/components/projects/ProjectChangeRequestPanel";
import { Input, Label, Select, ToggleSwitch } from "@/components/form";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

function ProjectSettingsContent() {
  const { projectId } = useParams();
  const id = projectId ?? "";
  const { t } = useTranslation();
  const navigate = useNavigate();
  const toast = useToast();
  const qc = useQueryClient();
  const { has } = usePermission(id);
  const canEdit = has("edit_project");

  const { data: project, isLoading, isError, refetch } = useQuery({
    queryKey: ["project", id],
    queryFn: () => fetchProject(id),
    enabled: Boolean(id),
  });

  const {
    data: capabilities = [],
    isLoading: capsLoading,
  } = useQuery({
    queryKey: ["project-capabilities", id],
    queryFn: () => listCapabilities(id),
    enabled: Boolean(id),
  });

  const {
    data: fiscalLocks = [],
    isLoading: locksLoading,
  } = useQuery({
    queryKey: ["project-fiscal-locks", id],
    queryFn: () => listFiscalLocks(id),
    enabled: Boolean(id),
  });

  const { data: orgUnitsRaw } = useQuery({
    queryKey: ["organization-units"],
    queryFn: fetchOrganizationUnits,
  });
  const orgUnits = asList(orgUnitsRaw ?? []);

  const [form, setForm] = useState<Partial<CreateProjectPayload>>({});
  const [lockForm, setLockForm] = useState({
    period_start: "",
    period_end: "",
    reason: "",
  });

  const saveMutation = useMutation({
    mutationFn: (payload: Partial<CreateProjectPayload>) =>
      updateProject(id, payload),
    onSuccess: () => {
      toast.success(t("projectSettings.saveSuccess", "تغییرات ذخیره شد"));
      void qc.invalidateQueries({ queryKey: ["project", id] });
      void qc.invalidateQueries({ queryKey: ["projects"] });
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteProject(id),
    onSuccess: () => {
      toast.success(t("projectSettings.deleteSuccess", "پروژه با موفقیت حذف شد"));
      void qc.invalidateQueries({ queryKey: ["projects"] });
      navigate(`/${PATHS.PROJECT}`);
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const capabilityMutation = useMutation({
    mutationFn: ({
      capabilityKey,
      enabled,
    }: {
      capabilityKey: string;
      enabled: boolean;
    }) =>
      updateCapability(id, capabilityKey, {
        enabled,
        mode: enabled ? "optional" : "disabled",
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["project-capabilities", id] });
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const lockMutation = useMutation({
    mutationFn: () => createFiscalLock(id, lockForm),
    onSuccess: () => {
      toast.success(
        t("projectSettings.fiscalLockCreated", "دوره مالی قفل شد"),
      );
      setLockForm({ period_start: "", period_end: "", reason: "" });
      void qc.invalidateQueries({ queryKey: ["project-fiscal-locks", id] });
    },
    onError: (err: Error) => toast.error(err.message),
  });

  if (isLoading) {
    return <LoadingSkeleton rows={6} />;
  }
  if (isError) {
    return <QueryErrorState onRetry={() => void refetch()} />;
  }
  if (!project) {
    return <EmptyState title={t("common.projectNotFound")} />;
  }

  const protectedLocked = ["active", "suspended", "completed", "archived"].includes(
    project.status,
  );
  const isDraftLike = project.status === "draft" || project.status === "pending_approval";

  const values = {
    project_name: form.project_name ?? project.project_name,
    project_code: form.project_code ?? project.project_code,
    employer: form.employer ?? project.employer,
    contractor: form.contractor ?? project.contractor ?? "",
    consultant: form.consultant ?? project.consultant ?? "",
    location: form.location ?? project.location ?? "",
    contract_type: form.contract_type ?? project.contract_type ?? "",
    contract_number: form.contract_number ?? project.contract_number ?? "",
    purpose: form.purpose ?? project.purpose ?? "",
    scope_description: form.scope_description ?? project.scope_description ?? "",
    main_deliverables: form.main_deliverables ?? project.main_deliverables ?? "",
    start_date: form.start_date ?? project.start_date ?? "",
    planned_finish_date:
      form.planned_finish_date ?? project.planned_finish_date ?? "",
    contract_amount:
      form.contract_amount ?? project.contract_amount ?? "",
    currency: (form.currency ?? project.currency ?? "IRR") as ProjectCurrency,
    owning_unit: form.owning_unit ?? project.owning_unit ?? "",
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!canEdit) return;
    saveMutation.mutate({
      project_name: values.project_name,
      ...(protectedLocked
        ? {}
        : {
            employer: values.employer,
            start_date: values.start_date || undefined,
            planned_finish_date: values.planned_finish_date || undefined,
            contract_amount: values.contract_amount || undefined,
            scope_description: values.scope_description || undefined,
          }),
      purpose: values.purpose || undefined,
      main_deliverables: values.main_deliverables || undefined,
      contract_number: values.contract_number || undefined,
      contractor: values.contractor || undefined,
      consultant: values.consultant || undefined,
      location: values.location || undefined,
      contract_type: values.contract_type || undefined,
      currency: values.currency,
      owning_unit: values.owning_unit || null,
    });
  };

  return (
    <>
      <Breadcrumb
        items={[
          { label: t("project.title", "پروژه‌ها"), href: `/${PATHS.PROJECT}` },
          {
            label: project.project_name,
            href: `/${PATHS.PROJECT}/${id}/${PATHS.PROJECT_OVERVIEW}`,
          },
          { label: t("projectSettings.title", "تنظیمات") },
        ]}
      />
      <PageHeader
        title={t("projectSettings.title", "تنظیمات پروژه")}
        subtitle={
          canEdit
            ? undefined
            : t("projectSettings.readOnly", "نمایش فقط خواندنی")
        }
      />

      <form onSubmit={handleSubmit} className='mx-auto max-w-2xl space-y-4'>
        <div>
          <Label htmlFor='input-projectName'>
            {t("projectSettings.projectName", "نام پروژه")}
          </Label>
          <Input
            id='input-projectName'
            value={values.project_name}
            disabled={!canEdit}
            onChange={(e) =>
              setForm((f) => ({ ...f, project_name: e.target.value }))
            }
            required
          />
        </div>
        <div>
          <Label htmlFor='input-projectCode'>
            {t("projectSettings.projectCode", "کد پروژه")}
          </Label>
          <Input
            id='input-projectCode'
            value={values.project_code}
            disabled
            readOnly
          />
        </div>
        <div>
          <Label htmlFor='input-employer'>
            {t("projectSettings.employer", "کارفرما")}
          </Label>
          <Input
            id='input-employer'
            value={values.employer}
            disabled={
              !canEdit ||
              ["active", "suspended", "completed", "archived"].includes(project.status)
            }
            onChange={(e) =>
              setForm((f) => ({ ...f, employer: e.target.value }))
            }
            required
          />
          {protectedLocked ? (
            <p className="mt-1 text-xs text-muted-foreground">
              {t("project.protectedFieldHint")}
            </p>
          ) : null}
        </div>
        <div>
          <Label htmlFor="input-purpose">{t("project.purpose", "هدف پروژه")}</Label>
          <Input
            id="input-purpose"
            data-testid="settings-purpose"
            value={values.purpose}
            disabled={!canEdit}
            onChange={(e) => setForm((f) => ({ ...f, purpose: e.target.value }))}
          />
        </div>
        <div>
          <Label htmlFor="input-scope">{t("project.scope", "شرح محدوده")}</Label>
          <Input
            id="input-scope"
            data-testid="settings-scope"
            value={values.scope_description}
            disabled={!canEdit || protectedLocked}
            onChange={(e) =>
              setForm((f) => ({ ...f, scope_description: e.target.value }))
            }
          />
          {protectedLocked ? (
            <p className="mt-1 text-xs text-muted-foreground">
              {t("project.protectedFieldHint")}
            </p>
          ) : null}
        </div>
        <div>
          <Label htmlFor="input-deliverables">
            {t("project.deliverables", "خروجی‌های اصلی")}
          </Label>
          <Input
            id="input-deliverables"
            data-testid="settings-deliverables"
            value={values.main_deliverables}
            disabled={!canEdit}
            onChange={(e) =>
              setForm((f) => ({ ...f, main_deliverables: e.target.value }))
            }
          />
        </div>
        <div>
          <Label htmlFor="input-contract-number">
            {t("project.contractNumber", "شماره قرارداد")}
          </Label>
          <Input
            id="input-contract-number"
            data-testid="settings-contract-number"
            value={values.contract_number}
            disabled={!canEdit}
            onChange={(e) =>
              setForm((f) => ({ ...f, contract_number: e.target.value }))
            }
          />
        </div>
        <div>
          <Label htmlFor="input-contract-amount">
            {t("project.amount", "مبلغ قرارداد")}
          </Label>
          <Input
            id="input-contract-amount"
            data-testid="settings-contract-amount"
            value={values.contract_amount}
            disabled={!canEdit || protectedLocked}
            onChange={(e) =>
              setForm((f) => ({ ...f, contract_amount: e.target.value }))
            }
          />
          {protectedLocked ? (
            <p className="mt-1 text-xs text-muted-foreground">
              {t("project.protectedFieldHint")}
            </p>
          ) : null}
        </div>
        {isDraftLike ? (
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <Label htmlFor="input-start-date">{t("project.startDate", "تاریخ شروع")}</Label>
              <Input
                id="input-start-date"
                data-testid="settings-start-date"
                type="date"
                value={values.start_date}
                disabled={!canEdit}
                onChange={(e) =>
                  setForm((f) => ({ ...f, start_date: e.target.value }))
                }
              />
            </div>
            <div>
              <Label htmlFor="input-finish-date">
                {t("project.finish", "تاریخ پایان")}
              </Label>
              <Input
                id="input-finish-date"
                data-testid="settings-finish-date"
                type="date"
                value={values.planned_finish_date}
                disabled={!canEdit}
                onChange={(e) =>
                  setForm((f) => ({
                    ...f,
                    planned_finish_date: e.target.value,
                  }))
                }
              />
            </div>
          </div>
        ) : null}
        <div>
          <Label htmlFor='input-contractor'>
            {t("projectSettings.contractor", "پیمانکار")}
          </Label>
          <Input
            id='input-contractor'
            value={values.contractor}
            disabled={!canEdit}
            onChange={(e) =>
              setForm((f) => ({ ...f, contractor: e.target.value }))
            }
          />
        </div>
        <div>
          <Label htmlFor='input-consultant'>
            {t("projectSettings.consultant", "مشاور")}
          </Label>
          <Input
            id='input-consultant'
            value={values.consultant}
            disabled={!canEdit}
            onChange={(e) =>
              setForm((f) => ({ ...f, consultant: e.target.value }))
            }
          />
        </div>
        <div>
          <Label htmlFor='input-location'>
            {t("projectSettings.location", "موقعیت")}
          </Label>
          <Input
            id='input-location'
            value={values.location}
            disabled={!canEdit}
            onChange={(e) =>
              setForm((f) => ({ ...f, location: e.target.value }))
            }
          />
        </div>
        <Select
          name='currency'
          id='input-currency'
          label={t("projectSettings.currency", "واحد پول")}
          value={values.currency}
          disabled={!canEdit}
          options={[
            {
              value: "IRR",
              label: t("projectSettings.currencyIrr", "ریال (IRR)"),
            },
            {
              value: "IRT",
              label: t("projectSettings.currencyIrt", "تومان (IRT)"),
            },
          ]}
          onChange={(e) =>
            setForm((f) => ({
              ...f,
              currency: e.target.value as ProjectCurrency,
            }))
          }
        />
        <Select
          name='owning_unit'
          id='input-owning-unit'
          label={t("centralData.owningUnit", "واحد سازمانی مالک")}
          value={values.owning_unit ?? ""}
          disabled={!canEdit}
          options={[
            { value: "", label: "—" },
            ...orgUnits.map((u) => ({
              value: u.id,
              label: `${u.code} — ${u.name}`,
            })),
          ]}
          onChange={(e) =>
            setForm((f) => ({
              ...f,
              owning_unit: e.target.value || null,
            }))
          }
        />

        {canEdit ? (
          <div className='flex items-center justify-between border-t pt-4'>
            <Button type='submit' loading={saveMutation.isPending}>
              {t("projectSettings.save", "ذخیره")}
            </Button>
            <Button
              type='button'
              variant='danger'
              loading={deleteMutation.isPending}
              onClick={() => {
                if (
                  window.confirm(
                    t(
                      "projectSettings.deleteConfirm",
                      "آیا از حذف این پروژه و تمامی داده‌های مربوط به آن اطمینان دارید؟",
                    ),
                  )
                ) {
                  deleteMutation.mutate();
                }
              }}
            >
              {t("projectSettings.delete", "حذف پروژه")}
            </Button>
          </div>
        ) : null}
      </form>

      {protectedLocked ? <ProjectChangeRequestPanel projectId={id} /> : null}

      <section className='mx-auto mt-10 max-w-2xl space-y-3 border-t pt-8'>
        <h2 className='text-base font-semibold'>
          {t("projectSettings.capabilities", "قابلیت‌ها")}
        </h2>
        <p className='text-sm text-muted-foreground'>
          {t(
            "projectSettings.capabilitiesHint",
            "غیرفعال‌سازی یک قابلیت، تاریخچه را حذف نمی‌کند؛ فقط ایجاد/ویرایش جدید را مسدود می‌کند.",
          )}
        </p>
        {capsLoading ? (
          <p className='text-sm text-muted-foreground'>{t("common.loading")}</p>
        ) : capabilities.length === 0 ? (
          <p className='text-sm text-muted-foreground'>
            {t("projectSettings.capabilitiesEmpty", "قابلیتی تعریف نشده است")}
          </p>
        ) : (
          <ul className='space-y-2'>
            {capabilities.map((cap) => (
              <li
                key={cap.capability_key}
                className='flex items-center justify-between gap-3 rounded-md border border-border px-3 py-2'
              >
                <span className='text-sm'>{cap.capability_key}</span>
                <ToggleSwitch
                  name={`cap-${cap.capability_key}`}
                  checked={cap.enabled}
                  disabled={!canEdit || capabilityMutation.isPending}
                  onChange={(e) => {
                    capabilityMutation.mutate({
                      capabilityKey: cap.capability_key,
                      enabled: Boolean(e.target.checked),
                    });
                  }}
                  label={
                    cap.enabled
                      ? t("common.enabled", "فعال")
                      : t("common.disabled", "غیرفعال")
                  }
                />
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className='mx-auto mt-10 max-w-2xl space-y-3 border-t pt-8'>
        <h2 className='text-base font-semibold'>
          {t("projectSettings.fiscalLock", "قفل دوره مالی")}
        </h2>
        {locksLoading ? (
          <p className='text-sm text-muted-foreground'>{t("common.loading")}</p>
        ) : fiscalLocks.length > 0 ? (
          <ul className='mb-4 space-y-1 text-sm text-muted-foreground'>
            {fiscalLocks.map((lock) => (
              <li key={lock.id}>
                {lock.period_start} → {lock.period_end}
                {lock.reason ? ` — ${lock.reason}` : ""}
                {lock.is_active === false
                  ? ` (${t("common.inactive", "غیرفعال")})`
                  : ""}
              </li>
            ))}
          </ul>
        ) : null}

        {canEdit ? (
          <form
            className='space-y-3'
            onSubmit={(e) => {
              e.preventDefault();
              if (!lockForm.period_start || !lockForm.period_end || !lockForm.reason.trim()) {
                toast.error(
                  t(
                    "projectSettings.fiscalLockRequired",
                    "تاریخ شروع، پایان و دلیل الزامی است",
                  ),
                );
                return;
              }
              lockMutation.mutate();
            }}
          >
            <div className='grid gap-3 sm:grid-cols-2'>
              <div>
                <Label htmlFor='input-periodStart'>
                  {t("projectSettings.periodStart", "شروع دوره")}
                </Label>
                <Input
                  id='input-periodStart'
                  type='date'
                  value={lockForm.period_start}
                  onChange={(e) =>
                    setLockForm((f) => ({ ...f, period_start: e.target.value }))
                  }
                  required
                />
              </div>
              <div>
                <Label htmlFor='input-periodEnd'>
                  {t("projectSettings.periodEnd", "پایان دوره")}
                </Label>
                <Input
                  id='input-periodEnd'
                  type='date'
                  value={lockForm.period_end}
                  onChange={(e) =>
                    setLockForm((f) => ({ ...f, period_end: e.target.value }))
                  }
                  required
                />
              </div>
            </div>
            <div>
              <Label htmlFor='input-lockReason'>
                {t("projectSettings.lockReason", "دلیل")}
              </Label>
              <Input
                id='input-lockReason'
                value={lockForm.reason}
                onChange={(e) =>
                  setLockForm((f) => ({ ...f, reason: e.target.value }))
                }
                required
              />
            </div>
            <Button type='submit' loading={lockMutation.isPending}>
              {t("projectSettings.createFiscalLock", "قفل کردن دوره")}
            </Button>
          </form>
        ) : null}
      </section>
    </>
  );
}

export default function ProjectSettingsPage() {
  const { projectId = "" } = useParams();

  return (
    <main className='page-main page-shell mx-auto px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <ProjectSettingsContent />
      </ProjectProvider>
    </main>
  );
}
