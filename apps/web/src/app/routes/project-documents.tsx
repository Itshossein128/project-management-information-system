import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FolderOpen, Mail, Users } from "lucide-react";
import { useState } from "react";
import { useParams } from "react-router";
import {
  ProjectProvider,
  usePermission,
  useProject,
} from "@/app/contexts/project-context";
import {
  CORR_STATUS_LABELS,
  CORR_TYPE_LABELS,
  createCorrespondence,
  DOC_TYPE_LABELS,
  fetchCorrespondence,
  fetchDocuments,
  fetchMeetings,
  MEETING_TYPE_LABELS,
  respondCorrespondence,
  uploadDocument,
} from "@/app/lib/api/documents";
import { formatDisplayDate } from "@/app/lib/jalali-utils";
import { PATHS } from "@/app/routeVars";
import { Field, Input } from "@/components/form";
import { JalaliDatePicker } from "@/components/form/JalaliDatePicker";
import { EmptyState } from "@/components/layout/empty-state";
import {
  Breadcrumb,
  LoadingSkeleton,
  PageHeader,
} from "@/components/layout/page-header";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { Drawer } from "@/components/ui/drawer";
import { Button } from "@/components/ui/sprint-button";
import { Tabs, TabsContent as ShadcnTabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/components/ui/toast";

type Tab = "archive" | "correspondence" | "meetings";

function DocumentsContent() {
  const { projectId, project, isLoading } = useProject();
  const { has } = usePermission(projectId);
  const canViewDocs = has("view_documents");
  const canUpload = has("upload_documents");
  const canViewCorr = has("view_correspondence") || canViewDocs;
  const canEditCorr = has("edit_correspondence");
  const toast = useToast();
  const qc = useQueryClient();
  const [tab, setTab] = useState<Tab>("archive");
  const [search, setSearch] = useState("");
  const [overdueOnly, setOverdueOnly] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [corrOpen, setCorrOpen] = useState(false);
  const [uploadForm, setUploadForm] = useState({
    title: "",
    doc_type: "other",
    doc_code: "",
    file: null as File | null,
  });
  const [corrForm, setCorrForm] = useState({
    corr_type: "incoming",
    subject: "",
    from_party: "",
    to_party: "",
    corr_date: "",
    response_due_date: "",
  });

  const canViewCurrent =
    tab === "archive" ? canViewDocs : tab === "correspondence" ? canViewCorr : canViewDocs;

  const {
    data: docs,
    isLoading: dloading,
    isError: dError,
    refetch: refetchDocs,
  } = useQuery({
    queryKey: ["documents", projectId, search],
    queryFn: () => fetchDocuments(projectId, search ? { search } : {}),
    enabled: canViewDocs && tab === "archive",
  });

  const {
    data: corr,
    isLoading: cloading,
    isError: cError,
    refetch: refetchCorr,
  } = useQuery({
    queryKey: ["correspondence", projectId, overdueOnly],
    queryFn: () =>
      fetchCorrespondence(projectId, overdueOnly ? { overdue: "true" } : {}),
    enabled: canViewCorr && tab === "correspondence",
  });

  const {
    data: meetings,
    isLoading: mloading,
    isError: mError,
    refetch: refetchMeetings,
  } = useQuery({
    queryKey: ["meetings", projectId],
    queryFn: () => fetchMeetings(projectId),
    enabled: canViewDocs && tab === "meetings",
  });

  const uploadMut = useMutation({
    mutationFn: () => {
      const fd = new FormData();
      fd.append("title", uploadForm.title);
      fd.append("doc_type", uploadForm.doc_type);
      if (uploadForm.doc_code) fd.append("doc_code", uploadForm.doc_code);
      if (uploadForm.file) fd.append("file", uploadForm.file);
      return uploadDocument(projectId, fd);
    },
    onSuccess: () => {
      toast.success("مدرک بارگذاری شد");
      setUploadOpen(false);
      void qc.invalidateQueries({ queryKey: ["documents", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const corrMut = useMutation({
    mutationFn: () =>
      createCorrespondence(projectId, {
        corr_type: corrForm.corr_type,
        subject: corrForm.subject,
        from_party: corrForm.from_party,
        to_party: corrForm.to_party,
        corr_date: corrForm.corr_date,
        response_due_date: corrForm.response_due_date || null,
      }),
    onSuccess: () => {
      toast.success("مکاتبه ثبت شد");
      setCorrOpen(false);
      void qc.invalidateQueries({ queryKey: ["correspondence", projectId] });
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (isLoading) return <LoadingSkeleton rows={8} />;
  if (!project) {
    return <EmptyState title="پروژه یافت نشد" />;
  }
  if (!canViewCurrent) {
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
        <div className="mb-4 flex flex-wrap items-center gap-2">
          <TabsList>
            {tabs.map(([id, label]) => (
              <TabsTrigger key={id} value={id}>
                {label}
              </TabsTrigger>
            ))}
          </TabsList>
          {tab === "archive" && canUpload ? (
            <Button className="ms-auto" size="sm" onClick={() => setUploadOpen(true)}>
              بارگذاری مدرک
            </Button>
          ) : null}
          {tab === "correspondence" && canEditCorr ? (
            <Button className="ms-auto" size="sm" onClick={() => setCorrOpen(true)}>
              مکاتبه جدید
            </Button>
          ) : null}
        </div>

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
                  <p className="text-xs text-muted-foreground">
                    {DOC_TYPE_LABELS[d.doc_type] ?? d.doc_type}
                  </p>
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
            <label className="flex items-center gap-2 rounded-lg border p-4 text-sm">
              <input
                type="checkbox"
                checked={overdueOnly}
                onChange={(e) => setOverdueOnly(e.target.checked)}
              />
              فقط سررسید گذشته
            </label>
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
                    {[
                      "شماره",
                      "نوع",
                      "موضوع",
                      "از",
                      "به",
                      "موعد پاسخ",
                      "وضعیت",
                      "",
                    ].map((h) => (
                      <th key={h} className="px-3 py-2 text-start">
                        {h}
                      </th>
                    ))}
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
                      <td className="px-3 py-2">
                        {canEditCorr && c.status === "open" ? (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() =>
                              respondCorrespondence(projectId, c.id)
                                .then(() => {
                                  toast.success("پاسخ ثبت شد");
                                  void qc.invalidateQueries({
                                    queryKey: ["correspondence", projectId],
                                  });
                                })
                                .catch((e: Error) => toast.error(e.message))
                            }
                          >
                            ثبت پاسخ
                          </Button>
                        ) : null}
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

      <Drawer
        isOpen={uploadOpen}
        onClose={() => setUploadOpen(false)}
        title="بارگذاری مدرک"
        footer={
          <Button onClick={() => uploadMut.mutate()} loading={uploadMut.isPending}>
            ذخیره
          </Button>
        }
      >
        <div className="space-y-3 p-4">
          <input
            className="w-full rounded border px-2 py-1"
            placeholder="عنوان"
            value={uploadForm.title}
            onChange={(e) => setUploadForm((f) => ({ ...f, title: e.target.value }))}
          />
          <select
            className="w-full rounded border px-2 py-1"
            value={uploadForm.doc_type}
            onChange={(e) => setUploadForm((f) => ({ ...f, doc_type: e.target.value }))}
          >
            {Object.entries(DOC_TYPE_LABELS).map(([k, v]) => (
              <option key={k} value={k}>
                {v}
              </option>
            ))}
          </select>
          <input
            className="w-full rounded border px-2 py-1"
            placeholder="کد مدرک"
            value={uploadForm.doc_code}
            onChange={(e) => setUploadForm((f) => ({ ...f, doc_code: e.target.value }))}
          />
          <input
            type="file"
            onChange={(e) =>
              setUploadForm((f) => ({ ...f, file: e.target.files?.[0] ?? null }))
            }
          />
        </div>
      </Drawer>

      <Drawer
        isOpen={corrOpen}
        onClose={() => setCorrOpen(false)}
        title="مکاتبه جدید"
        footer={
          <Button onClick={() => corrMut.mutate()} loading={corrMut.isPending}>
            ذخیره
          </Button>
        }
      >
        <div className="space-y-3 p-4">
          <select
            className="w-full rounded border px-2 py-1"
            value={corrForm.corr_type}
            onChange={(e) => setCorrForm((f) => ({ ...f, corr_type: e.target.value }))}
          >
            {Object.entries(CORR_TYPE_LABELS).map(([k, v]) => (
              <option key={k} value={k}>
                {v}
              </option>
            ))}
          </select>
          <input
            className="w-full rounded border px-2 py-1"
            placeholder="موضوع"
            value={corrForm.subject}
            onChange={(e) => setCorrForm((f) => ({ ...f, subject: e.target.value }))}
          />
          <input
            className="w-full rounded border px-2 py-1"
            placeholder="از"
            value={corrForm.from_party}
            onChange={(e) => setCorrForm((f) => ({ ...f, from_party: e.target.value }))}
          />
          <input
            className="w-full rounded border px-2 py-1"
            placeholder="به"
            value={corrForm.to_party}
            onChange={(e) => setCorrForm((f) => ({ ...f, to_party: e.target.value }))}
          />
          <JalaliDatePicker
            name="corr_date"
            label="تاریخ"
            value={corrForm.corr_date}
            onChange={(v) => setCorrForm((f) => ({ ...f, corr_date: v }))}
          />
          <JalaliDatePicker
            name="response_due_date"
            label="موعد پاسخ"
            value={corrForm.response_due_date}
            onChange={(v) => setCorrForm((f) => ({ ...f, response_due_date: v }))}
          />
        </div>
      </Drawer>
    </div>
  );
}

export default function ProjectDocumentsPage() {
  const { projectId } = useParams();
  return (
    <ProjectProvider projectId={projectId!}>
      <main className="page-main page-shell mx-auto px-4 py-8">
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
