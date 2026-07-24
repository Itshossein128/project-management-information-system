import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router";
import {
  ProjectProvider,
  usePermission,
  useProject,
} from "@/app/contexts/project-context";
import {
  createEquipment,
  fetchEquipmentRegistry,
  fetchEquipmentUtilization,
  fetchEquipmentUtilizationSummary,
} from "@/app/lib/api/equipment";
import { PATHS } from "@/app/routeVars";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { Button } from "@/components/ui/sprint-button";
import { Drawer } from "@/components/ui/drawer";
import { useToast } from "@/components/ui/toast";

function Content() {
  const { t } = useTranslation();

  const { projectId } = useProject();
  const { has } = usePermission(projectId);
  const canEdit = has("edit_reports");
  const toast = useToast();
  const qc = useQueryClient();
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [registryOpen, setRegistryOpen] = useState(false);
  const [form, setForm] = useState({
    equipment_code: "",
    equipment_name: "",
    ownership_type: "owned",
    equipment_type: "",
    plate_number: "",
  });

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ["equipment-util-summary", projectId, dateFrom, dateTo],
    queryFn: () =>
      fetchEquipmentUtilizationSummary(projectId, {
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      }),
  });

  const { data: rows = [], isLoading } = useQuery({
    queryKey: ["equipment-util", projectId, dateFrom, dateTo],
    queryFn: () =>
      fetchEquipmentUtilization(projectId, {
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      }),
  });

  const { data: registry } = useQuery({
    queryKey: ["equipment-registry", projectId],
    queryFn: async () => {
      const res = await fetchEquipmentRegistry(projectId);
      return Array.isArray(res) ? res : res.results;
    },
  });

  const create = useMutation({
    mutationFn: () => createEquipment(projectId, form),
    onSuccess: () => {
      toast.success("دستگاه ثبت شد");
      setRegistryOpen(false);
      void qc.invalidateQueries({
        queryKey: ["equipment-registry", projectId],
      });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (summaryLoading || isLoading) return <LoadingSkeleton rows={8} />;

  return (
    <div className='space-y-6'>
      <div className='flex flex-wrap items-end gap-3'>
        <JalaliDatePicker
          name='from'
          label='از تاریخ'
          value={dateFrom}
          onChange={setDateFrom}
        />
        <JalaliDatePicker
          name='to'
          label='تا تاریخ'
          value={dateTo}
          onChange={setDateTo}
        />
        {canEdit ? (
          <Button
            size='sm'
            className='ms-auto'
            onClick={() => setRegistryOpen(true)}
          >
            ثبت دستگاه جدید
          </Button>
        ) : null}
      </div>

      {summary ? (
        <div className='grid gap-3 sm:grid-cols-2 lg:grid-cols-4'>
          {[
            ["تعداد دستگاه", summary.equipment_count],
            [
              "میانگین بهره‌وری",
              summary.avg_utilization_rate != null
                ? `${summary.avg_utilization_rate}%`
                : "—",
            ],
            ["ساعات مفید", summary.total_productive_hours],
            ["ساعات بیکاری", summary.total_idle_hours],
          ].map(([label, value]) => (
            <div
              key={String(label)}
              className='rounded-lg border border-border p-4'
            >
              <p className='text-xs text-muted-foreground'>{label}</p>
              <p className='text-xl font-semibold'>{value}</p>
            </div>
          ))}
        </div>
      ) : null}

      <div className='overflow-x-auto rounded-lg border border-border'>
        <table className='w-full text-sm'>
          <thead className='bg-muted/50'>
            <tr>
              {[
                "دستگاه",
                "کد",
                "ساعات مفید",
                "بیکاری",
                "بهره‌وری",
                "هزینه",
                "لاگ",
              ].map((h) => (
                <th key={h} className='px-3 py-2 text-start'>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td
                  colSpan={7}
                  className='px-3 py-8 text-center text-muted-foreground'
                >
                  داده‌ای یافت نشد
                </td>
              </tr>
            ) : (
              rows.map((r) => (
                <tr
                  key={`${r.equipment_name}-${r.equipment_code}`}
                  className='border-t border-border'
                >
                  <td className='px-3 py-2'>{r.equipment_name}</td>
                  <td className='px-3 py-2 font-mono text-xs'>
                    {r.equipment_code || "—"}
                  </td>
                  <td className='px-3 py-2'>{r.productive_hours}</td>
                  <td className='px-3 py-2'>{r.idle_hours}</td>
                  <td className='px-3 py-2'>
                    {r.utilization_rate != null
                      ? `${r.utilization_rate}%`
                      : "—"}
                  </td>
                  <td className='px-3 py-2'>
                    {r.total_cost.toLocaleString("fa-IR")}
                  </td>
                  <td className='px-3 py-2'>{r.log_count}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {registry && registry.length > 0 ? (
        <div className='space-y-2'>
          <h3 className='text-sm font-medium'>
            فهرست دستگاه‌ها ({registry.length})
          </h3>
          <div className='flex flex-wrap gap-2'>
            {registry.map((e) => (
              <span
                key={e.id}
                className='rounded-md border border-border px-2 py-1 text-xs'
              >
                {e.equipment_code} — {e.equipment_name}
              </span>
            ))}
          </div>
        </div>
      ) : null}

      <Drawer
        isOpen={registryOpen}
        onClose={() => setRegistryOpen(false)}
        title='ثبت دستگاه'
        footer={
          <Button onClick={() => create.mutate()} loading={create.isPending}>
            ذخیره
          </Button>
        }
      >
        <div className='space-y-3 p-4'>
          <input
            className='w-full rounded border px-2 py-1'
            placeholder='کد دستگاه'
            value={form.equipment_code}
            onChange={(e) =>
              setForm((f) => ({ ...f, equipment_code: e.target.value }))
            }
          />
          <input
            className='w-full rounded border px-2 py-1'
            placeholder='نام دستگاه'
            value={form.equipment_name}
            onChange={(e) =>
              setForm((f) => ({ ...f, equipment_name: e.target.value }))
            }
          />
          <select
            className='w-full rounded border px-2 py-1'
            value={form.ownership_type}
            onChange={(e) =>
              setForm((f) => ({ ...f, ownership_type: e.target.value }))
            }
          >
            <option value='owned'>تملیکی</option>
            <option value='rented'>اجاره‌ای</option>
          </select>
        </div>
      </Drawer>
    </div>
  );
}

export default function ProjectEquipmentUtilizationPage() {
  const { t, i18n } = useTranslation();
  const { projectId = "" } = useParams();
  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "بهره‌وری ماشین‌آلات" },
          ]}
        />
        <PageHeader title={t("pages.equipmentUtilization.title")} />
        <p className='text-sm text-muted-foreground'>
          <Link
            className='text-primary hover:underline'
            to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_EQUIPMENT_LOG}`}
          >
            کارکرد روزانه
          </Link>
        </p>
        <Content />
      </ProjectProvider>
    </main>
  );
}
