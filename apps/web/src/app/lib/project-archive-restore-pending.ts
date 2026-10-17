import type { RestorePayload } from "./api/projects";
export interface PendingArchiveRestore extends RestorePayload { user_id:string;project_id:string }
const prefix="velora:archive-restore:";
const key=(user:string,project:string)=>`${prefix}${user}:${project}`;
export function readPendingRestore(user:string|undefined,project:string):PendingArchiveRestore|null {
 if(typeof window==="undefined"||!user)return null;
 try {
  const value=JSON.parse(sessionStorage.getItem(key(user,project))??"null");
  if(value?.user_id!==user||value?.project_id!==project||![value?.request_id,value?.confirmation_token,value?.reason].every(v=>typeof v==="string"&&v.length>0))return null;
  return value;
 } catch{return null;}
}
export function savePendingRestore(value:PendingArchiveRestore) {
 if(typeof window!=="undefined")sessionStorage.setItem(key(value.user_id,value.project_id),JSON.stringify(value));
}
export function removePendingRestore(user:string|undefined,project:string,requestId?:string) {
 if(typeof window!=="undefined"&&user&&(!requestId||readPendingRestore(user,project)?.request_id===requestId))sessionStorage.removeItem(key(user,project));
}
export function retainRestoreAttemptsForUser(user?:string) {
 if(typeof window==="undefined")return;
 for(let i=sessionStorage.length-1;i>=0;i--) {
  const name=sessionStorage.key(i);
  for(const namespace of [prefix,draftPrefix]) {
   if(name?.startsWith(namespace)&&(!user||!name.startsWith(`${namespace}${user}:`)))sessionStorage.removeItem(name);
  }
 }
}

// An unsent draft contains no confirmation token or request identity. It is
// retained only when following a remediation link, separately from sent work.
const draftPrefix="velora:archive-restore-draft:";
const draftKey=(user:string,project:string)=>`${draftPrefix}${user}:${project}`;
export function readRestoreDraft(user:string|undefined,project:string):string {
 if(typeof window==="undefined"||!user)return "";
 try {
  const value=JSON.parse(sessionStorage.getItem(draftKey(user,project))??"null");
  return value?.user_id===user&&value?.project_id===project&&typeof value?.reason==="string"?value.reason:"";
 } catch{return "";}
}
export function saveRestoreDraft(user:string|undefined,project:string,reason:string) {
 if(typeof window!=="undefined"&&user)sessionStorage.setItem(draftKey(user,project),JSON.stringify({user_id:user,project_id:project,reason}));
}
export function removeRestoreDraft(user:string|undefined,project:string) {
 if(typeof window!=="undefined"&&user)sessionStorage.removeItem(draftKey(user,project));
}
