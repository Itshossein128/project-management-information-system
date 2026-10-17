import { expect } from "@playwright/test";
import type { APIRequestContext } from "@playwright/test";

export const restoreBase = (id: string) => `/api/v1/projects/${id}/`;
export async function assertResponse(response: Awaited<ReturnType<APIRequestContext["get"]>>) {
  if (!response.ok()) throw new Error(`Request failed (${response.status()}): ${await response.text()}`);
  return response.json();
}

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import type { Page } from "@playwright/test";
export function realActors() {
  return JSON.parse(readFileSync(resolve(__dirname,"../../test-results/status-undo-actors.json"),"utf8")) as Record<string,{access:string;refresh:string;user:{id:string;full_name:string;roles:string[]}}>;
}
export async function realSession(page: Page, actor: ReturnType<typeof realActors>[string], language: string) {
  await page.context().addCookies([{name:"auth_token",value:actor.access,url:"http://localhost:5173"}]);
  await page.addInitScript(({actor,language})=>{
    localStorage.setItem("auth_access_token",actor.access);localStorage.setItem("auth_refresh_token",actor.refresh);
    localStorage.setItem("auth_user",JSON.stringify(actor.user));localStorage.setItem("app-language",language);localStorage.setItem("i18nextLng",language);
  },{actor,language});
}
export async function createStatusSourceProject(request: APIRequestContext, origin: string, incomplete = false, operation = "undo_completion") {
 const creator=realActors().creator;
 const headers={Authorization:`Bearer ${creator.access}`};
 const url="http://localhost:8000/api/v1/projects/";
 await expect.poll(async()=>{try{return(await request.get(url,{headers})).status();}catch{return 0;}},{timeout:15000,message:"The real restore API must be ready"}).toBe(200);
 const p=await assertResponse(await request.post(url,{headers,data:{project_code:`AR-${crypto.randomUUID().slice(0,16)}`,project_name:"Status undo browser project",employer:"E",start_date:"2026-10-16",project_manager:creator.user.id,scope_description:"Approved scope",contract_amount:"1000"}}));
 const base=`${url}${p.project_id}/`;
 for(const action of ["submit","approve",...(incomplete?["prepare-incomplete"]:[]),...(origin==="suspended"||operation==="resume"?["suspend"]:[]),...(operation==="undo_completion"?["complete"]:[])]){
  if(action==="prepare-incomplete") {
   const cr=await assertResponse(await request.post(base+"change-requests/",{headers,data:{reason:"Prepare incomplete known-origin fixture",proposed_changes:{scope_description:" ",contract_amount:null}}}));
   await assertResponse(await request.post(`${base}change-requests/${cr.id}/submit/`,{headers,data:{}}));
   await assertResponse(await request.post(`${base}change-requests/${cr.id}/approve/`,{headers:{Authorization:`Bearer ${realActors().administrator.access}`},data:{}}));
   await assertResponse(await request.patch(base,{headers,data:{project_manager:null}}));
   continue;
  }
  await assertResponse(await request.post(`${base}${action}/`,{headers,data:{}}));
 }
 return {id:p.project_id as string,base};
}

export async function grantOrdinaryProjectAuthority(request:APIRequestContext,project:{base:string}) {
 const actors=realActors();const headers={Authorization:`Bearer ${actors.administrator.access}`};const user=actors.ordinary.user;
 const roles=await assertResponse(await request.get("http://localhost:8000/api/v1/roles/",{headers}));
 const viewer=(Array.isArray(roles)?roles:roles.results).find((r:{role_name:string})=>r.role_name==="viewer");expect(viewer).toBeTruthy();
 await assertResponse(await request.post(project.base+"members/",{headers,data:{user_id:user.id,role_ids:[viewer.id]}}));
 for(const permission_codename of ["view_project","edit_project","approve_project"]) {
  await assertResponse(await request.post(`${project.base}members/${user.id}/permissions/`,{headers,data:{permission_codename,is_granted:true}}));
 }
 await assertResponse(await request.patch(project.base,{headers,data:{project_manager:user.id}}));
 const effective=await assertResponse(await request.get(`${project.base}members/${user.id}/permissions/`,{headers:{Authorization:`Bearer ${actors.ordinary.access}`}}));
 for(const code of ["view_project","edit_project","approve_project"])expect(effective.effective[code]).toBe(true);
}

export async function grantHistoryOnlyProjectAuthority(request:APIRequestContext,project:{base:string}) {
 const actors=realActors();const headers={Authorization:`Bearer ${actors.administrator.access}`};const user=actors.viewer.user;
 const roles=await assertResponse(await request.get('http://localhost:8000/api/v1/roles/',{headers}));
 const viewer=(Array.isArray(roles)?roles:roles.results).find((r:{role_name:string})=>r.role_name==='viewer');expect(viewer).toBeTruthy();
 await assertResponse(await request.post(project.base+'members/',{headers,data:{user_id:user.id,role_ids:[viewer.id]}}));
 // Existing membership API permits clearing roles; grant only the exact tested permission.
 await assertResponse(await request.patch(`${project.base}members/${user.id}/`,{headers,data:{role_ids:[]}}));
 await assertResponse(await request.post(`${project.base}members/${user.id}/permissions/`,{headers,data:{permission_codename:'view_project',is_granted:true}}));
 const own={Authorization:`Bearer ${actors.viewer.access}`};
 const effective=await assertResponse(await request.get(`${project.base}members/${user.id}/permissions/`,{headers:own}));
 expect(Object.entries(effective.effective).filter(([,granted])=>granted===true).map(([code])=>code)).toEqual(['view_project']);
 expect(actors.viewer.user.roles).toEqual([]);
 return actors.viewer;
}
