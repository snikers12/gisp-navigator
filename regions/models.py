import datetime
import pytz
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from djchoices import DjangoChoices, ChoiceItem
"""

https://ru.wikipedia.org/wiki/Таблица_административных_единиц_по_странам#.D0.A0
https://kladr-rf.ru
http://www.gosspravka.ru/Adresa/regions.html

"""


class FederalSubjectType(models.Model):
    """Тип федерального субъекта"""
    # https://en.wikipedia.org/wiki/Federal_subjects_of_Russia#Terminology
    # 6 штук
    full_name = models.CharField('Полное название', max_length=30, unique=True)
    short_name = models.CharField('Сокращенное название', max_length=5, unique=True)

    class Meta:
        verbose_name = "Тип федерального субъекта"
        verbose_name_plural = "Типы федеральных субъектов"

    def __str__(self):
        return self.full_name


class FederalSubjectManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            deleted=False
        ).select_related('federal_subject_type', 'district')


class FederalSubjectAdminManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('federal_subject_type', 'district')


class FederalSubject(models.Model):  # states in PHP
    """Республики и области"""
    # https://en.wikipedia.org/wiki/Federal_subjects_of_Russia
    # https://ru.wikipedia.org/wiki/Субъекты_Российской_Федерации
    # https://kladr-api.ru/
    # https://dadata.ru/
    # 86 штук

    class TypePosition(DjangoChoices):
        prefix = ChoiceItem('prefix', 'В начале')  # "Республика Татарстан"
        suffix = ChoiceItem('suffix', 'В конце')  # "Удмуртская республика"
        omit = ChoiceItem('omit', 'Не используется')  # "Ханты-Мансийский Автономный округ - Югра"

    name = models.CharField('Название', max_length=50, unique=True)
    system_name = models.CharField('Полное название', max_length=100, blank=True)
    federal_subject_type = models.ForeignKey(FederalSubjectType, on_delete=models.PROTECT,
                                             verbose_name=FederalSubjectType._meta.verbose_name)

    kladr_id = models.CharField('Код КЛАДР', max_length=13, unique=True)
    # (Тимур): на эти почтовые адреса отправляются выгрузки участников конкурса экселевские.
    email = models.EmailField('Почтовый адрес')  # ad16@добровольцыроссии.рф - Татарстан

    federal_subject_type_position = models.CharField('Позиция типа субъекта', max_length=6,
                                                     choices=TypePosition.choices)

    # [{timezone: 'Europe/Moscow', title: 'видимое в интерфейсе название: Московское время'}, ...]
    timezones = JSONField('Часовые пояса')
    deleted = models.BooleanField('Удаленно', default=False)
    district = models.ForeignKey('FederalDistrict', on_delete=models.PROTECT,
                                 null=True, blank=True, verbose_name='Федеральный округ',
                                 related_name='regions')
    objects = FederalSubjectManager()
    admin_objects = FederalSubjectAdminManager()

    class Meta:
        verbose_name = "Федеральный субъект"
        verbose_name_plural = "Федеральные субъекты"
        ordering = ["name"]
        indexes = [
            models.Index(fields=['name'], name='regions_fed_name_48125e1_idx'),
        ]

    def __str__(self):
        return self.full_pretty_name

    @property
    def full_pretty_name(self):
        fst = self.federal_subject_type
        if self.federal_subject_type_position == self.TypePosition.omit:
            return self.name

        if self.federal_subject_type_position == self.TypePosition.prefix:
            parts = [fst.full_name.title(), self.name]
        elif self.federal_subject_type_position == self.TypePosition.suffix:
            parts = [self.name, fst.full_name.lower()]
        else:
            raise AssertionError("Unknown federal_subject_type_position")  # pragma: no cover
        return ' '.join(parts)

    @property
    def default_timezone(self) -> datetime.tzinfo:
        return pytz.timezone(self.timezones[0]['timezone'])

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.system_name = self.full_pretty_name
        super().save(force_insert, force_update, using, update_fields)


class FederalSubjectWithPolygon(FederalSubject):
    polygon_location = models.GeometryField()
    center = models.PointField(verbose_name='Точка центра', null=True,
                               help_text='Задайте эту точку явно, если автоматически '
                                         'посчитанное значение отличается от желаемого')

    objects = FederalSubjectManager()

    class Meta:
        verbose_name = "Федеральный субъект с гео"
        verbose_name_plural = "Федеральные субъекты с гео"
        # ordering is inherited from the parent


class FederalDistrict(models.Model):
    name = models.CharField('Название', max_length=255)
    name_short = models.CharField('Сокращенное название', max_length=5)

    class Meta:
        verbose_name = "Федеральный округ"
        verbose_name_plural = "Федеральные округа"

    def __str__(self):
        return self.name
