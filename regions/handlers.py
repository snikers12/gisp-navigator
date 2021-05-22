from django.core.cache import cache


def reset_region_cache(sender, instance, *args, **kwargs):
    cache.delete_pattern("region-list*")


def reset_district_cache(sender, instance, *args, **kwargs):
    cache.delete_pattern("district-list*")
