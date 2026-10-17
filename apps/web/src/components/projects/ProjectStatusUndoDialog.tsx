import { Link } from "react-router";
import { readStatusUndoDraft, saveStatusUndoDraft, removeStatusUndoDraft, readPendingStatusUndo, savePendingStatusUndo, removePendingStatusUndo, type PendingStatusUndo } from "@/app/lib/project-status-undo-state";
import { useEffect, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useAuth } from "@/app/contexts/auth-context";
import { getStoredUser } from "@/app/lib/auth-storage";
import { ApiRequestError } from "@/app/lib/api-client";
import { applyStatusUndo,fetchStatusUndoPreview,type ProjectDetail,type StatusUndoOperation,type StatusUndoPayload,type StatusUndoReceipt,type StatusUndoCurrent,fetchStatusUndoAttempt } from "@/app/lib/api/projects";
import { Dialog,DialogTrigger,DialogContent,DialogHeader,DialogTitle,DialogDescription,DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";

export function ProjectStatusUndoSection({project}:{project:ProjectDetail}) {
 const {user}=useAuth();
 return <>{(["resume","undo_completion"] as const).map(operation=><StatusUndoSession key={`${user?.id}:${project.project_id}:${operation}`} project={project} operation={operation}/>)}</>;
}
function StatusUndoSession({project,operation}:{project:ProjectDetail;operation:StatusUndoOperation}) {
 const {user}=useAuth();const {t}=useTranslation();const qc=useQueryClient();const toast=useToast();
 const [open,setOpen]=useState(false);const [reason,setReason]=useState(()=>readStatusUndoDraft(user?.id,project.project_id,operation));const [busy,setBusy]=useState(false);
 const [pending,setPending]=useState<PendingStatusUndo|null>(()=>readPendingStatusUndo(user?.id,project.project_id,operation));const [error,setError]=useState("");const [denied,setDenied]=useState(false);
 const dispatching=useRef(false);const mounted=useRef(true);
 useEffect(()=>{mounted.current=true;return()=>{mounted.current=false;};},[]);
 const ownsView=()=>mounted.current&&getStoredUser()?.id===user?.id;
 const canStart=!denied&&(operation==="resume"?project.can_resume_with_confirmation:project.can_undo_completion);
 const preview=useQuery({queryKey:["status-undo-preview",project.project_id,user?.id,operation],queryFn:()=>fetchStatusUndoPreview(project.project_id,operation),enabled:open&&Boolean(canStart)&&!pending,staleTime:0,refetchOnWindowFocus:false,retry:false});
 const label=(value:string)=>t(`projectStatusUndo.targets.${value}`,{defaultValue:t(`status.${value}`)});
 const close=()=>{setOpen(false);if(!pending){removeStatusUndoDraft(user?.id,project.project_id,operation);setReason("");setError("");}};
 const ownsAttempt=(requestId:string)=>ownsView()&&readPendingStatusUndo(user?.id,project.project_id,operation)?.request_id===requestId;
 const refresh=()=>{void qc.invalidateQueries({queryKey:["project",project.project_id]});};
 const refreshCompleted=()=>{
  refresh();
  for(const queryKey of [["projects"],["status-undo-history",project.project_id],["portfolio-summary"],["portfolio-dashboard"]])void qc.invalidateQueries({queryKey});
 };
 const clear=(requestId:string)=>{removePendingStatusUndo(user?.id,project.project_id,operation,requestId);setPending(null);};
 const resolved=(receipt:StatusUndoReceipt,current:StatusUndoCurrent,fresh:boolean,requestId:string)=>{
  clear(requestId);setReason("");setOpen(false);setError("");refreshCompleted();
  if(fresh)toast.success(t(`projectStatusUndo.success.${operation}`,{name:receipt.project_name,status:label(current.status)}));
  else toast.warning(t("projectStatusUndo.recorded",{name:receipt.project_name,target:label(receipt.to_status),current:label(current.status)}));
 };
 const handleError=(err:unknown,requestId:string)=>{
  if(err instanceof ApiRequestError&&(err.status===401||err.status===403)){clear(requestId);setDenied(true);setOpen(false);setError("denied");return;}
  if(err instanceof ApiRequestError&&err.code==="status_undo_not_applied"){setError("notApplied");return;}
  if(err instanceof ApiRequestError&&err.status<500){clear(requestId);setError(err.code==="status_undo_already_applied"?"another":err.code==="activation_gates_failed"?"incomplete":"changed");refresh();void preview.refetch();return;}
  setError("unknown");
 };
 const send=async(payload:StatusUndoPayload)=>{
  if(dispatching.current||!user?.id)return;
  const source=pending?.source_event_id??preview.data?.source_event_id;if(!source)return;
  const frozen={...payload,user_id:user.id,project_id:project.project_id,operation,source_event_id:source};
  removeStatusUndoDraft(user.id,project.project_id,operation);savePendingStatusUndo(frozen);setPending(frozen);
  dispatching.current=true;setBusy(true);setError("");
  try {const result=await applyStatusUndo(project.project_id,operation,payload);if(ownsAttempt(payload.request_id))resolved(result.receipt,result.current_project,result.outcome==="applied",payload.request_id);}
  catch(err){if(ownsAttempt(payload.request_id))handleError(err,payload.request_id);}
  finally{if(ownsView()){dispatching.current=false;setBusy(false);}}
 };
 const submit=()=>{
  if(dispatching.current||pending||preview.isFetching||preview.isError||!preview.data?.can_confirm||!reason.trim())return;
  void send({request_id:crypto.randomUUID(),confirmation_token:preview.data.confirmation_token,reason:reason.trim()});
 };
 const check=async()=>{
  if(!pending||dispatching.current)return;const requestId=pending.request_id;dispatching.current=true;setBusy(true);
  try {
   const result=await fetchStatusUndoAttempt(project.project_id,operation,requestId);if(!ownsAttempt(requestId))return;
   if(result.outcome==="completed"&&result.receipt)resolved(result.receipt,result.current_project,false,requestId);else setError("notRecorded");
  }catch(err){if(ownsAttempt(requestId))handleError(err,requestId);}finally{if(ownsView()){dispatching.current=false;setBusy(false);}}
 };
 const previewCode=preview.error instanceof ApiRequestError?preview.error.status:0;
 const previewError=[401,403].includes(previewCode)?"previewDenied":[400,404,409,410].includes(previewCode)?"previewChanged":"previewUnavailable";
 const pendingControls=<div className="flex flex-wrap gap-2"><Button variant="outline" onClick={()=>void check()} disabled={busy}>{t("projectStatusUndo.checkResult")}</Button><Button variant="outline" onClick={()=>pending&&void send({request_id:pending.request_id,confirmation_token:pending.confirmation_token,reason:pending.reason})} disabled={busy}>{t("projectStatusUndo.retrySame")}</Button></div>;
 if(!canStart&&!pending&&!error&&!open)return null;
 return <section className="mb-4 space-y-3" data-testid={`project-status-undo-${operation}`}>
  {pending?<div data-testid={`status-undo-unresolved-${operation}`} className="space-y-3 rounded-md border border-amber-500/50 bg-muted p-4"><p className="font-semibold">{t(operation==="resume"?"project.resume":"projectStatusUndo.action")}</p><p role="alert">{t(`projectStatusUndo.${busy?"pending":error||"unknown"}`)}</p>{pendingControls}</div>:!open&&error?<p role="alert">{t(`projectStatusUndo.${error}`)}</p>:null}
  <Dialog open={open} onOpenChange={value=>value?setOpen(true):close()}>
   {canStart&&!pending?<DialogTrigger asChild><Button variant="outline">{t(operation==="resume"?"project.resume":"projectStatusUndo.action")}</Button></DialogTrigger>:null}
   <DialogContent className="max-h-[90dvh] overflow-y-auto">
    <DialogHeader><DialogTitle>{t(operation==="resume"?"project.resume":"projectStatusUndo.action")}</DialogTitle><DialogDescription>{t("projectStatusUndo.description")}</DialogDescription></DialogHeader>
    {pending?<><p role="alert">{t(`projectStatusUndo.${busy?"pending":error||"unknown"}`)}</p><p>{pending.reason}</p><p>{t("projectStatusUndo.dismissHint")}</p>{pendingControls}</>:preview.isError?<div className="space-y-3"><p role="alert">{t(`projectStatusUndo.${previewError}`)}</p><Button variant="outline" onClick={()=>void preview.refetch()} disabled={preview.isFetching}>{t("projectStatusUndo.retryPreview")}</Button></div>:preview.isPending?<p>{t("common.loading")}</p>:preview.data?<>
     <p className="font-semibold">{preview.data.project_name}</p><p>{t("projectStatusUndo.source")}: {label(preview.data.from_status)}</p>
     <p data-testid="status-undo-target">{t("projectStatusUndo.destination")}: <strong>{label(preview.data.to_status)}</strong></p>
     <p className="rounded-md bg-muted p-3 text-sm">{t(`projectStatusUndo.effects.${operation==="resume"?"resume":`undo_completion_${preview.data.to_status}`}`)}</p>
     <p className="text-sm text-muted-foreground">{t("projectStatusUndo.preserve")}</p>
     {preview.data.missing.length>0?<div role="alert"><p>{t("project.activationIncomplete")}</p><ul className="list-disc space-y-2 ps-5">{preview.data.missing.map(field=><li key={field}>{t(`projectStatusUndo.missing.${field}`)} {preview.data.remediation.find(row=>row.field===field)?.can_perform?<Link className="font-semibold underline" onClick={()=>saveStatusUndoDraft(user?.id,project.project_id,operation,reason)} to={`/projects/${project.project_id}/settings${field==="project_manager"?"#restore-manager":"#project-change-requests"}`}>{t(field==="project_manager"?"projectStatusUndo.completeManager":"projectStatusUndo.reviewChanges")}</Link>:<span className="block text-sm">{t("projectStatusUndo.contactEditor")}</span>}</li>)}</ul></div>:null}
     <div className="space-y-2"><label htmlFor={`status-undo-reason-${operation}-${project.project_id}`}>{t("projectStatusUndo.reason")}</label><textarea id={`status-undo-reason-${operation}-${project.project_id}`} className="w-full rounded-md border border-input bg-background p-2" value={reason} onChange={e=>setReason(e.target.value)} required aria-describedby={`undo-reason-help-${operation}`}/></div>
     <p id={`undo-reason-help-${operation}`} className="text-sm text-muted-foreground">{t("projectStatusUndo.reasonRequired")}</p>
    </>:null}
    {!pending&&error?<p role="alert">{t(`projectStatusUndo.${error}`)}</p>:null}
    <DialogFooter><Button variant="outline" onClick={close}>{t(pending?"common.close":"common.cancel")}</Button>
     {!pending?<Button onClick={()=>void submit()} disabled={busy||preview.isFetching||preview.isError||!preview.data?.can_confirm||!reason.trim()}>{t("projectStatusUndo.confirm")}</Button>:null}
    </DialogFooter>
   </DialogContent>
  </Dialog>
 </section>;
}
