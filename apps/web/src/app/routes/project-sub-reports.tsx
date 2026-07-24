import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import {
  createSubReport,
  fetchSubReports,
  submitSubReport,
} from "@/app/lib/api/hr-forms";
import { ProjectProvider, useProject } from "@/app/contexts/project-context";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { Button } from "@/components/ui/sprint-button";
import { Drawer } from "@/components/ui/drawer";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";

const DISCIPLINES = [
  { id: "civil", label: "ابنیه" },
  { id: "electrical", label: "برق" },
  { id: "mechanical", label: "مکانیک" },
] as const;

function Content() {
  const { t } = useTranslation();

  const { projectId } = useProject();
  const toast = useToast();
  const qc = useQueryClient();
  const [discipline, setDiscipline] = useState<string>("civil");
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    report_date: "",
    weather_condition: "sunny",
    form_code: "",
  });

  const { data, isLoading } = useQuery({
    queryKey: ["sub-reports", projectId, discipline],
    queryFn: () => fetchSubReports(projectId, discipline),
  });

  const save = useMutation({
    mutationFn: () =>
      createSubReport(projectId, {
        ...form,
        discipline,
        activities: [
          {
            row_number: 1,
            shift: "shift_1",
            crew_name: "گروه ۱",
            activity_description: "فعالیت نمونه",
            worker_count: 1,
          },
        ],
      }),
    onSuccess: () => {
      toast.success("ثبت شد");
      setOpen(false);
      void qc.invalidateQueries({ queryKey: ["sub-reports", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const rows = (data?.results ?? []) as {
    id: string;
    report_date: string;
    status: string;
    activity_count: number;
    weather_condition: string;
  }[];

  if (isLoading) return <LoadingSkeleton rows={6} />;

  return (
    <div className='space-y-4'>
      <div className='flex flex-wrap gap-2'>
        {DISCIPLINES.map((d) => (
          <Button
            key={d.id}
            variant={discipline === d.id ? "primary" : "secondary"}
            size='sm'
            onClick={() => setDiscipline(d.id)}
          >
            {d.label}
          </Button>
        ))}
        <Button className='ms-auto' size='sm' onClick={() => setOpen(true)}>
          گزارش جدید
        </Button>
      </div>
      <table className='w-full text-sm border rounded-lg'>
        <thead className='bg-muted/50'>
          <tr>
            {["تاریخ", "وضعیت جوی", "ردیف‌ها", "وضعیت", ""].map((h) => (
              <th key={h} className='px-3 py-2 text-start'>
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className='border-t'>
              <td className='px-3 py-2'>{r.report_date}</td>
              <td className='px-3 py-2'>{r.weather_condition}</td>
              <td className='px-3 py-2'>{r.activity_count}</td>
              <td className='px-3 py-2'>
                <Badge
                  variant={r.status === "approved" ? "success" : "info"}
                  label={r.status}
                />
              </td>
              <td className='px-3 py-2'>
                {r.status === "draft" ? (
                  <Button
                    size='sm'
                    variant='ghost'
                    onClick={() =>
                      submitSubReport(projectId, r.id).then(() =>
                        qc.invalidateQueries({
                          queryKey: ["sub-reports", projectId],
                        }),
                      )
                    }
                  >
                    ارسال
                  </Button>
                ) : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Drawer
        isOpen={open}
        onClose={() => setOpen(false)}
        title='گزارش روزانه رشته'
        footer={
          <Button onClick={() => save.mutate()} loading={save.isPending}>
            ذخیره
          </Button>
        }
      >
        <div className='space-y-3 p-4'>
          <JalaliDatePicker
            name='report_date'
            label='تاریخ'
            value={form.report_date}
            onChange={(v) => setForm((f) => ({ ...f, report_date: v }))}
          />
          <input
            className='w-full rounded border px-2 py-1'
            placeholder='کد فرم'
            value={form.form_code}
            onChange={(e) =>
              setForm((f) => ({ ...f, form_code: e.target.value }))
            }
          />
        </div>
      </Drawer>
    </div>
  );
}

export default function ProjectSubReportsPage() {
  const { t, i18n } = useTranslation();
  const { projectId = "" } = useParams();
  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <Breadcrumb items={[{ label: "گزارش‌های رشته‌ای" }]} />
        <PageHeader title={t("pages.subReports.title")} />
        <Content />
      </ProjectProvider>
    </main>
  );
}
