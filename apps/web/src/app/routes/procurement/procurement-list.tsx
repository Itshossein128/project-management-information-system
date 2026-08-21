import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { PageHeader, Breadcrumb, LoadingSkeleton } from "@/components/layout/page-header";
import { ProjectProvider, useProject } from "~/contexts/project-context";
import { usePermission } from "~/contexts/project-context";
import { fetchRequisitions, fetchBlocks } from "~/lib/api/procurement";
import { PATHS } from "~/routeVars";
import { QueryErrorState } from "@/components/layout/query-error-state";

function ProcurementListContent() {
  const { t } = useTranslation();
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_procurement");
  const canCreate = has("edit_reports"); // Just mapping permissions as existing ones

  const [statusFilter, setStatusFilter] = useState("");
  const [blockFilter, setBlockFilter] = useState("");

  const { data: requisitions = [], isLoading: loadingReqs, isError, refetch } = useQuery({
    queryKey: ["procurement", projectId, statusFilter, blockFilter],
    queryFn: () => fetchRequisitions(projectId, { 
        ...(statusFilter && { status: statusFilter }),
        ...(blockFilter && { block: blockFilter })
    }),
    enabled: canView,
  });

  const { data: blocks = [] } = useQuery({
    queryKey: ["blocks", projectId],
    queryFn: () => fetchBlocks(projectId),
    enabled: canView,
  });

  if (isLoading) return <LoadingSkeleton rows={10} />;
  if (!project) return <p>پروژه یافت نشد</p>;
  if (!canView) return <p className="p-8 text-center">{t("common.accessDenied")}</p>;

  return (
    <div className="space-y-6">
      <PageHeader title="تدارکات و لجستیک (درخواست‌های خرید)" subtitle={project.project_name} />
      
      <div className="flex flex-wrap items-end gap-3">
        <label className="flex flex-col gap-1 text-sm">
          <span>وضعیت</span>
          <select className="rounded-md border px-3 py-2" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">همه</option>
            <option value="draft">پیش‌نویس</option>
            <option value="technical_review">بررسی فنی</option>
            <option value="workshop_approval">تایید کارگاه</option>
            <option value="control_check">کنترل پروژه</option>
            <option value="pm_approval">تایید مدیر پروژه</option>
            <option value="procurement_queue">صف تدارکات</option>
            <option value="hq_control_approval">تایید دفتر مرکزی</option>
            <option value="final_approval">تایید نهایی</option>
            <option value="approved">تایید شده</option>
            <option value="rejected">رد شده</option>
          </select>
        </label>

        <label className="flex flex-col gap-1 text-sm">
          <span>بلوک/فاز</span>
          <select className="rounded-md border px-3 py-2" value={blockFilter} onChange={(e) => setBlockFilter(e.target.value)}>
            <option value="">همه</option>
            {blocks.map((b) => (
              <option key={b.id} value={b.id}>{b.block_code} - {b.block_name}</option>
            ))}
          </select>
        </label>

        {canCreate && (
          <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT_NEW}`}>
            <Button variant="default">درخواست جدید</Button>
          </Link>
        )}
        
        <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT_OFFICER}`}>
          <Button variant="outline">کارتابل کارپرداز</Button>
        </Link>
        <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT_INVENTORY}`}>
          <Button variant="outline">انبار بلوک‌ها</Button>
        </Link>
        <Link to={`/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT_REPORTS}`}>
          <Button variant="outline">گزارشات داشبورد</Button>
        </Link>
      </div>

      {loadingReqs ? (
        <LoadingSkeleton rows={8} />
      ) : isError ? (
        <QueryErrorState onRetry={() => void refetch()} />
      ) : requisitions.length === 0 ? (
        <p className="text-center text-muted-foreground p-8">هیچ درخواستی یافت نشد.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm text-start">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-3 py-2 text-start">شماره درخواست</th>
                <th className="px-3 py-2 text-start">بلوک</th>
                <th className="px-3 py-2 text-start">نوع درخواست</th>
                <th className="px-3 py-2 text-start">تاریخ درخواست</th>
                <th className="px-3 py-2 text-start">تعداد آیتم</th>
                <th className="px-3 py-2 text-start">وضعیت</th>
                <th className="px-3 py-2 text-start">عملیات</th>
              </tr>
            </thead>
            <tbody>
              {requisitions.map((req) => (
                <tr key={req.id} className="border-t border-border">
                  <td className="px-3 py-2 font-medium">{req.requisition_number}</td>
                  <td className="px-3 py-2">{req.block_code}</td>
                  <td className="px-3 py-2">{req.requisition_type_display}</td>
                  <td className="px-3 py-2">{req.request_date}</td>
                  <td className="px-3 py-2">{(req as any).item_count || 0}</td>
                  <td className="px-3 py-2">
                    <span className="rounded-full bg-blue-100 px-2 py-1 text-xs text-blue-800">
                      {req.status_display}
                    </span>
                  </td>
                  <td className="px-3 py-2">
                    <Link to={`/${PATHS.PROJECT}/${projectId}/procurement/req/${req.id}`}>
                      <Button size="sm" variant="outline">مشاهده و بررسی</Button>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default function ProcurementListPage() {
  const { projectId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto px-4 py-8">
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "تدارکات و لجستیک" },
          ]}
        />
        <ProcurementListContent />
      </main>
    </ProjectProvider>
  );
}
