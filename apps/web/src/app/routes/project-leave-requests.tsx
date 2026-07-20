import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import {
  createLeaveRequest,
  fetchLeaveRequests,
  managerApproveLeave,
  securityApproveLeave,
  submitLeave,
  supervisorApproveLeave,
} from "@/app/lib/api/hr-forms";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { EmptyState } from "@/components/layout/empty-state";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Button } from "@/components/ui/sprint-button";
import { Drawer } from "@/components/ui/drawer";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";

function Content() {
  const { projectId } = useProject();
  const { has } = usePermission(projectId);
  const canApprove = has("approve_reports");
  const toast = useToast();
  const qc = useQueryClient();
  const [tab, setTab] = useState<"mine" | "all">("mine");
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    request_type: "daily",
    leave_date: "",
    department: "",
    mission_subject: "",
  });

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["leave", projectId, tab],
    queryFn: () => fetchLeaveRequests(projectId, tab === "mine"),
  });

  const save = useMutation({
    mutationFn: () => createLeaveRequest(projectId, form),
    onSuccess: () => {
      toast.success("ثبت شد");
      setOpen(false);
      void qc.invalidateQueries({ queryKey: ["leave", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const rows = (data?.results ?? []) as {
    id: string;
    leave_date: string;
    requester_name: string;
    request_type: string;
    department: string;
    status: string;
  }[];

  if (isLoading) return <LoadingSkeleton rows={6} />;
  if (isError) return <QueryErrorState onRetry={() => void refetch()} />;

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
      {rows.length === 0 ? (
        <EmptyState
          title="درخواستی ثبت نشده"
          description="اولین درخواست مرخصی را ثبت کنید."
          action={
            <Button size="sm" onClick={() => setOpen(true)}>
              درخواست جدید
            </Button>
          }
        />
      ) : (
      <table className='w-full text-sm border rounded-lg'>
        <thead className='bg-muted/50'>
          <tr>
            {["تاریخ", "نوع", "نام", "واحد", "وضعیت", ""].map((h) => (
              <th key={h} className='px-3 py-2 text-start'>
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className='border-t'>
              <td className='px-3 py-2'>{r.leave_date}</td>
              <td className='px-3 py-2'>
                <Badge variant='info' label={r.request_type} />
              </td>
              <td className='px-3 py-2'>{r.requester_name}</td>
              <td className='px-3 py-2'>{r.department}</td>
              <td className='px-3 py-2'>
                <Badge
                  variant={r.status === "rejected" ? "danger" : "neutral"}
                  label={r.status}
                />
              </td>
              <td className='px-3 py-2 space-x-1'>
                {r.status === "draft" ? (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() =>
                      submitLeave(projectId, r.id)
                        .then(() => {
                          toast.success("ارسال شد");
                          void qc.invalidateQueries({ queryKey: ["leave", projectId] });
                        })
                        .catch((e: Error) => toast.error(e.message))
                    }
                  >
                    ارسال
                  </Button>
                ) : null}
                {canApprove && r.status === "submitted" ? (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() =>
                      supervisorApproveLeave(projectId, r.id, true)
                        .then(() => {
                          toast.success("تأیید سرپرست");
                          void qc.invalidateQueries({ queryKey: ["leave", projectId] });
                        })
                        .catch((e: Error) => toast.error(e.message))
                    }
                  >
                    تأیید سرپرست
                  </Button>
                ) : null}
                {canApprove && r.status === "supervisor_approved" ? (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() =>
                      managerApproveLeave(projectId, r.id, true)
                        .then(() => {
                          toast.success("تأیید مدیر");
                          void qc.invalidateQueries({ queryKey: ["leave", projectId] });
                        })
                        .catch((e: Error) => toast.error(e.message))
                    }
                  >
                    تأیید مدیر
                  </Button>
                ) : null}
                {canApprove && r.status === "manager_approved" && r.request_type === "mission" ? (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() =>
                      securityApproveLeave(projectId, r.id, true)
                        .then(() => {
                          toast.success("تأیید حراست");
                          void qc.invalidateQueries({ queryKey: ["leave", projectId] });
                        })
                        .catch((e: Error) => toast.error(e.message))
                    }
                  >
                    تأیید حراست
                  </Button>
                ) : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      )}
      <Drawer
        isOpen={open}
        onClose={() => setOpen(false)}
        title='درخواست مرخصی/مأموریت'
        footer={
          <Button onClick={() => save.mutate()} loading={save.isPending}>
            ذخیره
          </Button>
        }
      >
        <div className='space-y-3 p-4'>
          <div className='flex gap-3 text-sm'>
            {(["mission", "hourly", "daily"] as const).map((t) => (
              <label key={t} className='flex items-center gap-1'>
                <input
                  type='radio'
                  checked={form.request_type === t}
                  onChange={() => setForm((f) => ({ ...f, request_type: t }))}
                />
                {t}
              </label>
            ))}
          </div>
          <JalaliDatePicker
            name='leave_date'
            label='تاریخ'
            value={form.leave_date}
            onChange={(v) => setForm((f) => ({ ...f, leave_date: v }))}
          />
          <input
            className='w-full rounded border px-2 py-1'
            placeholder='واحد'
            value={form.department}
            onChange={(e) =>
              setForm((f) => ({ ...f, department: e.target.value }))
            }
          />
          {form.request_type === "mission" ? (
            <textarea
              className='w-full rounded border px-2 py-1'
              placeholder='موضوع مأموریت'
              value={form.mission_subject}
              onChange={(e) =>
                setForm((f) => ({ ...f, mission_subject: e.target.value }))
              }
            />
          ) : null}
        </div>
      </Drawer>
    </div>
  );
}

export default function ProjectLeaveRequestsPage() {
  const { projectId = "" } = useParams();
  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <Breadcrumb items={[{ label: "مرخصی و مأموریت" }]} />
        <PageHeader title='درخواست‌های مرخصی و مأموریت' />
        <Content />
      </ProjectProvider>
    </main>
  );
}
