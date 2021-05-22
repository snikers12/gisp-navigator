from django.db import migrations

REGION_ID = 34


def forwards_func(apps, schema_editor):
    FederalSubject = apps.get_model("regions", "FederalSubject")
    FederalSubject.objects.filter(id=REGION_ID).update(
        name='Кемеровская область - Кузбасс',
        federal_subject_type_position='omit'
    )


def reverse_func(apps, schema_editor):
    FederalSubject = apps.get_model("regions", "FederalSubject")
    FederalSubject.objects.filter(id=REGION_ID).update(
        name='Кемеровская',
        federal_subject_type_position='suffix'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('regions', '0013_auto_20190228_1520'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
