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

from gisp.models import SingletonModel


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


class OrganizationCorrelation(models.Model):
    # Вот мое предложение реализации чтобы считать и хранить рейтинг.
    # Как запустить
    # docker exec -it gispbackend_web_0_1 ./entrypoint.sh ./manage.py shell
    # from organizations.models import *
    # OrganizationCorrelation.calculate_rating('1327014934', '6453070688')
    # Когда будете получать похожие организации можно пробовать вот так
    # OrganizationCorrelation.objects.filer(Q(org_1__inn=inn)| Q(org2__inn=inn)).distinct().order_by('-correlation').values_list('org_1__inn', 'org_2__inn')
    org_1 = models.ForeignKey('organizations.Organization', on_delete=models.PROTECT,
                              related_name='correlation_1')
    org_2 = models.ForeignKey('organizations.Organization', on_delete=models.PROTECT,
                              related_name='correlation_2')
    correlation = models.FloatField('Коэффициент', default=0)

    class Meta:
        verbose_name = 'Близость организации'
        verbose_name_plural = 'Близости Организаций'
        unique_together = [('org_1', 'org_2')]

    @classmethod
    def calculate_rating(cls, inn_1, inn_2) -> 'OrganizationCorrelation':
        org1 = Organization.objects.get(inn=inn_1)
        org2 = Organization.objects.get(inn=inn_2)
        # 2  * 3 * 10 * (1 + 4 + 5 + 6 + 7 + 8 + 9 + 2 + 3 + 10)
        right_sum = 0
        # 1
        if org1.region_id == org2.region_id:
            right_sum += 1
        # 4
        delta = (org1.found_date - org2.found_date).days
        if abs(delta) < 365:
            right_sum += 1
        elif abs(delta) < 1000:
            right_sum += 0.5
        # 5
        if org1.size_id == org2.size_id:
            right_sum += 1
        # 6 не нашел
        # 7
        equal_count = 0
        count = 4
        if org1.eshn == org2.eshn:
            equal_count += 1
        if org1.srp == org2.srp:
            equal_count += 1
        if org1.envd == org2.envd:
            equal_count += 1
        if org1.usn == org2.usn:
            equal_count += 1
        right_sum += equal_count / count
        # 8 типы не нашел, можно смотреть по длине инн
        # 9 контрактов нет(
        # 10 этого тоже нет
        # 3 вид деятельности хз
        # 2
        okveds_count = org1.okveds.filter(id__in=org2.okveds.values_list("id", flat=True)).count()
        okveds = 1
        for i in range(okveds_count - 1):
            okveds += 0.1
        correlation = okveds * (right_sum + okveds)
        correlation_model, _ = cls.objects.get_or_create(org_1_id=org1.id, org_2_id=org2.id)
        correlation_model.correlation = correlation
        correlation_model.save()
        return correlation_model


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


class TypeFormatSupport(DjangoChoices):
    not_defined = ChoiceItem('not_defined', 'Не определено')
    credit = ChoiceItem('credit', 'Возвратная (займ, кредит)')
    consultation = ChoiceItem('consultation', 'Консультации')
    grant = ChoiceItem('grant', 'Грант')
    subsidian = ChoiceItem('subsidian', 'Субсидиарная')
    guarantee = ChoiceItem('guarantee', 'Гарантии (поручительства)')
    regulator = ChoiceItem('regulator', 'Регуляторная')
    property_support = ChoiceItem('property_support', 'Имущественная поддержка')
    education_help = ChoiceItem('education_help', 'Образовательная поддержка')


class RegularitySelect(DjangoChoices):
    regular = ChoiceItem('regular', 'На регулярной основе')
    every_year = ChoiceItem('every_year', 'Ежегодно')
    one_time = ChoiceItem('one_time', 'Единоразово')
    every_month = ChoiceItem('every_month', 'Ежемесячно')
    not_more_two_times = ChoiceItem('not_more_two_times', 'Не более 2 раз в год')
    every_kvartal = ChoiceItem('every_kvartal', 'Ежеквартально')
    two_times_per_year_2_4_kvartal = ChoiceItem('two_times_per_year_2_4_kvartal',
                                                '2 раза в год (во 2 и 4 квартале)')
    two_times_per_year_1_3_kvartal = ChoiceItem('two_times_per_year_1_3_kvartal',
                                                '2 раза в год (во 1 и 3 квартале)')


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
    type_format_support = models.CharField('Формат предоставления поддержки', max_length=20,
                                           default=TypeFormatSupport.not_defined,
                                           choices=TypeFormatSupport.choices)
    regularity_select = models.CharField('Регуляронсть оказания мер поддержки', max_length=30,
                                         default=RegularitySelect.regular,
                                         choices=RegularitySelect.choices)
    is_sofinance = models.BooleanField('Необходимость софинансирования проекта', default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Мера поддержки'
        verbose_name_plural = 'Меры поддержки'


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


class Coefficients(SingletonModel):
    similarity_coefficient = models.FloatField(
        'Пороговое значения коэффициента похожести организаций', default=3.5
    )

    class Meta:
        verbose_name = 'Коэффициенты'
        verbose_name_plural = 'Коэффициенты'
