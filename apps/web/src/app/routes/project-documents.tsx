import { useQuery } from "@tanstack/react-query";
import { FolderOpen, Mail, Users } from "lucide-react";
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
import { Field, Input } from "@/components/form";
import { EmptyState } from "@/components/layout/empty-state";
import { Breadcrumb, LoadingSkeleton, PageHeader } from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Button } from "@/components/ui/sprint-button";
import { Tabs, TabsContent as ShadcnTabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

type Tab = "archive" | "correspondence" | "meetings";

function DocumentsContent() {
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canView = has("view_documents");
  const [tab, setTab] = useState<Tab>("archive");
  const [search, setSearch] = useState("");

  const {
    data: docs,
    isLoading: dloading,
    isError: dError,
    refetch: refetchDocs,
  } = useQuery({
    queryKey: ["documents", projectId, search],
    queryFn: () => fetchDocuments(projectId, search ? { search } : {}),
    enabled: canView && tab === "archive",
  });

  const {
    data: corr,
    isLoading: cloading,
    isError: cError,
    refetch: refetchCorr,
  } = useQuery({
    queryKey: ["correspondence", projectId],
    queryFn: () => fetchCorrespondence(projectId),
    enabled: canView && tab === "correspondence",
  });

  const {
    data: meetings,
    isLoading: mloading,
    isError: mError,
    refetch: refetchMeetings,
  } = useQuery({
    queryKey: ["meetings", projectId],
    queryFn: () => fetchMeetings(projectId),
    enabled: canView && tab === "meetings",
  });

  if (isLoading) return <LoadingSkeleton rows={8} />;
  if (!project) {
    return <EmptyState title="پروژه یافت نشد" />;
  }
  if (!canView) {
    return (
      <EmptyState
        title="دسترسی ندارید"
        description="برای مشاهده مدارک و مکاتبات به مجوز مربوطه نیاز است."
      />
    );
  }

  const docRows = docs?.results ?? [];
  const corrRows = corr?.results ?? [];
  const meetingRows = meetings?.results ?? [];
  const openCount = corrRows.filter((c) => c.status === "open").length;
  const overdueCount = corrRows.filter(
    (c) =>
      c.status === "open" &&
      c.response_due_date &&
      c.response_due_date < new Date().toISOString().slice(0, 10),
  ).length;

  const tabs = [
    ["archive", "آرشیو مدارک"],
    ["correspondence", "مکاتبات"],
    ["meetings", "صورتجلسات"],
  ] as const;

  return (
    <div className="space-y-6">
      <PageHeader title="مدارک و مکاتبات" subtitle={project.project_name} />

      <Tabs value={tab} onValueChange={(v) => setTab(v as Tab)} className="w-full" dir="rtl">
        <TabsList className="mb-4">
          {tabs.map(([id, label]) => (
            <TabsTrigger key={id} value={id}>
              {label}
            </TabsTrigger>
          ))}
        </TabsList>

        <ShadcnTabsContent value="archive" className="space-y-4 mt-0">
          <Field name="doc_search" label="جستجو" htmlFor="doc-search">
            {() => (
              <Input
                id="doc-search"
                className="max-w-md"
                placeholder="جستجو در عنوان، کد، برچسب..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            )}
          </Field>
          {dloading ? (
            <LoadingSkeleton rows={4} />
          ) : dError ? (
            <QueryErrorState onRetry={() => void refetchDocs()} />
          ) : docRows.length === 0 ? (
            <EmptyState
              icon={<FolderOpen />}
              title="مدرکی ثبت نشده"
              description={
                search
                  ? "نتیجه‌ای برای این جستجو یافت نشد."
                  : "مدارک پروژه پس از بارگذاری اینجا نمایش داده می‌شوند."
              }
            />
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {docRows.map((d) => (
                <div key={d.id} className="rounded-lg border p-4">
                  <p className="text-xs text-muted-foreground">{d.doc_code || "—"}</p>
                  <p className="font-medium">{d.title}</p>
                  {d.revision ? (
                    <span className="mt-1 inline-block rounded bg-muted px-2 py-0.5 text-xs">
                      {d.revision}
                    </span>
                  ) : null}
                  <p className="mt-2 text-xs text-muted-foreground">
                    {formatDisplayDate(d.revision_date)}
                  </p>
                  {d.file_url ? (
                    <a
                      href={d.file_url}
                      className="mt-2 inline-block text-sm text-primary underline"
                      target="_blank"
                      rel="noreferrer"
                    >
                      دانلود
                    </a>
                  ) : null}
                </div>
              ))}
            </div>
          )}
        </ShadcnTabsContent>

        <ShadcnTabsContent value="correspondence" className="space-y-4 mt-0">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-lg border p-4">
              <p className="text-sm text-muted-foreground">باز</p>
              <p className="text-xl font-semibold">{openCount}</p>
            </div>
            <div className="rounded-lg border p-4">
              <p className="text-sm text-muted-foreground">سررسید گذشته</p>
              <p className="text-xl font-semibold text-red-600">{overdueCount}</p>
            </div>
          </div>
          {cloading ? (
            <LoadingSkeleton rows={6} />
          ) : cError ? (
            <QueryErrorState onRetry={() => void refetchCorr()} />
          ) : corrRows.length === 0 ? (
            <EmptyState
              icon={<Mail />}
              title="مکاتبه‌ای ثبت نشده"
              description="نامه‌ها و مکاتبات پروژه اینجا نمایش داده می‌شوند."
            />
          ) : (
            <div className="overflow-x-auto rounded-lg border">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    {["شماره", "نوع", "موضوع", "از", "به", "موعد پاسخ", "وضعیت"].map(
                      (h) => (
                        <th key={h} className="px-3 py-2 text-start">
                          {h}
                        </th>
                      ),
                    )}
                  </tr>
                </thead>
                <tbody>
                  {corrRows.map((c) => (
                    <tr key={c.id} className="border-t">
                      <td className="px-3 py-2">{c.corr_number}</td>
                      <td className="px-3 py-2">
                        {CORR_TYPE_LABELS[c.corr_type] ?? c.corr_type}
                      </td>
                      <td className="px-3 py-2">{c.subject}</td>
                      <td className="px-3 py-2">{c.from_party}</td>
                      <td className="px-3 py-2">{c.to_party}</td>
                      <td className="px-3 py-2">
                        {formatDisplayDate(c.response_due_date)}
                      </td>
                      <td className="px-3 py-2">
                        {CORR_STATUS_LABELS[c.status] ?? c.status}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </ShadcnTabsContent>

        <ShadcnTabsContent value="meetings" className="mt-0">
          {mloading ? (
            <LoadingSkeleton rows={6} />
          ) : mError ? (
            <QueryErrorState onRetry={() => void refetchMeetings()} />
          ) : meetingRows.length === 0 ? (
            <EmptyState
              icon={<Users />}
              title="صورتجلسه‌ای ثبت نشده"
              description="جلسات و مصوبات پروژه اینجا نمایش داده می‌شوند."
            />
          ) : (
            <div className="overflow-x-auto rounded-lg border">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    {["تاریخ", "نوع", "مکان", "مصوبات"].map((h) => (
                      <th key={h} className="px-3 py-2 text-start">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {meetingRows.map((m) => (
                    <tr key={m.id} className="border-t">
                      <td className="px-3 py-2">{formatDisplayDate(m.meeting_date)}</td>
                      <td className="px-3 py-2">
                        {MEETING_TYPE_LABELS[m.meeting_type] ?? m.meeting_type}
                      </td>
                      <td className="px-3 py-2">{m.location || "—"}</td>
                      <td className="max-w-md truncate px-3 py-2">{m.decisions}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </ShadcnTabsContent>
      </Tabs>
    </div>
  );
}

export default function ProjectDocumentsPage() {
  const { projectId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto max-w-7xl px-4 py-8">
        <Breadcrumb
          items={[
            { label: "پروژه‌ها", href: `/${PATHS.PROJECT}` },
            { label: "مدارک و مکاتبات" },
          ]}
        />
        <DocumentsContent />
      </main>
    </ProjectProvider>
  );
}
