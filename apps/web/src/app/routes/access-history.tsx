import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router";
import { useTranslation } from "react-i18next";

import { fetchAccessChanges } from "@/app/lib/api/members";
import { formatLocaleDateTime } from "@/app/lib/jalali-utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function AccessHistoryPage() {
  const { projectId } = useParams();
  const organization = !projectId;
  const { t, i18n } = useTranslation();
  const [subject, setSubject] = useState("");
  const [actor, setActor] = useState("");
  const [project, setProject] = useState("");
  const [since, setSince] = useState("");
  const [until, setUntil] = useState("");
  const [page, setPage] = useState(1);
  const [applied, setApplied] = useState({ subject: "", actor: "", project: "", since: "", until: "" });

  const query = useQuery({
    queryKey: ["access-history", projectId ?? "organization", applied, page],
    queryFn: () =>
      fetchAccessChanges(projectId ?? null, {
        subject: applied.subject || undefined,
        actor: applied.actor || undefined,
        project: applied.project || undefined,
        since: applied.since || undefined,
        until: applied.until || undefined,
        page,
      }),
  });

  return (
    <section className="space-y-4">
      <h1 className="text-xl font-semibold">{t("projectMembers.historyTitle")}</h1>
      <form
        className="grid gap-2 md:grid-cols-4"
        onSubmit={(event) => {
          event.preventDefault();
          setPage(1);
          setApplied({ subject, actor, project, since, until });
        }}
      >
        <Input aria-label={t("projectMembers.filterSubject")} value={subject} onChange={(event) => setSubject(event.target.value)} placeholder={t("projectMembers.filterSubject")} />
        <Input aria-label={t("projectMembers.filterActor")} value={actor} onChange={(event) => setActor(event.target.value)} placeholder={t("projectMembers.filterActor")} />
        <Input aria-label={t("projectMembers.filterSince")} type="date" value={since} onChange={(event) => setSince(event.target.value)} />
        <Input aria-label={t("projectMembers.filterUntil")} type="date" value={until} onChange={(event) => setUntil(event.target.value)} />
        {organization ? (
          <Input aria-label={t("projectMembers.filterProject")} value={project} onChange={(event) => setProject(event.target.value)} placeholder={t("projectMembers.filterProject")} />
        ) : null}
        <Button type="submit">{t("projectMembers.applyFilters")}</Button>
      </form>
      {query.isError ? <p className="text-sm text-destructive">{t("projectMembers.historyForbidden")}</p> : null}
      <ul className="space-y-2 text-sm">
        {(query.data?.results ?? []).map((row) => (
          <li key={row.id} className="rounded border border-border p-3">
            <p>{formatLocaleDateTime(row.created_at, i18n.language)} — {row.actor_name || t("projectMembers.unknownValue")} — {row.subject_name || row.role_name}</p>
            <p>{t(`projectMembers.origins.${row.origin}`, { defaultValue: row.origin })} — {row.action}</p>
            {row.unknown.length > 0 ? <p>{t("projectMembers.unknownValue")}</p> : null}
          </li>
        ))}
      </ul>
      <div className="flex gap-2">
        <Button type="button" variant="secondary" disabled={page <= 1} onClick={() => setPage((current) => current - 1)}>
          {t("projectMembers.previousPage")}
        </Button>
        <Button
          type="button"
          variant="secondary"
          disabled={(query.data?.page ?? 1) * (query.data?.page_size ?? 50) >= (query.data?.count ?? 0)}
          onClick={() => setPage((current) => current + 1)}
        >
          {t("projectMembers.nextPage")}
        </Button>
      </div>
    </section>
  );
}
