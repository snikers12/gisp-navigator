from django.core import validators
from django.utils.deconstruct import deconstructible


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r'^[\w.,!?@+_\'"|/&№«»„“)(–↔ -]+$'
    message = 'Имя содержит недопустимые символы'
