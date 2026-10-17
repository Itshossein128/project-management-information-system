import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { fetchStatusUndoHistory } from "@/app/lib/api/projects";
import { Button } from "@/components/ui/sprint-button";
import { QueryErrorState } from "@/components/layout/query-error-state";
import { useAuth } from "@/app/contexts/auth-context";

export function ProjectStatusUndoHistory({projectId}:{projectId:string}) {
 const {user,isLoading}=useAuth();
 if(isLoading||!user)return null;
 return <StatusUndoHistorySession key={`${user.id}:${projectId}`} projectId={projectId} actorId={user.id}/>;
}

function StatusUndoHistorySession({projectId,actorId}:{projectId:string;actorId:string}) {
 const {t,i18n}=useTranslation();const [page,setPage]=useState(1);
 const history=useQuery({queryKey:["status-undo-history",projectId,actorId,page],queryFn:()=>fetchStatusUndoHistory(projectId,page),retry:false});
 const label=(status:string)=>t(`projectStatusUndo.targets.${status}`);
 const time=(value:string)=><time dateTime={value}>{new Date(value).toLocaleString(i18n.language==="fa"?"fa-IR":"en-GB")}</time>;
 return <section data-testid="status-undo-history" aria-label={t("projectStatusUndo.historyTitle")} className="min-w-0 space-y-4 rounded-xl border bg-card p-4">
  <h2 className="font-semibold">{t("projectStatusUndo.historyTitle")}</h2>
  {history.isPending?<p role="status">{t("common.loading")}</p>:history.isError?<QueryErrorState onRetry={()=>void history.refetch()}/>:<>
   {history.data.results.length===0?<p className="text-muted-foreground">{t("projectStatusUndo.historyEmpty")}</p>:<ol className="space-y-4">{history.data.results.map(event=><li key={event.id} className="space-y-3 break-words rounded-lg border p-3">
    <p className="font-semibold">{event.project_name} · {t(event.operation==="resume"?"project.resume":"projectStatusUndo.action")}</p>
    <p>{t("projectStatusUndo.historyActor")}: {event.actor.display_name}</p><p>{t("projectStatusUndo.historyTime")}: {time(event.performed_at)}</p>
    <p>{t("projectStatusUndo.historyFrom")}: {label(event.from_status)} · {t("projectStatusUndo.historyTo")}: {label(event.to_status)}</p>
    <p className="whitespace-pre-wrap">{t("projectStatusUndo.reason")}: {event.reason}</p>
    <div className="space-y-2 rounded bg-muted/40 p-3 text-sm"><h3 className="font-medium">{t(`projectStatusUndo.originalKinds.${event.source_event.kind}`)}</h3><p>{event.source_event.project_name}</p><p>{t("projectStatusUndo.originalActor")}: {event.source_event.actor.display_name}</p><p>{t("projectStatusUndo.originalTime")}: {time(event.source_event.occurred_at)}</p><p>{t("projectStatusUndo.historyFrom")}: {label(event.source_event.from_status)} · {t("projectStatusUndo.historyTo")}: {label(event.source_event.to_status)}</p></div>
   </li>)}</ol>}
   <nav aria-label={t("projectStatusUndo.historyTitle")} className="flex flex-wrap items-center gap-2"><Button variant="secondary" size="sm" data-testid="status-undo-history-previous" disabled={!history.data.previous} onClick={()=>setPage(n=>Math.max(1,n-1))}>{t("projectStatusUndo.previousPage")}</Button><span>{t("projectStatusUndo.historyPage",{page,count:history.data.count})}</span><Button variant="secondary" size="sm" data-testid="status-undo-history-next" disabled={!history.data.next} onClick={()=>setPage(n=>n+1)}>{t("projectStatusUndo.nextPage")}</Button></nav>
  </>}
 </section>;
}
