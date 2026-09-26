from django.db import migrations


def create_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for name in ("Partnership Editors", "Partnership Viewers"):
        Group.objects.get_or_create(name=name)


def remove_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=("Partnership Editors", "Partnership Viewers")).delete()


class Migration(migrations.Migration):
    dependencies = [("partnerships", "0003_alter_document_uploaded_at")]
    operations = [migrations.RunPython(create_groups, remove_groups)]
