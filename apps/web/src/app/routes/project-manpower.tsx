import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useParams } from "react-router";
import {
  fetchJobTitles,
  fetchManpower,
  saveManpowerDay,
} from "@/app/lib/api/manpower";
import { ProjectProvider, useProject } from "@/app/contexts/project-context";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { Button } from "@/components/ui/sprint-button";
import { useToast } from "@/components/ui/toast";

type Tab = "indirect" | "direct";

function Content() {
  const { projectId } = useProject();
  const toast = useToast();
  const qc = useQueryClient();
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [tab, setTab] = useState<Tab>("indirect");
  const [counts, setCounts] = useState<
    Record<string, { s1: number; s2: number; s3: number }>
  >({});

  const { data: titles, isLoading: titlesLoading } = useQuery({
    queryKey: ["job-titles", projectId],
    queryFn: () => fetchJobTitles(projectId),
  });

  const { data: saved = [], isLoading } = useQuery({
    queryKey: ["manpower", projectId, date],
    queryFn: () => fetchManpower(projectId, date),
  });

  const jobTitles =
    tab === "indirect" ? (titles?.indirect ?? []) : (titles?.direct ?? []);

  const rows = useMemo(() => {
    return jobTitles.map((t) => {
      const existing = saved.find(
        (r) => r.job_title === t.title && r.labor_category === tab,
      );
      const local = counts[`${tab}:${t.title}`];
      return {
        title: t.title,
        s1: local?.s1 ?? existing?.shift_1_count ?? 0,
        s2: local?.s2 ?? existing?.shift_2_count ?? 0,
        s3: local?.s3 ?? existing?.shift_3_count ?? 0,
      };
    });
  }, [jobTitles, saved, counts, tab]);

  const save = useMutation({
    mutationFn: () =>
      saveManpowerDay(
        projectId,
        rows.map((r) => ({
          report_date: date,
          labor_category: tab,
          job_title: r.title,
          shift_1_count: r.s1,
          shift_2_count: r.s2,
          shift_3_count: r.s3,
        })),
      ),
    onSuccess: (res) => {
      const n = (res as { count?: number }).count ?? rows.length;
      toast.success(`${n} ردیف ذخیره شد`);
      void qc.invalidateQueries({ queryKey: ["manpower", projectId, date] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (titlesLoading || isLoading) return <LoadingSkeleton rows={8} />;

  return (
    <div className='space-y-4'>
      <JalaliDatePicker
        name='manpower_date'
        label='تاریخ'
        value={date}
        onChange={setDate}
      />
      <div className='flex gap-2'>
        <Button
          variant={tab === "indirect" ? "primary" : "secondary"}
          size='sm'
          onClick={() => setTab("indirect")}
        >
          نیروی غیرمستقیم
        </Button>
        <Button
          variant={tab === "direct" ? "primary" : "secondary"}
          size='sm'
          onClick={() => setTab("direct")}
        >
          نیروی مستقیم
        </Button>
      </div>
      <table className='w-full text-sm border rounded-lg overflow-hidden'>
        <thead className='bg-muted/50'>
          <tr>
            {["عنوان", "شیفت ۱", "شیفت ۲", "شیفت ۳", "جمع"].map((h) => (
              <th key={h} className='px-3 py-2 text-start'>
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.title} className='border-t'>
              <td className='px-3 py-2'>{r.title}</td>
              {(["s1", "s2", "s3"] as const).map((k, idx) => (
                <td key={k} className='px-3 py-2'>
                  <input
                    type='number'
                    className='w-20 rounded border px-2 py-1'
                    value={r[k]}
                    onChange={(e) =>
                      setCounts((prev) => ({
                        ...prev,
                        [`${tab}:${r.title}`]: {
                          s1: idx === 0 ? Number(e.target.value) : r.s1,
                          s2: idx === 1 ? Number(e.target.value) : r.s2,
                          s3: idx === 2 ? Number(e.target.value) : r.s3,
                        },
                      }))
                    }
                  />
                </td>
              ))}
              <td className='px-3 py-2 font-medium'>{r.s1 + r.s2 + r.s3}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <Button
        variant='primary'
        onClick={() => save.mutate()}
        loading={save.isPending}
      >
        ذخیره روز
      </Button>
    </div>
  );
}

export default function ProjectManpowerPage() {
  const { projectId = "" } = useParams();
  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <Breadcrumb items={[{ label: "نیروی انسانی" }]} />
        <PageHeader title='نیروی انسانی روزانه' />
        <Content />
      </ProjectProvider>
    </main>
  );
}
