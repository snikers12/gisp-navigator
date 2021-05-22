import waffle
from django.conf import settings

default_app_config = 'waffle_protected_drf.apps.WaffleProtectedDrfConfig'

# Don't change these - migrations use them directly.
FLAG_NAME = 'allow_drf_browsable_api'
GROUP_NAME = 'Allow DRF Browsable API'


def is_drf_browsable_api_allowed(request):
    assert not waffle.get_setting('OVERRIDE'), \
        "Waffle OVERRIDE setting is turned ON. You must disable it, because it would allow " \
        "accessing DRF Browsable API for anyone by setting a specific GET query param. " \
        "See http://waffle.readthedocs.io/en/stable/starting/configuring.html"
    return settings.DEBUG or waffle.flag_is_active(request, FLAG_NAME)
