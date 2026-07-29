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

def bulk_create_relations(relations_to_create, wbs_count, activity_count, relation_count, warnings, progress_callback):
    """
    Bulk create relations and return the summary dictionary.
    This logic is shared between msp_import and p6_import.
    """
    ActivityRelation.objects.bulk_create(relations_to_create, ignore_conflicts=True)

    if progress_callback:
        progress_callback(100)

    return {
        'wbs_nodes_created': wbs_count,
        'activities_created': activity_count,
        'relations_created': relation_count,
        'warnings': warnings,
    }
