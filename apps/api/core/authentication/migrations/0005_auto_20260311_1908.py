from django.db import migrations

def apply_roles_automatically(apps, schema_editor):
    # این کد دقیقاً جایگزین کار دستی شماست
    Group = apps.get_model('auth', 'Group')
    
    # اضافه کردن نقش جدید
    Group.objects.get_or_create(name='hr')
    Group.objects.get_or_create(name='site_engineer')
    
    # حذف نقش اشتباه
    Group.objects.filter(name='root').delete()

def revert_roles(apps, schema_editor):
    # کدی برای زمانی که بخواهید مایگریشن را برگردانید (Undo)
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['hr', 'site_engineer']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_add_business_setup_group'),
    ]

    operations = [
        # اینجا به جنگو دستور می‌دهیم کدهای ما را اجرا کند
        migrations.RunPython(apply_roles_automatically, revert_roles),
    ]
