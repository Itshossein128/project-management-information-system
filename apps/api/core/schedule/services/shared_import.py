from projects.models import Activity, ActivityRelation

def extract_activities_from_tasks(tasks, project, existing_activities, uid_to_activity, outline_to_wbs, warnings, audit_user, done, activity_count, get_wbs_func):
    """
    Extract activities from tasks, bulk create them and update maps.
    This logic is shared between msp_import and p6_import.
    """
    activities_to_create = []
    task_uid_to_activity_index = {}

    for task in tasks:
        if task.is_summary:
            continue
        wbs = get_wbs_func(task, outline_to_wbs, warnings)
        if wbs is None:
            continue

        code = task.wbs_code or task.uid
        if code in existing_activities:
            warnings.append(f'Duplicate activity code "{code}" — skipped.')
            continue

        activities_to_create.append(Activity(
            project=project,
            wbs=wbs,
            activity_code=code,
            activity_name=task.name,
            planned_start=task.start,
            planned_finish=task.finish,
            actual_start=getattr(task, 'actual_start', None),
            actual_finish=getattr(task, 'actual_finish', None),
            duration_days=task.duration_days,
            is_milestone=bool(getattr(task, 'is_milestone', False)),
            planned_percent=None if getattr(task, 'percent_invalid', False) else getattr(task, 'percent_complete', None),
            is_critical=task.is_critical if getattr(task, 'critical_known', False) else None,
            total_slack_days=getattr(task, 'total_slack_days', None),
            free_slack_days=getattr(task, 'free_slack_days', None),
            created_by=audit_user,
            updated_by=audit_user,
        ))
        task_uid_to_activity_index[task.uid] = len(activities_to_create) - 1
        existing_activities.add(code)
        activity_count += 1
        done += 1

    created_activities = Activity.objects.bulk_create(activities_to_create)
    for task_uid, index in task_uid_to_activity_index.items():
        uid_to_activity[task_uid] = created_activities[index]

    return done, activity_count

def bulk_create_relations(relations_to_create, wbs_count, activity_count, warnings, progress_callback):
    """
    Insert relationships that are not already active and return the stored counts.
    """
    existing = set(
        ActivityRelation.objects.filter(is_deleted=False).values_list('predecessor_id', 'successor_id')
    )
    to_create = []
    relation_warning_items = []
    for relation in relations_to_create:
        key = (relation.predecessor_id, relation.successor_id)
        if key in existing:
            code = getattr(relation.successor, 'activity_code', None) or str(relation.successor_id)
            relation_warning_items.append({'code': 'duplicate_relation', 'row': str(code)})
            continue
        existing.add(key)
        to_create.append(relation)
    if to_create:
        ActivityRelation.objects.bulk_create(to_create)

    if progress_callback:
        progress_callback(100)

    return {
        'wbs_nodes_created': wbs_count,
        'activities_created': activity_count,
        'relations_created': len(to_create),
        'warnings': warnings,
        'relation_warning_items': relation_warning_items,
    }
