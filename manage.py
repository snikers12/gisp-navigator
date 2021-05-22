#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    default_settings = ('gisp.settings_test'
                        if len(sys.argv) > 1 and
                           sys.argv[1] in ('test', 'makemessages')
                        else 'gisp.settings')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", default_settings)

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
