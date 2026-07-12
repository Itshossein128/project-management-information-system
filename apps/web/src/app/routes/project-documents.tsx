import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import { ProjectProvider, usePermission, useProject } from "@/app/contexts/project-context";
import {
  CORR_STATUS_LABELS,
  CORR_TYPE_LABELS,
  fetchCorrespondence,
  fetchDocuments,
  fetchMeetings,
  MEETING_TYPE_LABELS,
} from "@/app/lib/api/documents";
import { formatDisplayDate } from "@/app/lib/jalali-utils";
import { PATHS } from "@/app/routeVars";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/sprint-button";

type Tab = "archive" | "correspondence" | "meetings";

function DocumentsContent() {
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_documents");
  const [tab, setTab] = useState<Tab>("archive");
  const [search, setSearch] = useState("");

  const { data: docs, isLoading: dloading } = useQuery({
    queryKey: ["documents", projectId, search],
    queryFn: () => fetchDocuments(projectId, search ? { search } : {}),
    enabled: canView && tab === "archive",
  });

  const { data: corr, isLoading: cloading } = useQuery({
    queryKey: ["correspondence", projectId],
    queryFn: () => fetchCorrespondence(projectId),
    enabled: canView && tab === "correspondence",
  });

  const { data: meetings, isLoading: mloading } = useQuery({
    queryKey: ["meetings", projectId],
    queryFn: () => fetchMeetings(projectId),
    enabled: canView && tab === "meetings",
  });

  if (isLoading) return <LoadingSkeleton rows={8} />;
  if (!project) return <p>پروژه یافت نشد</p>;
  if (!canView) {
    return <p className="rounded-lg border p-8 text-center text-muted-foreground">دسترسی ندارید.</p>;
  }

  const corrRows = corr?.results ?? [];
  const openCount = corrRows.filter((c) => c.status === "open").length;
  const overdueCount = corrRows.filter(
    (c) => c.status === "open" && c.response_due_date && c.response_due_date < new Date().toISOString().slice(0, 10),
  ).length;

  return (
    <div className="space-y-6">
      <PageHeader title="مدارک و مکاتبات" subtitle={project.project_name} />

      <div className="flex flex-wrap gap-2">
        {([
          ["archive", "آرشیو مدارک"],
          ["correspondence", "مکاتبات"],
          ["meetings", "صورتجلسات"],
        ] as const).map(([id, label]) => (
          <Button key={id} variant={tab === id ? "primary" : "secondary"} onClick={() => setTab(id)}>
            {label}
          </Button>
        ))}
      </div>

      {tab === "archive" && (
        <>
          <input
            className="w-full max-w-md rounded-md border px-3 py-2 text-sm"
            placeholder="جستجو در عنوان، کد، برچسب..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {dloading ? <LoadingSkeleton rows={4} /> : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {(docs?.results ?? []).map((d) => (
                <div key={d.id} className="rounded-lg border p-4">
                  <p className="text-xs text-muted-foreground">{d.doc_code || "—"}</p>
                  <p className="font-medium">{d.title}</p>
                  {d.revision && <span className="mt-1 inline-block rounded bg-muted px-2 py-0.5 text-xs">{d.revision}</span>}
                  <p className="mt-2 text-xs text-muted-foreground">{formatDisplayDate(d.revision_date)}</p>
                  {d.file_url && (
                    <a href={d.file_url} className="mt-2 inline-block text-sm text-primary underline" target="_blank" rel="noreferrer">
                      دانلود
                    </a>
                  )}
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {tab === "correspondence" && (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-lg border p-4"><p className="text-sm text-muted-foreground">باز</p><p className="text-xl font-semibold">{openCount}</p></div>
            <div className="rounded-lg border p-4"><p className="text-sm text-muted-foreground">سررسید گذشته</p><p className="text-xl font-semibold text-red-600">{overdueCount}</p></div>
          </div>
          {cloading ? <LoadingSkeleton rows={6} /> : (
            <div className="overflow-x-auto rounded-lg border">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    {["شماره", "نوع", "موضوع", "از", "به", "موعد پاسخ", "وضعیت"].map((h) => (
                      <th key={h} className="px-3 py-2 text-start">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {corrRows.map((c) => (
                    <tr key={c.id} className="border-t">
                      <td className="px-3 py-2">{c.corr_number}</td>
                      <td className="px-3 py-2">{CORR_TYPE_LABELS[c.corr_type] ?? c.corr_type}</td>
                      <td className="px-3 py-2">{c.subject}</td>
                      <td className="px-3 py-2">{c.from_party}</td>
                      <td className="px-3 py-2">{c.to_party}</td>
                      <td className="px-3 py-2">{formatDisplayDate(c.response_due_date)}</td>
                      <td className="px-3 py-2">{CORR_STATUS_LABELS[c.status] ?? c.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {tab === "meetings" && (
        mloading ? <LoadingSkeleton rows={6} /> : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  {["تاریخ", "نوع", "مکان", "مصوبات"].map((h) => (
                    <th key={h} className="px-3 py-2 text-start">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {(meetings?.results ?? []).map((m) => (
                  <tr key={m.id} className="border-t">
                    <td className="px-3 py-2">{formatDisplayDate(m.meeting_date)}</td>
                    <td className="px-3 py-2">{MEETING_TYPE_LABELS[m.meeting_type] ?? m.meeting_type}</td>
                    <td className="px-3 py-2">{m.location || "—"}</td>
                    <td className="max-w-md truncate px-3 py-2">{m.decisions}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}
    </div>
  );
}

export default function ProjectDocumentsPage() {
  const { projectId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto max-w-7xl px-4 py-8">
        <Breadcrumb items={[{ label: "پروژه‌ها", href: `/${PATHS.PROJECT}` }, { label: "مدارک و مکاتبات" }]} />
        <DocumentsContent />
      </main>
    </ProjectProvider>
  );
}
