import type { StatusUndoOperation, StatusUndoPayload } from "./api/projects";
const draftPrefix="velora:status-undo-draft:";
const pendingPrefix="velora:status-undo-pending:";
const key=(prefix:string,user:string,project:string,operation:StatusUndoOperation)=>`${prefix}${user}:${project}:${operation}`;
export interface PendingStatusUndo extends StatusUndoPayload {user_id:string;project_id:string;operation:StatusUndoOperation;source_event_id:string}
export function readPendingStatusUndo(user:string|undefined,project:string,operation:StatusUndoOperation):PendingStatusUndo|null {
 if(typeof window==="undefined"||!user)return null;
 try {const value=JSON.parse(sessionStorage.getItem(key(pendingPrefix,user,project,operation))??"null");return value?.user_id===user&&value?.project_id===project&&value?.operation===operation&&[value?.request_id,value?.confirmation_token,value?.reason,value?.source_event_id].every(v=>typeof v==="string"&&v.length>0)?value:null;}catch{return null;}
}
export function savePendingStatusUndo(value:PendingStatusUndo) {if(typeof window!=="undefined")sessionStorage.setItem(key(pendingPrefix,value.user_id,value.project_id,value.operation),JSON.stringify(value));}
export function removePendingStatusUndo(user:string|undefined,project:string,operation:StatusUndoOperation,requestId:string) {
 if(typeof window!=="undefined"&&user&&readPendingStatusUndo(user,project,operation)?.request_id===requestId)sessionStorage.removeItem(key(pendingPrefix,user,project,operation));
}
export function readStatusUndoDraft(user:string|undefined,project:string,operation:StatusUndoOperation):string {
 if(typeof window==="undefined"||!user)return "";
 try {const value=JSON.parse(sessionStorage.getItem(key(draftPrefix,user,project,operation))??"null");return value?.user_id===user&&value?.project_id===project&&value?.operation===operation&&typeof value.reason==="string"?value.reason:"";}catch{return "";}
}
export function saveStatusUndoDraft(user:string|undefined,project:string,operation:StatusUndoOperation,reason:string) {if(typeof window!=="undefined"&&user)sessionStorage.setItem(key(draftPrefix,user,project,operation),JSON.stringify({user_id:user,project_id:project,operation,reason}));}
export function removeStatusUndoDraft(user:string|undefined,project:string,operation:StatusUndoOperation) {if(typeof window!=="undefined"&&user)sessionStorage.removeItem(key(draftPrefix,user,project,operation));}
export function retainStatusUndoStateForUser(user?:string) {
 if(typeof window==="undefined")return;
 for(let index=sessionStorage.length-1;index>=0;index--){const name=sessionStorage.key(index);for(const prefix of [draftPrefix,pendingPrefix])if(name?.startsWith(prefix)&&(!user||!name.startsWith(`${prefix}${user}:`)))sessionStorage.removeItem(name);}
}
