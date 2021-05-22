# daphne.server must be imported before raven (which is imported
# in .celery).
#
# Otherwise you'd get a warning:
# > Something has already installed a non-asyncio Twisted reactor.
# > Attempting to uninstall it...
import daphne.server  # noqa

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.

__all__ = []
