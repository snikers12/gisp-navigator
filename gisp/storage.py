from functools import wraps
from time import time

from django.conf import settings
from django.contrib.staticfiles.storage import ManifestFilesMixin
from django.core.exceptions import ImproperlyConfigured
from logging import getLogger

try:
    # (Kostya): This *must* go before the SwiftStorage import. Otherwise python silently crashes.
    import swiftclient
    import swiftclient.exceptions
except ImportError:
    raise ImproperlyConfigured("Could not load swiftclient library")

from swift.storage import SwiftStorage as _SwiftStorage, StaticSwiftStorage as _StaticSwiftStorage

logger = getLogger(__name__)


def retry_on_token_expired(func):
    @wraps(func)
    def f(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except swiftclient.ClientException as e:
            if e.http_status != 401:  # 401 - unauthorized - that is an expired token
                raise

            token_creation_time = self._token_creation_time or 0  # None to int
            current_time = time()
            expired_token_lifetime = current_time - token_creation_time
            logger.error('Refreshing Swift token due to 401 response',
                         exc_info=True,
                         extra=dict(token_creation_time=token_creation_time,
                                    current_time=current_time,
                                    hours_since_token_creation=expired_token_lifetime / 3600))

            expired_token = self.token
            self._token_creation_time = 0
            self.get_token()  # recreates token
            assert self.token != expired_token, 'Swift storage token did not refresh as expected'

            return func(self, *args, **kwargs)  # retry failed operation with the new token

    return f


class _SwiftPatchesMixin:

    # PR: https://github.com/dennisv/django-storage-swift/pull/91
    def _save(self, name, content, *args, **kwargs):
        # Set file position to the beginning.
        # Fixes stuck image uploads with DRF (which keeps position at the end of the file).
        pos = content.tell()
        try:
            content.seek(0)
            return super()._save(name, content, *args, **kwargs)
        finally:
            content.seek(pos)

    def _open(self, *args, **kwargs):
        try:
            return super()._open(*args, **kwargs)
        except IOError:
            raise
        except swiftclient.exceptions.ClientException as e:
            # django.contrib.staticfiles.storage.ManifestFilesMixin#read_manifest
            # When manifest file doesn't exist, the raised error must be an instance of IOError.
            raise IOError(e)

    def __getattribute__(self, name):
        """
        Decorate all methods with `retry_on_token_expired`, which refreshes
        auth token on 401 error from the storage and retries the failed operation.
        """
        value = object.__getattribute__(self, name)  # raises AttributeError
        if callable(value) and not name.startswith('__'):
            func = value.__func__  # value is a bound method. get an unbound function
            wrapped_func = retry_on_token_expired(func)
            return wrapped_func.__get__(self, type(self))  # bind the unbound func
        return value


class SwiftStorage(_SwiftPatchesMixin, _SwiftStorage):
    pass


class StaticSwiftStorage(_SwiftPatchesMixin, _StaticSwiftStorage):
    pass


class ManifestStaticSwiftStorage(ManifestFilesMixin, StaticSwiftStorage):
    # Fall back to non-suffixed file names when staticfiles.json doesn't exist
    # https://docs.djangoproject.com/en/1.11/ref/contrib/staticfiles/#django.contrib.staticfiles.storage.ManifestStaticFilesStorage.manifest_strict  # noqa
    manifest_strict = settings.SWIFT_MANIFEST_STRICT
