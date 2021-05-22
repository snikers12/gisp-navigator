import shutil
import signal
import tempfile
import os

from .settings_common import *  # noqa

SECRET_KEY = 'fake'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('GISP_POSTGRES_NAME', 'gisp'),  # will be prefixed with `test_` automatically  # noqa
        'USER': os.environ['GISP_POSTGRES_USER'],
        'PASSWORD': os.environ['GISP_POSTGRES_PASSWORD'],
        'HOST': os.environ['GISP_POSTGRES_HOST'],
    }
}

CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'

# https://docs.djangoproject.com/en/dev/topics/email/#in-memory-backend
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Django channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
        "CONFIG": {},
    },
}

try:
    del STATICFILES_STORAGE  # use DEFAULT_FILE_STORAGE  # noqa
except NameError:
    pass
MEDIA_ROOT = tempfile.mkdtemp()
MEDIA_URL = 'http://testserver/media/'


def signal_handler():
    shutil.rmtree(MEDIA_ROOT, ignore_errors=True)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

MOMMY_CUSTOM_FIELDS_GEN = {
}
