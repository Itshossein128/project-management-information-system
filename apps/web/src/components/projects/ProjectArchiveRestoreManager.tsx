import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { lookupUsers } from "@/app/lib/api/members";
import { updateProject, type ProjectDetail } from "@/app/lib/api/projects";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";

export function ProjectArchiveRestoreManager({project}:{project:ProjectDetail}) {
 const {t}=useTranslation();const qc=useQueryClient();const toast=useToast();
 const [search,setSearch]=useState("");const [selected,setSelected]=useState("");
 const users=useQuery({queryKey:["restore-manager-lookup",search],queryFn:()=>lookupUsers(search),enabled:search.trim().length>=2});
 const save=useMutation({mutationFn:()=>updateProject(project.project_id,{project_manager:selected}),onSuccess:()=>{void qc.invalidateQueries({queryKey:["project",project.project_id]});toast.success(t("common.saved"));}});
 return <section id="restore-manager" className="mx-auto mb-8 max-w-2xl space-y-3 rounded-lg border border-border bg-muted/20 p-4">
  <h2 className="font-semibold">{t("projectRestore.completeManager")}</h2>
  <p className="text-sm text-muted-foreground">{t("projectRestore.managerHint")}</p>
  <label htmlFor="restore-manager-search" className="block text-sm">{t("projectRestore.searchManager")}</label>
  <input id="restore-manager-search" data-testid="restore-manager-search" className="w-full rounded border border-input bg-background p-2" value={search} onChange={e=>setSearch(e.target.value)}/>
  <label htmlFor="restore-manager-select" className="block text-sm">{t("projectRestore.chooseManager")}</label>
  <select id="restore-manager-select" data-testid="restore-manager-select" className="w-full rounded border border-input bg-background p-2" value={selected} onChange={e=>setSelected(e.target.value)}>
   <option value="">{t("projectRestore.chooseManager")}</option>
   {(users.data??[]).map(user=><option key={user.user_id} value={user.user_id}>{user.full_name||user.mobile||user.email||t("projectRestore.chooseManager")}</option>)}
  </select>
  {save.isError?<p role="alert">{t("projectRestore.managerError")}</p>:null}
  <Button type="button" data-testid="restore-manager-save" disabled={!selected||save.isPending} onClick={()=>save.mutate()}>{t("common.save")}</Button>
 </section>;
}
