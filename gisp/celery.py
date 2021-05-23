import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gisp.settings")

from django.conf import settings  # noqa

app = Celery('gisp')

# (Kostya): Don't use the `Celery.on_configure` method implementation for connecting Sentry
# as suggested in Sentry docs https://docs.sentry.io/clients/python/integrations/celery/ .
# With that, tests are mysteriously failing with celery.exceptions.NotRegistered exception.

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
