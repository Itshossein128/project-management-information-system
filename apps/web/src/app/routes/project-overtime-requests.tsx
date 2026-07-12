import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import {
  createOvertimeRequest,
  fetchOvertimeRequests,
  submitOvertime,
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

function Content() {
  const { projectId } = useProject();
  const toast = useToast();
  const qc = useQueryClient();
  const [tab, setTab] = useState<"mine" | "all">("mine");
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    overtime_date: "",
    department: "",
    requested_hours: 1,
    reason: "درخواست اضافه‌کاری پروژه",
  });

  const { data, isLoading } = useQuery({
    queryKey: ["overtime", projectId, tab],
    queryFn: () => fetchOvertimeRequests(projectId, tab === "mine"),
  });

  const save = useMutation({
    mutationFn: () => createOvertimeRequest(projectId, form),
    onSuccess: () => {
      toast.success("ثبت شد");
      setOpen(false);
      void qc.invalidateQueries({ queryKey: ["overtime", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const rows = (data?.results ?? []) as {
    id: string;
    overtime_date: string;
    requester_name: string;
    department: string;
    requested_hours: string;
    approved_hours: string | null;
    status: string;
  }[];

  if (isLoading) return <LoadingSkeleton rows={6} />;

  return (
    <div className='space-y-4'>
      <div className='flex gap-2'>
        <Button
          variant={tab === "mine" ? "primary" : "secondary"}
          size='sm'
          onClick={() => setTab("mine")}
        >
          درخواست‌های من
        </Button>
        <Button
          variant={tab === "all" ? "primary" : "secondary"}
          size='sm'
          onClick={() => setTab("all")}
        >
          همه درخواست‌ها
        </Button>
        <Button className='ms-auto' size='sm' onClick={() => setOpen(true)}>
          درخواست جدید
        </Button>
      </div>
      <table className='w-full text-sm border rounded-lg'>
        <thead className='bg-muted/50'>
          <tr>
            {["تاریخ", "نام", "واحد", "درخواستی", "تأییدشده", "وضعیت", ""].map(
              (h) => (
                <th key={h} className='px-3 py-2 text-start'>
                  {h}
                </th>
              ),
            )}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className='border-t'>
              <td className='px-3 py-2'>{r.overtime_date}</td>
              <td className='px-3 py-2'>{r.requester_name}</td>
              <td className='px-3 py-2'>{r.department}</td>
              <td className='px-3 py-2'>{r.requested_hours}</td>
              <td className='px-3 py-2'>{r.approved_hours ?? "—"}</td>
              <td className='px-3 py-2'>
                <Badge
                  variant={
                    r.status === "rejected"
                      ? "danger"
                      : r.status === "manager_approved"
                        ? "success"
                        : "info"
                  }
                  label={r.status}
                />
              </td>
              <td className='px-3 py-2'>
                {r.status === "draft" ? (
                  <Button
                    size='sm'
                    variant='ghost'
                    onClick={() =>
                      submitOvertime(projectId, r.id).then(() =>
                        qc.invalidateQueries({
                          queryKey: ["overtime", projectId],
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
        title='درخواست اضافه‌کاری'
        footer={
          <Button onClick={() => save.mutate()} loading={save.isPending}>
            ذخیره
          </Button>
        }
      >
        <div className='space-y-3 p-4'>
          <JalaliDatePicker
            name='overtime_date'
            label='تاریخ اضافه‌کاری'
            value={form.overtime_date}
            onChange={(v) => setForm((f) => ({ ...f, overtime_date: v }))}
          />
          <input
            className='w-full rounded border px-2 py-1'
            placeholder='واحد'
            value={form.department}
            onChange={(e) =>
              setForm((f) => ({ ...f, department: e.target.value }))
            }
          />
          <input
            type='number'
            className='w-full rounded border px-2 py-1'
            placeholder='ساعات'
            value={form.requested_hours}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                requested_hours: Number(e.target.value),
              }))
            }
          />
          <textarea
            className='w-full rounded border px-2 py-1'
            value={form.reason}
            onChange={(e) => setForm((f) => ({ ...f, reason: e.target.value }))}
          />
        </div>
      </Drawer>
    </div>
  );
}

export default function ProjectOvertimePage() {
  const { projectId = "" } = useParams();
  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <Breadcrumb items={[{ label: "اضافه‌کاری" }]} />
        <PageHeader title='درخواست‌های اضافه‌کاری' />
        <Content />
      </ProjectProvider>
    </main>
  );
}
