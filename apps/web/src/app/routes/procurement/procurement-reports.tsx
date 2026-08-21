import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import { PageHeader, Breadcrumb, LoadingSkeleton } from "@/components/layout/page-header";
import { ProjectProvider, useProject } from "~/contexts/project-context";
import { fetchLiquidityReport, fetchMaterialDeviationReport, fetchAuditTrailReport } from "~/lib/api/procurement";
import { PATHS } from "~/routeVars";
import { QueryErrorState } from "@/components/layout/query-error-state";

function ReportsDashboardContent() {
  const { projectId, project } = useProject();
  const [activeTab, setActiveTab] = useState("liquidity");

  const { data: liquidity, isLoading: loadL } = useQuery({
    queryKey: ["reportLiquidity", projectId],
    queryFn: () => fetchLiquidityReport(projectId),
    enabled: activeTab === "liquidity"
  });

  const { data: deviation, isLoading: loadD } = useQuery({
    queryKey: ["reportDeviation", projectId],
    queryFn: () => fetchMaterialDeviationReport(projectId),
    enabled: activeTab === "deviation"
  });

  const { data: audit, isLoading: loadA } = useQuery({
    queryKey: ["reportAudit", projectId],
    queryFn: () => fetchAuditTrailReport(projectId),
    enabled: activeTab === "audit"
  });

  if (!project) return null;

  return (
    <div className="space-y-6">
      <PageHeader title="گزارشات و داشبورد تدارکات" subtitle={project.project_name} />
      
      <div className="flex border-b border-border">
        {[
          { id: "liquidity", label: "داشبورد نقدینگی و بودجه بلوک‌ها" },
          { id: "deviation", label: "گزارش انحراف مصالح" },
          { id: "audit", label: "دفترچه حسابرسی (Audit Trail)" },
        ].map((tab: any) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab.id 
                ? "border-primary text-primary" 
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="pt-4">
        {activeTab === "liquidity" && (
          <div className="space-y-4">
            {loadL ? <LoadingSkeleton rows={5} /> : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {liquidity?.liquidity_status?.map((b: any) => (
                  <div key={b.block_code} className="p-4 border border-border rounded-lg bg-card">
                    <h4 className="font-semibold mb-2">{b.block_name} ({b.block_code})</h4>
                    <div className="space-y-1 text-sm">
                      <p className="flex justify-between"><span>بودجه کل:</span> <span>{b.budget}</span></p>
                      <p className="flex justify-between"><span>هزینه درخواستی (برآورد):</span> <span>{b.total_requested_value}</span></p>
                      <p className="flex justify-between font-medium">
                        <span>مانده نقدینگی:</span> 
                        <span className={b.remaining_liquidity < 0 ? "text-red-600" : "text-green-600"}>
                          {b.remaining_liquidity}
                        </span>
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "deviation" && (
          <div className="space-y-4">
            {loadD ? <LoadingSkeleton rows={5} /> : (
              <div className="overflow-x-auto border border-border rounded-lg">
                <table className="w-full text-sm text-start">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="px-3 py-2 text-start">بلوک</th>
                      <th className="px-3 py-2 text-start">متریال</th>
                      <th className="px-3 py-2 text-start">مقدار برآوردی (بودجه)</th>
                      <th className="px-3 py-2 text-start">مقدار درخواستی</th>
                      <th className="px-3 py-2 text-start">انحراف</th>
                      <th className="px-3 py-2 text-start">وضعیت انحراف</th>
                    </tr>
                  </thead>
                  <tbody>
                    {deviation?.deviation_data?.map((d: any, idx: number) => (
                      <tr key={idx} className="border-t border-border">
                        <td className="px-3 py-2">{d.block_code}</td>
                        <td className="px-3 py-2">{d.material_name}</td>
                        <td className="px-3 py-2">{d.estimated_qty || '-'}</td>
                        <td className="px-3 py-2">{d.requested_qty}</td>
                        <td className="px-3 py-2" dir="ltr">{d.deviation_qty}</td>
                        <td className="px-3 py-2">
                          <span className={`px-2 py-1 rounded text-xs ${
                            d.deviation_percent > 0 ? "bg-red-100 text-red-800" : "bg-green-100 text-green-800"
                          }`}>
                            {d.deviation_percent > 0 ? '+' : ''}{d.deviation_percent.toFixed(1)}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === "audit" && (
          <div className="space-y-4">
            {loadA ? <LoadingSkeleton rows={5} /> : (
              <div className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                  <div className="p-4 border border-border rounded-lg bg-card">
                    <p className="text-sm text-muted-foreground">کل لاگ‌ها</p>
                    <p className="text-2xl font-bold">{audit?.summary?.total_actions || 0}</p>
                  </div>
                  <div className="p-4 border border-border rounded-lg bg-card">
                    <p className="text-sm text-muted-foreground">تایید شده</p>
                    <p className="text-2xl font-bold text-green-600">{audit?.summary?.approved_actions || 0}</p>
                  </div>
                  <div className="p-4 border border-border rounded-lg bg-card">
                    <p className="text-sm text-muted-foreground">رد شده</p>
                    <p className="text-2xl font-bold text-red-600">{audit?.summary?.rejected_actions || 0}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ProcurementReportsPage() {
  const { projectId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto px-4 py-8">
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "تدارکات", href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT}` },
            { label: "داشبورد گزارشات" },
          ]}
        />
        <ReportsDashboardContent />
      </main>
    </ProjectProvider>
  );
}
