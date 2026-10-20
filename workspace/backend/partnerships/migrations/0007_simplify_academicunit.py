from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("partnerships", "0006_academicunit_organizationacademicunit_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="academicunit",
            name="category",
        ),
        migrations.RemoveField(
            model_name="academicunit",
            name="parent",
        ),
        migrations.AlterModelOptions(
            name="academicunit",
            options={
                "ordering": ["-is_active", "name"],
                "verbose_name": "Direction",
                "verbose_name_plural": "Directions",
            },
        ),
    ]
