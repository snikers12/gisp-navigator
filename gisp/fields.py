import re

import idna
from django.db.models import CharField

from gisp.validators import WeakURLValidator


class WeakURLDescriptor:
    def __init__(self, field):
        self.field = field

    def __get__(self, instance=None, owner=None):
        if instance is None:
            raise AttributeError(
                "The '%s' attribute can only be accessed from %s instances."
                % (self.field.name, owner.__name__))
        return instance.__dict__[self.field.name]

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = self.field.clean_url(value)


class WeakURLField(CharField):
    default_validators = [WeakURLValidator()]
    description = "URL"
    descriptor_class = WeakURLDescriptor
    idna_url_regex = re.compile(r'^https?://([^:/]+)(:[0-9]+)?(/.*)?$', flags=re.IGNORECASE)

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 200)
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, *args, **kwargs):
        super().contribute_to_class(cls, name, *args, **kwargs)
        setattr(cls, self.name, self.descriptor_class(self))

    def clean_url(self, url):
        """Replace IDNA/Punycode-encoded hostname with a human-readable one"""
        if not url:
            return url

        def repl(matchobj):
            url = matchobj.group(0)
            hostname = matchobj.group(1)
            return url.replace(hostname, idna.decode(hostname), 1)

        try:
            return self.idna_url_regex.sub(repl, url)
        except (idna.core.IDNAError, ValueError):
            return url
