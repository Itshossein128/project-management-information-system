import { useEffect, useRef, useState } from "react";
import { Link } from "react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useAuth } from "@/app/contexts/auth-context";
import { getStoredUser } from "@/app/lib/auth-storage";
import { ApiRequestError } from "@/app/lib/api-client";
import { fetchRestorePreview, restoreProject, fetchRestoreAttempt, type ProjectDetail, type RestoreResult, type RestorePayload, type RestoreReceipt } from "@/app/lib/api/projects";
import { readPendingRestore, savePendingRestore, removePendingRestore, readRestoreDraft, saveRestoreDraft, removeRestoreDraft, type PendingArchiveRestore } from "@/app/lib/project-archive-restore-pending";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";

export function ProjectArchiveRestoreDialog({project}:{project:ProjectDetail}) {
 const {user}=useAuth();
 return <RestoreDialogSession key={`${user?.id}:${project.project_id}`} project={project}/>;
}

function RestoreDialogSession({project}:{project:ProjectDetail}) {
 const {t}=useTranslation();const {user}=useAuth();const qc=useQueryClient();const toast=useToast();
 const [open,setOpen]=useState(false);const [reason,setReason]=useState(()=>readRestoreDraft(user?.id,project.project_id));
 const [busy,setBusy]=useState(false);const [error,setError]=useState("");const [denied,setDenied]=useState(false);
 const [pending,setPending]=useState<PendingArchiveRestore|null>(()=>readPendingRestore(user?.id,project.project_id));
 const preview=useQuery({queryKey:["restore-preview",project.project_id,user?.id],queryFn:()=>fetchRestorePreview(project.project_id),enabled:open&&Boolean(project.can_restore_from_archive)&&!pending,staleTime:0,refetchOnWindowFocus:false,retry:(count,err)=>count<1&&!(err instanceof ApiRequestError&&err.status<500)});
 const mounted=useRef(true);
 useEffect(()=>{mounted.current=true;return()=>{mounted.current=false;};},[]);
 // A sent request survives navigation for result lookup; its late response
 // must not mutate a new project/account view or disclose the old receipt.
 const ownsView=()=>mounted.current&&getStoredUser()?.id===user?.id;
 const label=(status:string)=>t(`projectRestore.targets.${status}`,{defaultValue:t(`status.${status}`)});
 const refresh=()=>{
  void qc.invalidateQueries({queryKey:["project",project.project_id]});
  void qc.invalidateQueries({queryKey:["projects"]});
  void qc.invalidateQueries({queryKey:["restore-history",project.project_id]});
 };
 const clear=(requestId?:string)=>{removePendingRestore(user?.id,project.project_id,requestId);setPending(null);};
 const resolved=(receipt:RestoreReceipt,current:RestoreResult["current_project"],fresh=false,requestId?:string)=>{
  clear(requestId);setOpen(false);setReason("");setError("");refresh();
  void qc.invalidateQueries({queryKey:["portfolio-summary"]});
  void qc.invalidateQueries({queryKey:["portfolio-dashboard"]});
  if(fresh&&receipt.to_status===current.status)toast.success(t("projectRestore.success",{name:receipt.project_name,status:label(current.status)}));
  else toast.warning(t("projectRestore.recorded",{name:receipt.project_name,target:label(receipt.to_status),current:label(current.status)}));
 };
 const handleError=(err:unknown,requestId?:string)=>{
  if(err instanceof ApiRequestError&&(err.status===401||err.status===403)) {
   clear(requestId);setDenied(true);setOpen(false);setError("denied");refresh();return;
  }
  if(err instanceof ApiRequestError&&err.code==="restore_not_applied") {setError("notApplied");return;}
  if(err instanceof ApiRequestError&&err.status<500) {
   clear(requestId);
   if(err.code==="archive_already_restored") {setError("another");setOpen(false);refresh();}
   else {setError(err.code==="activation_gates_failed"?"incomplete":"changed");void preview.refetch();refresh();}
   return;
  }
  setError("unknown");
 };
 const send=async(payload:RestorePayload)=>{
  if(busy||!user?.id)return;
  const saved={...payload,user_id:user.id,project_id:project.project_id};
  removeRestoreDraft(user.id,project.project_id);setPending(saved);savePendingRestore(saved);setBusy(true);setError("");
  try {const result=await restoreProject(project.project_id,payload);if(ownsView())resolved(result.receipt,result.current_project,result.outcome==="restored",payload.request_id);}
  catch(err){if(ownsView())handleError(err,payload.request_id);}
  finally{if(ownsView())setBusy(false);}
 };
 const submit=()=>{
  if(busy||pending||preview.isFetching||preview.isError||!preview.data?.can_confirm||!reason.trim())return;
  void send({request_id:crypto.randomUUID(),confirmation_token:preview.data.confirmation_token,reason:reason.trim()});
 };
 const check=async()=>{
  if(!pending||busy)return;setBusy(true);
  try {
   const result=await fetchRestoreAttempt(project.project_id,pending.request_id);
   if(!ownsView())return;
   if(result.outcome==="completed"&&result.receipt)resolved(result.receipt,result.current_project,false,pending.request_id);
   else setError("notRecorded");
  } catch(err){if(ownsView())handleError(err,pending.request_id);}finally{if(ownsView())setBusy(false);}
 };
 const previewCode=preview.error instanceof ApiRequestError?preview.error.status:0;
 const previewError=previewCode===401||previewCode===403?"previewDenied":[400,404,409,410].includes(previewCode)?"previewChanged":"previewUnavailable";
 const canStart=project.can_restore_from_archive&&!denied&&!pending&&!(preview.isError&&previewError==="previewDenied");
 if(!canStart&&!pending&&!error&&!open)return null;
 const pendingControls=<div className="flex flex-wrap gap-2">
  <Button type="button" variant="outline" onClick={()=>void check()} disabled={busy}>{t("projectRestore.checkResult")}</Button>
  <Button type="button" variant="outline" onClick={()=>pending&&void send({request_id:pending.request_id,confirmation_token:pending.confirmation_token,reason:pending.reason})} disabled={busy}>{t("projectRestore.retrySame")}</Button>
 </div>;
 return <section className="mb-4 space-y-3" data-testid="project-archive-restore">
  {pending?<div className="space-y-3 rounded-md border border-amber-500/50 bg-muted p-4" data-testid="restore-unresolved"><p role="alert">{t(`projectRestore.${busy?"pending":error||"unknown"}`)}</p>{pendingControls}</div>:!open&&error?<p role="alert">{t(`projectRestore.${error}`)}</p>:null}
  <Dialog open={open} onOpenChange={value=>{setOpen(value);if(!value&&!pending){removeRestoreDraft(user?.id,project.project_id);setReason("");setError("");}}}>
   {canStart?<DialogTrigger asChild><Button variant="outline">{t("projectRestore.action")}</Button></DialogTrigger>:null}
   <DialogContent className="max-h-[90dvh] overflow-y-auto">
    <DialogHeader><DialogTitle>{t("projectRestore.action")}</DialogTitle><DialogDescription>{t("projectRestore.description")}</DialogDescription></DialogHeader>
    {pending?<><p role="alert">{t(`projectRestore.${busy?"pending":error||"unknown"}`)}</p><p>{t("projectRestore.sentReason")}: {pending.reason}</p><p>{t("projectRestore.dismissHint")}</p>{pendingControls}</>:preview.isError?<div className="space-y-3"><p role="alert">{t(`projectRestore.${previewError}`)}</p><Button variant="outline" onClick={()=>void preview.refetch()} disabled={preview.isFetching}>{t("projectRestore.retryPreview")}</Button></div>:preview.isPending?<p>{t("common.loading")}</p>:preview.data?<>
     <p className="font-semibold">{preview.data.project_name}</p>
     <p data-testid="restore-target">{t("projectRestore.destination")}: <strong>{label(preview.data.to_status)}</strong></p>
     <p className="rounded-md bg-muted p-3 text-sm">{t(`projectRestore.effects.${preview.data.to_status}`)}</p>
     <p className="text-sm text-muted-foreground">{t("projectRestore.preserve")}</p>
     {preview.data.missing.length>0?<div role="alert"><p>{t("projectRestore.incomplete")}</p><ul className="list-disc ps-5 space-y-2">{preview.data.missing.map(field=><li key={field}>{t(`projectRestore.missing.${field}`)} <Link className="font-semibold underline" onClick={()=>saveRestoreDraft(user?.id,project.project_id,reason)} to={`/projects/${project.project_id}/settings${field==="project_manager"?"#restore-manager":"#project-change-requests"}`}>{t(field==="project_manager"?"projectRestore.completeManager":"projectRestore.reviewChanges")}</Link></li>)}</ul></div>:null}
     <div className="space-y-2"><label htmlFor={`restore-reason-${project.project_id}`}>{t("projectRestore.reason")}</label>
      <textarea id={`restore-reason-${project.project_id}`} className="w-full rounded-md border border-input bg-background p-2" value={reason} onChange={e=>setReason(e.target.value)} disabled={busy} required aria-describedby="restore-reason-help"/>
      <p id="restore-reason-help" className="text-sm text-muted-foreground">{t("projectRestore.reasonRequired")}</p></div>
    </>:<p role="alert">{t("projectRestore.changed")}</p>}
    {!pending&&error?<p role="alert">{t(`projectRestore.${error}`)}</p>:null}
    <DialogFooter><Button variant="outline" onClick={()=>{setOpen(false);if(!pending){removeRestoreDraft(user?.id,project.project_id);setReason("");setError("");}}}>{t(pending?"common.close":"common.cancel")}</Button>
     {!pending?<Button onClick={submit} disabled={busy||preview.isFetching||preview.isError||!preview.data?.can_confirm||!reason.trim()}>{busy?t("projectRestore.pending"):t("projectRestore.confirm")}</Button>:null}</DialogFooter>
   </DialogContent>
  </Dialog>
 </section>;
}
