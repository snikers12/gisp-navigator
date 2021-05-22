import json

import os
from django.contrib.postgres.forms.jsonb import InvalidJSONInput
from django.contrib.postgres import forms
from django.contrib.postgres import fields as pg_fields
from uploads.models import FileUpload


class ReadableJSONFormField(forms.JSONField):
    def prepare_value(self, value):
        if isinstance(value, InvalidJSONInput):
            return value
        return json.dumps(value, ensure_ascii=False, indent=4)


def pluralize(n, text):
    if n % 10 == 1 and n % 100 != 11:
        index = 0
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        index = 1
    else:
        index = 2

    return str(n) + ' ' + text[index]


def _get_file(file_field):
    return os.path.basename(file_field.file.name), file_field.file


def _get_partner_files(instance, ):
    for partner in getattr(instance, 'project_partners').all():
        for index, file_filed in enumerate(partner.support_messages.all()):
            name, file = _get_file(file_filed)
            filename = os.path.join(partner.name, f'{index}_{name}')
            yield filename, file


def get_files_from_fields(instance, fields):
    for field in fields:
        model_field = instance._meta.get_field(field)
        if model_field.many_to_many:
            if field == 'project_partners':
                for name, file in _get_partner_files(instance):
                    yield os.path.join(model_field.verbose_name, name), file
            else:
                for file_filed in getattr(instance, field).all():
                    name, file = _get_file(file_filed)
                    yield os.path.join(model_field.verbose_name, name), file
        elif type(model_field) == pg_fields.JSONField:
            file_filed = getattr(instance, field, None)
            if type(file_filed) == dict:
                for uploaded in FileUpload.objects.filter(
                    id__in=instance.extra_appendices.values()
                ):
                    name, file = _get_file(uploaded)
                    yield os.path.join(model_field.verbose_name, name), file
        else:
            file_filed = getattr(instance, field, None)
            if file_filed:
                name, file = _get_file(file_filed)
                yield os.path.join(model_field.verbose_name, name), file
