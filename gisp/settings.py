import os
from .settings_common import *  # noqa

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['GISP_SECRET_KEY']

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ['GISP_POSTGRES_NAME'],
        'USER': os.environ['GISP_POSTGRES_USER'],
        'PASSWORD': os.environ['GISP_POSTGRES_PASSWORD'],
        'HOST': os.environ['GISP_POSTGRES_HOST'],
    }
}

DJANGO_REDIS_IGNORE_EXCEPTIONS = True  # silently tolerate non-responding redis
DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True

CACHES = {
    'default': {
        'TIMEOUT': 10,  # seconds
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ['GISP_REDIS_DEFAULT_CACHE_URL'],
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

CELERY_BROKER_URL = os.environ['GISP_CELERY_BROKER_URL']
CELERY_RESULT_BACKEND = os.environ['GISP_CELERY_RESULT_BACKEND']

if DEBUG:  # noqa: F405
    INSTALLED_APPS += (  # noqa: F405
        'debug_toolbar',
    )

    MIDDLEWARE += (  # noqa: F405
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK':
            'gisp.settings_common.custom_show_toolbar',
    }
