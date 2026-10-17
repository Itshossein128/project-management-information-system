import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { fetchRestoreHistory } from "@/app/lib/api/projects";
import { Button } from "@/components/ui/sprint-button";
import { QueryErrorState } from "@/components/layout/query-error-state";

export function ProjectArchiveRestoreHistory({projectId}:{projectId:string}) {
  const {t,i18n}=useTranslation();const [page,setPage]=useState(1);
  const history=useQuery({queryKey:["restore-history",projectId,page],queryFn:()=>fetchRestoreHistory(projectId,page)});
  const status=(value:string)=>t(`projectRestore.targets.${value}`,{defaultValue:t("projects.status.archived",{defaultValue:value})});
  return <section data-testid="restore-history" aria-label={t("projectRestore.historyTitle")} className="rounded-xl border bg-card p-4 space-y-4 min-w-0">
    <h2 className="font-semibold">{t("projectRestore.historyTitle")}</h2>
    {history.isPending?<p role="status">{t("common.loading")}</p>:history.isError?<QueryErrorState onRetry={()=>void history.refetch()}/>:<>
      {history.data.results.length===0?<p className="text-muted-foreground">{t("projectRestore.historyEmpty")}</p>:<ol className="space-y-4">
        {history.data.results.map(event=><li key={event.id} className="rounded-lg border p-3 space-y-2 break-words">
          <p className="font-medium">{event.project_name}</p>
          <p>{t("projectRestore.historyActor")}: {event.actor.display_name}</p>
          <p>{t("projectRestore.historyTime")}: <time dateTime={event.restored_at}>{new Date(event.restored_at).toLocaleString(i18n.language==="fa"?"fa-IR":"en-GB")}</time></p>
          <p>{t("projectRestore.historyFrom")}: {t("projectRestore.archived")} · {t("projectRestore.historyTo")}: {status(event.to_status)}</p>
          <p className="whitespace-pre-wrap">{t("projectRestore.reason")}: {event.reason}</p>
        </li>)}
      </ol>}
      <nav aria-label={t("projectRestore.historyTitle")} className="flex flex-wrap gap-2 items-center">
        <Button variant="secondary" size="sm" disabled={!history.data.previous} onClick={()=>setPage(n=>Math.max(1,n-1))}>{t("projectRestore.previousPage")}</Button>
        <span>{t("projectRestore.historyPage",{page,count:history.data.count})}</span>
        <Button variant="secondary" size="sm" disabled={!history.data.next} onClick={()=>setPage(n=>n+1)}>{t("projectRestore.nextPage")}</Button>
      </nav>
    </>}
  </section>;
}
