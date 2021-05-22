from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import UserManager as AbstractUserManager
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from djchoices import DjangoChoices, ChoiceItem

from accounts.validators import UsernameValidator
from gisp.models import RelatedManagerMixin


class UserExpertStatus(DjangoChoices):
    not_specified = ChoiceItem('not_specified', 'Не указано')
    social = ChoiceItem('social', 'Общественник')
    state_employee = ChoiceItem('state_employee', 'Госслужащий')


class UserManager(RelatedManagerMixin, AbstractUserManager):
    related_fields = ('photo',)
    prefetch_fields = ('groups',)

    @classmethod
    def normalize_email(cls, email):
        email = super().normalize_email(email)
        return email.lower()

    def _create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('The email must be set')
        username = email.split('@')[0]
        return super()._create_user(username, email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        username = email.split('@')[0]
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _('username'),
        max_length=250,
        validators=[UsernameValidator()],
        blank=True
    )
    email = models.EmailField(
        _('email address'), unique=True,
        error_messages={'unique': 'Пользователь с таким адресом электронной почты уже существует.'})
    photo = models.ForeignKey('pictures.Picture', verbose_name='Фото', blank=True, null=True,
                              on_delete=models.PROTECT)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into '
                    'this admin site.'),
    )

    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['-date_joined']),
            models.Index(fields=['-email', '-date_joined']),
        ]

    def clean(self):
        super(User, self).clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return self.username

    def __str__(self):
        return f'{self.id} - {self.get_full_name()} - {self.email}'
