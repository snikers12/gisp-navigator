from django.core.management.base import BaseCommand
from django.db import transaction

from regions.models import FederalSubject


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        for region in FederalSubject.objects.all():
            region.save()
