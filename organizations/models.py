from django.db import models


# class WinnerOrganization(models.Model):
#     class Meta:
#         verbose_name = 'Победитель'
#         verbose_name_plural = 'Победители'
#
#     ogrn = models.CharField(verbose_name='ОГРН', max_length=255, blank=True, null=True)
#     inn = models.CharField(verbose_name='ИНН', max_length=255, blank=True, null=True)
#     ids_support_measures = ArrayField(base_field=models.IntegerField(), blank=True, null=True)
#     summ = models.FloatField(verbose_name='Сумма', blank=True, null=True)
#     date_recieved = models.DateField(verbose_name='Дата получения', blank=True, null=True)
#     region_code = models.IntegerField(blank=True, null=True)
#     region_name = models.CharField(max_length=255, blank=True, null=True)
#
#     def __str__(self):
#         return self.ogrn
from djchoices import DjangoChoices, ChoiceItem


class SpravkaMixin(models.Model):
    class Meta:
        abstract = True

    code = models.CharField('Код', max_length=1000)
    name = models.CharField('Название', max_length=5000)

    def __str__(self):
        return self.name


class Okved(SpravkaMixin):
    class Meta:
        verbose_name = 'ОКВЭД'
        verbose_name_plural = 'ОКВЭД'


class Tass(SpravkaMixin):
    class Meta:
        verbose_name = 'ТАСС'
        verbose_name_plural = 'ТАСС'


class Branch(SpravkaMixin):
    class Meta:
        verbose_name = 'Отрасль'
        verbose_name_plural = 'Отрасли'


class Department(SpravkaMixin):
    class Meta:
        verbose_name = 'Департамент'
        verbose_name_plural = 'Департаменты'


class Region(models.Model):
    region_name = models.CharField('Назване региона', max_length=255)
    region_code = models.CharField('Код региона', max_length=255)

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'


class OrganizationSize(models.Model):
    name = models.CharField('Размер', max_length=32)
    # Малая (1-100 чел.), Средняя(101-250 чел.), Крупная(251+ чел.)

    class Meta:
        verbose_name = 'Размер организаций'
        verbose_name_plural = 'Размеры организаций'

    def __str__(self):
        return self.name


class SupportMeasuresTypes(DjangoChoices):
    financial = ChoiceItem('fin', 'Финансовая поддержка')
    property = ChoiceItem('prop', 'Имущественная поддержка')
    consulting = ChoiceItem('cons', 'Консультационная (информационная) поддержка')
    educational = ChoiceItem('edu', 'Образовательная поддержка')
    support = ChoiceItem('sup', 'Поддержка внешнеэкономической деятельности')
    regulator = ChoiceItem(
        'reg', 'Регуляторная поддержка (налоговые, таможенные, инвестиционные льготы и т.д.)'
    )


class Organization(models.Model):
    is_active = models.BooleanField('Активна?', default=False)
    ogrn = models.CharField('ОРГН', max_length=255, blank=True, null=True)
    inn = models.CharField('ИНН', max_length=255, null=True, blank=True)
    region = models.ForeignKey(Region, verbose_name='Регион', on_delete=models.PROTECT,
                               related_name='organizations', blank=True, null=True)
    okveds = models.ManyToManyField(Okved, verbose_name='ОКВЭДы', blank=True)
    branch = models.ManyToManyField(Branch, verbose_name='Отрасль', blank=True)
    size = models.ForeignKey(OrganizationSize, verbose_name='Размер организации',
                             related_name='organizations', on_delete=models.PROTECT, blank=True,
                             null=True)
    tasses = models.ManyToManyField(Tass, verbose_name='ТАСС', blank=True)
    found_date = models.DateField('Дата основания', blank=True, null=True)

    eshn = models.BooleanField('Признак ЕСХН', default=0)
    srp = models.BooleanField('Признак СРП', default=0)
    envd = models.BooleanField('Признак ЕНВД', default=0)
    usn = models.BooleanField('Признак УСН', default=0)

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'

    def __str__(self):
        return self.inn


class SupportMeasures(models.Model):
    departments = models.ManyToManyField(Department, verbose_name='Департаменты', blank=True)
    kbk = models.CharField('КБК', max_length=255, blank=True, null=True)
    name = models.CharField('Название', max_length=5000, blank=True, null=True)
    is_active = models.BooleanField('Активна?', default=False)
    region = models.ForeignKey(Region, verbose_name='Регион', on_delete=models.PROTECT,
                               related_name='support_measures', blank=True, null=True)
    is_federal = models.BooleanField('Федеральный бюджет?', default=True)
    okveds = models.ManyToManyField(Okved, verbose_name='ОКВЭДЫ', blank=True)
    branch = models.ManyToManyField(Branch, verbose_name='Отрасль', blank=True)
    sizes = models.ManyToManyField(OrganizationSize, verbose_name='Размеры организаций', blank=True)
    support_type = models.CharField('Тип поддержки', choices=SupportMeasuresTypes.choices,
                                    max_length=4, default=SupportMeasuresTypes.financial)

    def __str__(self):
        return self.name


class Subsidies(models.Model):
    class Meta:
        verbose_name = 'Субсидия'
        verbose_name_plural = 'Субсидии'

    organization = models.ForeignKey(Organization, related_name='subsidies',
                                     verbose_name='Организация', on_delete=models.PROTECT)
    sum = models.FloatField(verbose_name='Сумма', blank=True, null=True)
    date_received = models.DateField('Дата получения', null=True, blank=True)
    support_measure = models.ForeignKey(SupportMeasures, related_name='subsidies', blank=True,
                                        null=True, verbose_name='Тип поддержки',
                                        on_delete=models.PROTECT)

    def __str__(self):
        return f'Субсидия организации {self.organization.id}'
