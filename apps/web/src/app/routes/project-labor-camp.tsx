import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import {
  createLaborCampBatch,
  deleteLaborCamp,
  fetchLaborCampGroups,
} from "@/app/lib/api/labor-camp";
import { ProjectProvider, useProject } from "@/app/contexts/project-context";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { Button } from "@/components/ui/sprint-button";
import { Drawer } from "@/components/ui/drawer";
import { useToast } from "@/components/ui/toast";
import { PATHS } from "@/app/routeVars";
import { cn } from "@/app/lib/utils";

function Content() {
  const { projectId } = useProject();
  const toast = useToast();
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [date, setDate] = useState("");
  const [rows, setRows] = useState([
    {
      connex_number: "",
      subcontractor_name: "",
      total_residents: 0,
      present_count: 0,
      on_leave_count: 0,
      capacity: 0,
    },
  ]);

  const { data = [], isLoading } = useQuery({
    queryKey: ["labor-camp", projectId],
    queryFn: () => fetchLaborCampGroups(projectId),
  });

  const save = useMutation({
    mutationFn: () =>
      createLaborCampBatch(
        projectId,
        rows.map((r) => ({ ...r, report_date: date })),
      ),
    onSuccess: () => {
      toast.success("گزارش کمپ ذخیره شد");
      setOpen(false);
      void qc.invalidateQueries({ queryKey: ["labor-camp", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (isLoading) return <LoadingSkeleton rows={6} />;

  return (
    <div className='space-y-4'>
      <div className='flex justify-end'>
        <Button variant='primary' size='sm' onClick={() => setOpen(true)}>
          افزودن گزارش کمپ
        </Button>
      </div>
      {data.length === 0 ? (
        <p className='py-12 text-center text-muted-foreground'>
          گزارشی ثبت نشده است
        </p>
      ) : (
        data.map((group) => (
          <div key={group.date} className='rounded-lg border border-border'>
            <div className='border-b bg-muted/40 px-4 py-2 text-sm font-medium'>
              {`تاریخ: ${group.date} | جمع: ${group.totals.total_residents} نفر مستقر`}
            </div>
            <table className='w-full text-sm'>
              <thead>
                <tr className='bg-muted/30'>
                  {[
                    "شماره کانکس",
                    "پیمانکار",
                    "مستقر",
                    "حاضر",
                    "مرخصی",
                    "ظرفیت",
                    "خالی",
                    "",
                  ].map((h) => (
                    <th key={h} className='px-3 py-2 text-start'>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {group.records.map((r) => (
                  <tr key={r.id} className='border-t'>
                    <td className='px-3 py-2'>{r.connex_number}</td>
                    <td className='px-3 py-2'>{r.subcontractor_name}</td>
                    <td className='px-3 py-2'>{r.total_residents}</td>
                    <td className='px-3 py-2'>{r.present_count}</td>
                    <td className='px-3 py-2'>{r.on_leave_count}</td>
                    <td className='px-3 py-2'>{r.capacity}</td>
                    <td
                      className={cn(
                        "px-3 py-2 font-medium",
                        r.empty_capacity < 0
                          ? "text-red-600"
                          : r.empty_capacity === 0
                            ? "text-amber-600"
                            : "text-emerald-600",
                      )}
                    >
                      {r.empty_capacity}
                    </td>
                    <td className='px-3 py-2'>
                      <Button
                        variant='ghost'
                        size='sm'
                        onClick={() =>
                          deleteLaborCamp(projectId, r.id).then(() =>
                            qc.invalidateQueries({
                              queryKey: ["labor-camp", projectId],
                            }),
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
          </div>
        ))
      )}
      <Drawer
        isOpen={open}
        onClose={() => setOpen(false)}
        title='افزودن گزارش کمپ'
        footer={
          <Button onClick={() => save.mutate()} loading={save.isPending}>
            ذخیره همه
          </Button>
        }
      >
        <div className='space-y-3 p-4'>
          <JalaliDatePicker
            name='camp_date'
            label='تاریخ'
            value={date}
            onChange={setDate}
          />
          {rows.map((row, i) => (
            <div
              key={i}
              className='grid grid-cols-2 gap-2 rounded border p-2 text-sm'
            >
              {(["connex_number", "subcontractor_name"] as const).map((k) => (
                <input
                  key={k}
                  className='rounded border px-2 py-1'
                  placeholder={k}
                  value={row[k]}
                  onChange={(e) =>
                    setRows((prev) =>
                      prev.map((r, idx) =>
                        idx === i ? { ...r, [k]: e.target.value } : r,
                      ),
                    )
                  }
                />
              ))}
              {(
                [
                  "total_residents",
                  "present_count",
                  "on_leave_count",
                  "capacity",
                ] as const
              ).map((k) => (
                <input
                  key={k}
                  type='number'
                  className='rounded border px-2 py-1'
                  placeholder={k}
                  value={row[k]}
                  onChange={(e) =>
                    setRows((prev) =>
                      prev.map((r, idx) =>
                        idx === i ? { ...r, [k]: Number(e.target.value) } : r,
                      ),
                    )
                  }
                />
              ))}
            </div>
          ))}
          <Button
            variant='secondary'
            size='sm'
            onClick={() =>
              setRows((r) => [
                ...r,
                {
                  connex_number: "",
                  subcontractor_name: "",
                  total_residents: 0,
                  present_count: 0,
                  on_leave_count: 0,
                  capacity: 0,
                },
              ])
            }
          >
            افزودن کانکس
          </Button>
        </div>
      </Drawer>
    </div>
  );
}

export default function ProjectLaborCampPage() {
  const { projectId = "" } = useParams();
  return (
    <main className='page-main page-shell mx-auto  px-4 py-8'>
      <ProjectProvider projectId={projectId}>
        <Breadcrumb items={[{ label: "گزارش کمپ" }]} />
        <PageHeader title='گزارش نفرات کمپ' />
        <Content />
      </ProjectProvider>
    </main>
  );
}
