import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { PageHeader, Breadcrumb, LoadingSkeleton } from "@/components/layout/page-header";
import { ProjectProvider, useProject } from "~/contexts/project-context";
import { fetchBlocks, fetchBlockStock, issueStock } from "~/lib/api/procurement";
import { PATHS } from "~/routeVars";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { useToast } from "@/components/ui/toast";
import { Drawer } from "@/components/ui/drawer";

function ProcurementInventoryContent() {
  const { projectId, project } = useProject();
  const qc = useQueryClient();
  const toast = useToast();

  const [selectedBlock, setSelectedBlock] = useState("");
  const [issueDrawer, setIssueDrawer] = useState<any>(null);
  const [issueQty, setIssueQty] = useState("");

  const { data: blocks = [] } = useQuery({
    queryKey: ["blocks", projectId],
    queryFn: () => fetchBlocks(projectId),
  });

  const { data: stock = [], isLoading, isError, refetch } = useQuery({
    queryKey: ["blockStock", projectId, selectedBlock],
    queryFn: () => fetchBlockStock(projectId, selectedBlock),
    enabled: !!selectedBlock,
  });

  const issueMut = useMutation({
    mutationFn: (payload: { allocation_id: string; issue_qty: number }) => issueStock(projectId, selectedBlock, payload),
    onSuccess: () => {
      toast.success("حواله انبار با موفقیت صادر شد.");
      setIssueDrawer(null);
      setIssueQty("");
      void qc.invalidateQueries({ queryKey: ["blockStock", projectId, selectedBlock] });
    },
    onError: (e: any) => toast.error(e.message || "خطا در صدور حواله (Hard Stop ممکن است رخ داده باشد)"),
  });

  const handleIssue = () => {
    if (!issueQty || isNaN(Number(issueQty))) return toast.error("مقدار معتبر وارد کنید");
    issueMut.mutate({
      allocation_id: issueDrawer.id,
      issue_qty: Number(issueQty),
    });
  };

  return (
    <div className="space-y-6">
      <PageHeader title="انبارداری بلوکی" subtitle={project?.project_name} />
      
      <div className="bg-card border border-border p-4 rounded-lg">
        <label className="flex flex-col gap-2 text-sm max-w-sm">
          <span className="font-medium">انتخاب بلوک/فاز پروژه</span>
          <select 
            className="rounded-md border px-3 py-2" 
            value={selectedBlock} 
            onChange={(e) => setSelectedBlock(e.target.value)}
          >
            <option value="">برای مشاهده انبار، یک بلوک انتخاب کنید...</option>
            {blocks.map((b: any) => <option key={b.id} value={b.id}>{b.block_code} - {b.block_name}</option>)}
          </select>
        </label>
      </div>

      {selectedBlock && (
        <div className="space-y-4">
          <h3 className="text-lg font-medium">موجودی و تخصیص‌ها</h3>
          
          {isLoading ? (
            <LoadingSkeleton rows={5} />
          ) : isError ? (
            <QueryErrorState onRetry={() => void refetch()} />
          ) : stock.length === 0 ? (
            <div className="p-8 text-center border rounded-lg bg-muted/20">
              هیچ ورودی انباری (GRN) برای این بلوک ثبت نشده است.
            </div>
          ) : (
            <div className="overflow-x-auto rounded-lg border border-border">
              <table className="w-full text-sm text-start">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="px-3 py-2 text-start">شناسه تخصیص (MR Tag)</th>
                    <th className="px-3 py-2 text-start">متریال</th>
                    <th className="px-3 py-2 text-start">تخصیص یافته (MR)</th>
                    <th className="px-3 py-2 text-start">رسید شده (موجود)</th>
                    <th className="px-3 py-2 text-start">حواله شده (مصرفی)</th>
                    <th className="px-3 py-2 text-start">موجودی واقعی (قابل مصرف)</th>
                    <th className="px-3 py-2 text-start">عملیات</th>
                  </tr>
                </thead>
                <tbody>
                  {stock.map((item: any) => (
                    <tr key={item.id} className="border-t border-border">
                      <td className="px-3 py-2 font-mono text-xs">{item.mr_tag}</td>
                      <td className="px-3 py-2 font-medium">{item.material_name}</td>
                      <td className="px-3 py-2">{item.allocated_qty}</td>
                      <td className="px-3 py-2 text-blue-700">{item.received_qty}</td>
                      <td className="px-3 py-2 text-amber-600">{item.issued_qty}</td>
                      <td className="px-3 py-2 text-green-700 font-bold">{item.available_qty}</td>
                      <td className="px-3 py-2">
                        <Button 
                          size="sm" 
                          variant="outline" 
                          disabled={item.available_qty <= 0}
                          onClick={() => setIssueDrawer(item)}
                        >
                          صدور حواله (Issue)
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <Drawer
        isOpen={!!issueDrawer}
        onClose={() => setIssueDrawer(null)}
        title="صدور حواله (مصرف پای کار)"
        footer={
          <Button variant="default" onClick={handleIssue} disabled={issueMut.isPending}>
            ثبت حواله
          </Button>
        }
      >
        {issueDrawer && (
          <div className="space-y-6">
            <div className="bg-amber-50 p-4 rounded-md border border-amber-200 text-amber-900 text-sm">
              <p className="font-semibold mb-2">توجه (قانون Hard Stop):</p>
              <p>مجموع مقدار حواله نمی‌تواند از موجودی واقعی تخصیص این متریال برای کد <strong>{issueDrawer.mr_tag}</strong> بیشتر باشد.</p>
              <p className="mt-2 font-mono">موجودی مجاز: {issueDrawer.available_qty}</p>
            </div>
            
            <label className="flex flex-col gap-1 text-sm">
              <span>مقدار مصرف (Issue Quantity)</span>
              <input 
                type="number" 
                step="any" 
                max={issueDrawer.available_qty}
                className="rounded-md border px-3 py-2" 
                value={issueQty} 
                onChange={(e: any) => setIssueQty(e.target.value)} 
              />
            </label>
          </div>
        )}
      </Drawer>
    </div>
  );
}

export default function ProcurementInventoryPage() {
  const { projectId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto px-4 py-8">
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "تدارکات", href: `/${PATHS.PROJECT}/${projectId}/${PATHS.PROJECT_PROCUREMENT}` },
            { label: "انبارداری بلوکی" },
          ]}
        />
        <ProcurementInventoryContent />
      </main>
    </ProjectProvider>
  );
}
