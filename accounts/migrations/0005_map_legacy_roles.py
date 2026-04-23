from django.db import migrations


LEGACY_TO_NEW_ROLE_MAP = {
    'admin': 'vrs',
    'supervisor': 'dae',
    'staff': 'technical_operator',
    'career_director': 'dc',
    'career_coordinator': 'cc',
    'read_only': 'subdirector',
}


def map_legacy_roles(apps, schema_editor):
    UserProfile = apps.get_model('accounts', 'UserProfile')
    for legacy_role, new_role in LEGACY_TO_NEW_ROLE_MAP.items():
        UserProfile.objects.filter(role=legacy_role).update(role=new_role)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_userprofile_role'),
    ]

    operations = [
        migrations.RunPython(map_legacy_roles, migrations.RunPython.noop),
    ]
