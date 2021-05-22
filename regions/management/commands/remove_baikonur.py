from django.core.management.base import BaseCommand
from django.db import transaction

from contest_dobr.models import Dobr2018Application, Dobr2018Project
from projects.models import Project
from regions.models import FederalSubject


class Command(BaseCommand):
    help = 'Удаление Байконура'

    region_id = 12

    @transaction.atomic
    def handle(self, *args, **options):
        related_fields = [
            f for f in FederalSubject._meta.get_fields()
            if (f.one_to_many) and f.auto_created and not f.concrete
        ]

        for field in related_fields:
            try:
                field.related_model.objects.filter(
                    **{field.field.name: self.region_id}
                ).update(
                    **{field.field.name: None}
                )
            except Exception as e:
                print(e)

        apps = Dobr2018Application.objects.filter(project__main_region=self.region_id)

        Dobr2018Application.objects.filter(resent_application__in=apps).delete()
        deleted = apps.delete()
        print(f'delete Dobr2018Application: {deleted}')

        deleted = Dobr2018Project.objects.filter(
            original_project__main_region=self.region_id
        ).delete()
        print(f'delete Dobr2018Project: {deleted}')

        deleted = Project.objects.filter(main_region=self.region_id).delete()
        print(f'delete Project: {deleted}')
