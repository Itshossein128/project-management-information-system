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
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import {
  SpecialtyContributionForm,
  type SpecialtyContributionPayload,
} from "@/components/sub_reports/SpecialtyContributionForm";

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

  const { data, isLoading } = useQuery({
    queryKey: ["sub-reports", projectId, discipline],
    queryFn: () => fetchSubReports(projectId, discipline),
  });

  const invalidateRelated = () => {
    void qc.invalidateQueries({ queryKey: ["sub-reports", projectId] });
    void qc.invalidateQueries({ queryKey: ["daily-reports", projectId] });
    void qc.invalidateQueries({ queryKey: ["daily-report", projectId] });
  };

  const save = useMutation({
    mutationFn: (payload: SpecialtyContributionPayload) =>
      createSubReport(projectId, {
        ...payload,
        discipline,
      }),
    onSuccess: () => {
      toast.success(
        t(
          "dailyReports.summary.specialtySavedToast",
          "ثبت شد — جمع‌بندی گزارش روزانه پروژه به‌روزرسانی می‌شود",
        ),
      );
      setOpen(false);
      invalidateRelated();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const submit = useMutation({
    mutationFn: (id: string) => submitSubReport(projectId, id),
    onSuccess: () => {
      toast.success(
        t(
          "dailyReports.summary.specialtySubmittedToast",
          "ارسال شد — جمع‌بندی گزارش روزانه پروژه به‌روزرسانی می‌شود",
        ),
      );
      invalidateRelated();
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
        <Button
          className='ms-auto'
          size='sm'
          data-testid='sub-report-new-btn'
          onClick={() => setOpen(true)}
        >
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
                    loading={submit.isPending}
                    onClick={() => submit.mutate(r.id)}
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
        footer={null}
      >
        <SpecialtyContributionForm
          loading={save.isPending}
          onSubmit={(payload) => save.mutate(payload)}
        />
      </Drawer>
    </div>
  );
}

export default function ProjectSubReportsPage() {
  const { t } = useTranslation();
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
