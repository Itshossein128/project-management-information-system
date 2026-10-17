"""Confirmed correction of one exact suspend/completion event.

Required audits and durable results are committed with the root-row transition.
This service never invokes approval, finance, baseline or archive restoration.
"""
from uuid import UUID, uuid4
from django.contrib.auth import get_user_model
from django.core import signing
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from rest_framework.exceptions import PermissionDenied
from audit import service as audit_service
from config.exceptions import CodedValidationError, ConflictError
from permissions.project import _is_global_admin, member_has_codename
from projects.models import Project, ProjectStatusUndo
from projects.lifecycle_service import lock_project, save_project, activation_missing, _digest

SALT = 'projects.status-undo.v1'
OPERATIONS = {'resume','undo_completion'}
CONTEXT_KEYS = {'project_id','actor_id','operation','source_event_id','from_status','to_status','lifecycle_version','snapshot_hash'}


def require_authority(user, project_id, operation):
    fresh = get_user_model().objects.filter(pk=getattr(user,'pk',None),is_active=True).first()
    if not fresh or (operation == 'undo_completion' and not _is_global_admin(fresh)) or (operation in ('resume','history') and not member_has_codename(fresh,project_id,'view_project' if operation=='history' else 'edit_project')):
        raise PermissionDenied(_('You no longer have permission for this project action. Contact a system administrator.'))
    if operation not in OPERATIONS | {'history'}:
        invalid()
    return fresh


def current_data(project):
    return {'project_id':str(project.pk),'project_name':project.project_name,'status':project.status,
            'lifecycle_version':project.lifecycle_version,'suspension_event_id':str(project.suspension_event_id) if project.suspension_event_id else None,
            'completion_event_id':str(project.completion_event_id) if project.completion_event_id else None,
            'completed_from_status':project.completed_from_status,'archive_cycle_id':str(project.archive_cycle_id) if project.archive_cycle_id else None}


def conflict(project, code='status_undo_context_changed', source_id=None):
    details={'detail':_('The project changed. Review its current state and confirm again.'),'current_project':current_data(project)}
    if source_id:details['source_event_id']=str(source_id)
    raise ConflictError(details,code=code)


def invalid():
    raise CodedValidationError({'detail':_('Invalid status correction request. Open a new preview and confirm again.')},code='invalid_status_undo_request')


def _validate_event(project, event, kind):
    if event is None or event.project_id!=project.pk:
        conflict(project)
    data=event.changes
    target='suspended' if kind=='suspend' else 'completed'
    allowed={'active'} if kind=='suspend' else {'active','suspended'}
    if not isinstance(data,dict) or data.get('schema_version')!=1 or data.get('event')!=f'project.{target}' or data.get('from_status') not in allowed or data.get('to_status')!=target:
        conflict(project)
    before,after=data.get('version_before'),data.get('version_after')
    if type(before) is not int or type(after) is not int or before<0 or after!=before+1 or after>project.lifecycle_version:
        conflict(project)
    if not isinstance(data.get('actor'),dict) or not isinstance(data.get('project'),dict) or data['project'].get('id')!=str(project.pk):
        conflict(project)
    return data


def source_context(project, operation):
    expected='suspended' if operation=='resume' else 'completed'
    if project.status!=expected:conflict(project)
    event=project.suspension_event if operation=='resume' else project.completion_event
    data=_validate_event(project,event,'suspend' if operation=='resume' else 'complete')
    target='active' if operation=='resume' else project.completed_from_status
    if target not in ('active','suspended') or operation=='undo_completion' and target!=data['from_status']:
        conflict(project)
    if operation=='undo_completion' and target=='suspended':
        suspension=project.suspension_event
        _validate_event(project,suspension,'suspend')
        if data.get('suspension_event_id')!=str(suspension.pk) or ProjectStatusUndo.objects.filter(project=project,operation='resume',source_audit_log=suspension).exists():
            conflict(project)
    return event,target


def _context(project,user,operation,event,target):
    snapshot={**current_data(project),'archived_from_status':project.archived_from_status,
              'manager':str(project.project_manager_id) if project.project_manager_id else None,
              'scope':(project.scope_description or '').strip(),
              'amount':str(project.contract_amount.normalize()) if project.contract_amount is not None else None}
    return {'project_id':str(project.pk),'actor_id':str(user.pk),'operation':operation,'source_event_id':str(event.pk),
            'from_status':project.status,'to_status':target,'lifecycle_version':project.lifecycle_version,'snapshot_hash':_digest(snapshot)}


def remediation(project,user,operation,missing):
    from projects.change_request_service import OPEN_STATUSES
    can_edit=member_has_codename(user,project.pk,'edit_project')
    can_create=can_edit and project.status in ('active','suspended')
    if project.status=='completed':can_create=_is_global_admin(user) and project.completed_from_status=='active'
    can_create=bool(can_create and not project.change_requests.filter(is_deleted=False,status__in=OPEN_STATUSES).exists())
    return [{'field':field,'action':'project_settings' if field=='project_manager' else 'project_change_request',
             'can_perform':can_edit if field=='project_manager' else can_create} for field in missing]


def preview(project,user,operation):
    user=require_authority(user,getattr(project,'pk',project),operation)
    project=get_object_or_404(Project,pk=getattr(project,'pk',project))
    event,target=source_context(project,operation)
    missing=activation_missing(project) if target=='active' else []
    return {**current_data(project),'operation':operation,'source_event_id':str(event.pk),
            'from_status':project.status,'to_status':target,'confirmation_token':signing.dumps(_context(project,user,operation,event,target),salt=SALT),
            'can_confirm':not missing,'missing':missing,'remediation':remediation(project,user,operation,missing)}


def _source_data(event):
    data=event.changes
    return {'id':str(event.pk),'kind':'suspend' if data['event']=='project.suspended' else 'complete',
            'from_status':data['from_status'],'to_status':data['to_status'],'occurred_at':event.created_at.isoformat(),
            'actor':{'id':data['actor'].get('id'),'display_name':data['actor'].get('display_name','')},
            'project_name':data['project'].get('project_name','')}


def receipt_data(receipt):
    # Durable snapshots may gain internal fields; all public surfaces stay fixed.
    actor = {key: receipt.actor_snapshot.get(key) for key in ('id','display_name')}
    source = {key: receipt.source_snapshot.get(key) for key in ('kind','from_status','to_status','occurred_at','project_name')}
    source['id'] = str(receipt.source_audit_log_id)
    source['actor'] = {key: receipt.source_snapshot.get('actor', {}).get(key) for key in ('id','display_name')}
    return {'id':str(receipt.pk),'project_id':str(receipt.project_id),'project_name':receipt.project_snapshot['project_name'],
            'operation':receipt.operation,'source_event_id':str(receipt.source_audit_log_id),'request_id':str(receipt.request_id),
            'actor':actor,'performed_at':receipt.performed_at.isoformat(),'reason':receipt.reason,
            'from_status':receipt.from_status,'to_status':receipt.to_status,'source_event':source}


@transaction.atomic
def undo(project,user,operation,*,request_id,confirmation_token,reason):
    user=require_authority(user,getattr(project,'pk',project),operation)
    project=lock_project(project)
    user=require_authority(user,project.pk,operation)
    if not isinstance(reason,str) or not reason.strip():
        raise CodedValidationError({'detail':_('Enter a reason for this status correction.'),'fields':{'reason':_('A reason is required.')}},code='reason_required')
    reason=reason.strip()
    try:
        request_id=UUID(str(request_id))
        context=signing.loads(confirmation_token,salt=SALT)
        if not isinstance(context,dict) or set(context)!=CONTEXT_KEYS:raise ValueError
        if context['project_id']!=str(project.pk) or context['actor_id']!=str(user.pk) or context['operation']!=operation:
            raise PermissionDenied(_('This confirmation belongs to another user, project or action. Open your own preview.'))
        source_id=UUID(str(context['source_event_id']))
        if type(context['lifecycle_version']) is not int or context['lifecycle_version']<0 or not isinstance(context['snapshot_hash'],str) or len(context['snapshot_hash'])!=64:raise ValueError
        expected_from='suspended' if operation=='resume' else 'completed'
        if context['from_status']!=expected_from or context['to_status'] not in ({'active'} if operation=='resume' else {'active','suspended'}):raise ValueError
    except (signing.BadSignature,ValueError,TypeError,KeyError):invalid()
    fingerprint=_digest({'context':context,'reason':reason})
    previous=ProjectStatusUndo.objects.filter(project=project,request_id=request_id).first()
    if previous:
        if previous.operation!=operation or previous.request_fingerprint!=fingerprint:conflict(project,'status_undo_request_conflict')
        return {'outcome':'replayed','receipt':receipt_data(previous),'current_project':current_data(project)}
    if ProjectStatusUndo.objects.filter(project=project,operation=operation,source_audit_log_id=source_id).exists():
        conflict(project,'status_undo_already_applied',source_id)
    event,target=source_context(project,operation)
    if context!=_context(project,user,operation,event,target):conflict(project)
    missing=activation_missing(project) if target=='active' else []
    if missing:
        raise CodedValidationError({'detail':_('Complete all missing activation information, then review and confirm again.'),'missing':missing,
                                    'remediation':remediation(project,user,operation,missing)},code='activation_gates_failed')
    receipt_id=uuid4();source=_source_data(event)
    actor_snapshot={'id':str(user.pk),'display_name':user.full_name or user.username}
    project_snapshot={'id':str(project.pk),'project_code':project.project_code,'project_name':project.project_name}
    before=project.status;project.status=target;save_project(project,['status'])
    audit=audit_service.persist_audit_log({'actor_id':str(user.pk),'project_id':str(project.pk),'http_method':'POST',
        'path':f'/api/v1/projects/{project.pk}/{"resume" if operation=="resume" else "undo-completion"}/','resource_type':'project','resource_id':str(project.pk),
        'changes':{'schema_version':1,'event':'project.resumed' if operation=='resume' else 'project.completion_undone','receipt_id':str(receipt_id),
                   'request_id':str(request_id),'source_event_id':str(event.pk),'actor':actor_snapshot,'project':project_snapshot,'reason':reason,
                   'from_status':before,'to_status':target,'version_before':context['lifecycle_version'],'version_after':project.lifecycle_version}})
    receipt=ProjectStatusUndo.objects.create(id=receipt_id,project=project,operation=operation,source_audit_log=event,source_snapshot=source,
        request_id=request_id,request_fingerprint=fingerprint,confirmation_version=context['lifecycle_version'],actor=user,actor_snapshot=actor_snapshot,
        project_snapshot=project_snapshot,reason=reason,from_status=before,to_status=target,performed_at=audit.created_at,audit_log=audit)
    return {'outcome':'applied','receipt':receipt_data(receipt),'current_project':current_data(project)}
