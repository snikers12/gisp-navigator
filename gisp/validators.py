import re
import xml.etree.cElementTree as et

from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db.models.fields.files import FieldFile
from django.utils.deconstruct import deconstructible
from django.core import validators
from django.utils.html import strip_tags


@deconstructible
class YoutubeValidator(validators.RegexValidator):
    regex = r'^https?://(youtu\.be/[^/#]+|(www\.)?youtube\.com/.+)/?$'
    flags = re.IGNORECASE
    message = ('Идентификатор Youtube должен содержать корректный адрес '
               'канала, пользователя или видео')


@deconstructible
class NameValidator(validators.RegexValidator):
    allowed = r'\w.\')( -'
    # [^\W\d] - match \w (alphanum) excluding numbers
    regex = r'^[' + allowed + r']*[^\W\d][' + allowed + r']*$'
    message = 'Поле может содержать только буквы, пробел, точку, апостроф, дефис и скобки'


@deconstructible
class NonSocialURLValidator(validators.RegexValidator):
    social_domains = [
        # caution: these are pasted to a regex w/o any escaping
        'vk.com', 'vkontakte.ru',
        'fb.com', 'fb.me', 'facebook.com',
        'youtube.com', 'youtu.be',
        'twitter.com',
        'ok.ru', 'odnoklassniki.ru',
        'instagram.com', 'instagr.am',
    ]
    inverse_match = True
    regex = r'^[^:]+://([^/]*\.)*(%s)/?' % '|'.join(social_domains)
    flags = re.IGNORECASE
    message = 'Это поле не может содержать ссылки на страницы социальных сетей'


@deconstructible
class WeakURLValidator(validators.URLValidator):
    """
    The're two reasons to override this class:
    1. no way to exclude 'ftp' from allowed schemes
    2. no way to allow '_' in hostnames.

    See: https://code.djangoproject.com/ticket/20264 https://code.djangoproject.com/ticket/18517
    """
    ul = validators.URLValidator.ul
    hostname_re = r'[a-z' + ul + r'0-9_](?:[a-z' + ul + r'0-9_-]{0,61}[a-z' + ul + r'0-9_])?'
    domain_re = r'(?:\.(?!-)[a-z' + ul + r'0-9_-]{1,63}(?<!-))*'
    tld_re = validators.URLValidator.tld_re
    host_re = '(' + hostname_re + domain_re + tld_re + '|localhost)'

    regex = validators._lazy_re_compile(
        r'^(?:[a-z0-9\.\-\+]*)://'  # scheme is validated separately
        r'(?:\S+(?::\S*)?@)?'  # user:pass authentication
        r'(?:' + validators.URLValidator.ipv4_re + '|' + validators.URLValidator.ipv6_re +
        '|' + host_re + ')'
                        r'(?::\d{2,5})?'  # port
                        r'(?:[/?#][^\s]*)?'  # resource path
                        r'\Z', re.IGNORECASE)

    schemes = ['http', 'https']


@deconstructible
class MinLengthValidator(MinLengthValidator):
    def clean(self, x):
        return len(strip_tags(x).replace('&nbsp;', ''))


@deconstructible
class MaxLengthValidator(MaxLengthValidator):
    def clean(self, x):
        return len(strip_tags(x).replace('&nbsp;', ''))


@deconstructible
class RegNumberValidator(validators.RegexValidator):
    regex = r'^\d{13}$|^\d{15}$'
    message = 'ОГРН должен содержать 13 или 15 цифр'


@deconstructible
class InnValidator(validators.RegexValidator):
    regex = r'^\d{10}$|^\d{12}$'
    message = 'ИНН должен содержать 10 или 12 цифр'


@deconstructible
class KppValidator(validators.RegexValidator):
    regex = r'^\d{9}$'
    message = 'КПП должен содержать 9 цифр'


@deconstructible
class PostalCodeValidator(validators.RegexValidator):
    regex = r'^[0-9]{6}$'
    message = 'Почтовый индекс должен содержать ровно 6 цифр'


@deconstructible
class PhoneNumberValidator(validators.RegexValidator):
    regex = r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$'
    message = 'Неверный формат номера телефона'


@deconstructible
class HouseOfficeNumberValidator(validators.RegexValidator):
    regex = r"^[1-9][0-9]*([a-zA-Z]|[а-яА-Я]|(\/[1-9][0-9]*))?$"
    message = 'Неверный номер дома/офиса'


def validate_ogrn(value):
    len_ogrn = len(value)
    if len_ogrn not in (13, 15):
        raise ValidationError('ОГРН должен содержать 13 или 15 цифр')

    def ogrn_csum(ogrn):
        if len_ogrn == 13:
            delimeter = 11
        else:
            delimeter = 13
        return str(int(ogrn[:-1]) % delimeter % 10)

    if ogrn_csum(value) == value[-1]:
        return True
    raise ValidationError('Неправильный формат ОГРН')


def validate_inn(value):
    if len(value) not in (10, 12):
        raise ValidationError('ИНН должен содержать 10 или 12 цифр')

    def inn_csum(inn):
        k = (3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8)
        pairs = zip(k[11-len(inn):], [int(x) for x in inn])
        return str(sum([k * v for k, v in pairs]) % 11 % 10)

    if len(value) == 10:
        if value[-1] == inn_csum(value[:-1]):
            return True
        raise ValidationError('Неправильный формат ИНН')
    else:
        if value[-2:] == inn_csum(value[:-2]) + inn_csum(value[:-1]):
            return True
        raise ValidationError('Неправильный формат ИНН')


def validate_kpp(value):
    if len(value) != 9:
        raise ValidationError('КПП может состоять только из 9 знаков (цифр или заглавных букв '
                              'латинского алфавита от A до Z)')
    elif not re.fullmatch(r'[0-9]{4}[0-9A-Z]{2}[0-9]{3}', value):
        raise ValidationError('Неправильный формат КПП')
    return True


def validate_payment_accounts(value):
    if len(value) > 20 or not value.isdigit():
        raise ValidationError('Введите корректные данные')
    return True


def extra_validate(value):
    from contests.models import ContestEvaluationCriteria
    for k, v in value.items():
        obj = ContestEvaluationCriteria.objects.filter(field_name=k).first()
        if not obj:
            raise ValidationError(f'Поля {k} не существует.')
        if v < 0 or v > obj.max_value:
            raise ValidationError(f'Оценка для {k} должна быть от 0 до {obj.max_value}')
    return True
