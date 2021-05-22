from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save

from regions.handlers import reset_region_cache, reset_district_cache


class RegionsConfig(AppConfig):
    name = 'regions'
    verbose_name = 'Регионы'

    def ready(self):
        post_delete.connect(reset_region_cache, sender='regions.FederalSubject')
        post_save.connect(reset_region_cache, sender='regions.FederalSubject')
        post_delete.connect(reset_district_cache, sender='regions.FederalDistrict')
        post_save.connect(reset_district_cache, sender='regions.FederalDistrict')
