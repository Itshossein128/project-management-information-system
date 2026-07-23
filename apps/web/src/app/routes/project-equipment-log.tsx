import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import {
  createEquipmentLog,
  deleteEquipmentLog,
  fetchEquipmentLogs,
  fetchEquipmentSummary,
} from "@/app/lib/api/equipment-log";
import { ProjectProvider, useProject } from "@/app/contexts/project-context";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { Button } from "@/components/ui/sprint-button";
import { Drawer } from "@/components/ui/drawer";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { useToast } from "@/components/ui/toast";
import { Badge } from "@/components/ui/badge";

function Content() {
  const { projectId } = useProject();
  const toast = useToast();
  const qc = useQueryClient();
  const [mode, setMode] = useState<"detail" | "summary">("detail");
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    log_date: "",
    equipment_name: "",
    shift: "day",
    status: "active",
    ownership_type: "owned",
    work_start: "",
    work_end: "",
    repair_hours: "0",
    productive_hours: "0",
  });

  const { data: detailData, isLoading: detailLoading } = useQuery({
    queryKey: ["equipment-log-detail", projectId],
    queryFn: () => fetchEquipmentLogs(projectId),
    enabled: mode === "detail",
  });
  const { data: summaryData, isLoading: summaryLoading } = useQuery({
    queryKey: ["equipment-log-summary", projectId],
    queryFn: () => fetchEquipmentSummary(projectId),
    enabled: mode === "summary",
  });

  const isLoading = mode === "detail" ? detailLoading : summaryLoading;

  const save = useMutation({
    mutationFn: () => createEquipmentLog(projectId, form),
    onSuccess: () => {
      toast.success("ثبت شد");
      setOpen(false);
      void qc.invalidateQueries({ queryKey: ["equipment-log", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (isLoading) return <LoadingSkeleton rows={6} />;
  const detailRows = detailData?.results ?? [];
  const summaryRows = summaryData ?? [];

  return (
    <div className='space-y-4'>
      <div className='flex gap-2'>
        <Button
          variant={mode === "detail" ? "primary" : "secondary"}
          size='sm'
          onClick={() => setMode("detail")}
        >
          تفصیلی
        </Button>
        <Button
          variant={mode === "summary" ? "primary" : "secondary"}
          size='sm'
          onClick={() => setMode("summary")}
        >
          خلاصه
        </Button>
        <Button
          variant='primary'
          size='sm'
          className='ms-auto'
          onClick={() => setOpen(true)}
        >
          افزودن
        </Button>
      </div>
      {mode === "detail" ? (
        <table className='w-full text-sm border rounded-lg overflow-hidden'>
          <thead className='bg-muted/50'>
            <tr>
              {[
                "تاریخ",
                "دستگاه",
                "شیفت",
                "وضعیت",
                "مالکیت",
                "کارکرد مفید",
                "",
              ].map((h) => (
                <th key={h} className='px-3 py-2 text-start'>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {detailRows.map((r) => (
              <tr key={r.id} className='border-t'>
                <td className='px-3 py-2'>{r.log_date}</td>
                <td className='px-3 py-2'>{r.equipment_name}</td>
                <td className='px-3 py-2'>{r.shift}</td>
                <td className='px-3 py-2'>
                  <Badge
                    variant={
                      r.status === "active"
                        ? "success"
                        : r.status === "standby"
                          ? "warning"
                          : "danger"
                    }
                    label={r.status}
                  />
                </td>
                <td className='px-3 py-2'>{r.ownership_type}</td>
                <td
                  className={`px-3 py-2 ${r.warning ? "text-warning-600" : ""}`}
                >
                  {r.productive_hours ?? "—"}
                </td>
                <td className='px-3 py-2'>
                  <Button
                    variant='ghost'
                    size='sm'
                    onClick={() =>
                      deleteEquipmentLog(projectId, r.id).then(() =>
                        qc.invalidateQueries({ queryKey: ["equipment-log"] }),
                      )
                    }
                  >
                    حذف
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <table className='w-full text-sm border rounded-lg overflow-hidden'>
          <thead className='bg-muted/50'>
            <tr>
              {["تاریخ", "دستگاه", "کل", "فعال", "آماده", "خراب"].map((h) => (
                <th key={h} className='px-3 py-2 text-start'>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {summaryRows.map((r, i) => (
              <tr key={i} className='border-t'>
                <td className='px-3 py-2'>{r.date}</td>
                <td className='px-3 py-2'>{r.equipment_name}</td>
                <td className='px-3 py-2'>{r.total_units}</td>
                <td className='px-3 py-2'>{r.active}</td>
                <td className='px-3 py-2'>{r.standby}</td>
                <td className='px-3 py-2'>{r.broken}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <Drawer
        isOpen={open}
        onClose={() => setOpen(false)}
        title='ثبت تجهیزات'
        footer={
          <Button onClick={() => save.mutate()} loading={save.isPending}>
            ذخیره
          </Button>
        }
      >
        <div className='space-y-3 p-4 text-sm'>
          <JalaliDatePicker
            name='log_date'
            label='تاریخ'
            value={form.log_date}
            onChange={(v) => setForm((f) => ({ ...f, log_date: v }))}
          />
          <input
            className='w-full rounded border px-2 py-1'
            placeholder='عنوان دستگاه'
            value={form.equipment_name}
            onChange={(e) =>
              setForm((f) => ({ ...f, equipment_name: e.target.value }))
            }
          />
          <input
            type='number'
            className='w-full rounded border px-2 py-1'
            placeholder='کارکرد مفید'
            value={form.productive_hours}
            onChange={(e) =>
              setForm((f) => ({ ...f, productive_hours: e.target.value }))
            }
          />
        </div>
      </Drawer>
    </div>
  );
}

export default function ProjectEquipmentLogPage() {
  const { projectId = "" } = useParams();
  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <Breadcrumb items={[{ label: "ماشین‌آلات" }]} />
        <PageHeader title='ماشین‌آلات و تجهیزات' />
        <Content />
      </ProjectProvider>
    </main>
  );
}
