from django.db import models
from djchoices import DjangoChoices, ChoiceItem


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        instance, created = cls.objects.get_or_create(pk=1)
        return instance


class YesNoChoices(DjangoChoices):
    yes = ChoiceItem('yes', 'Да')
    no = ChoiceItem('no', 'Нет')


class CreatedUpdatedDateModelMixin(models.Model):
    created = models.DateTimeField('Дата добавления', auto_now_add=True)
    updated = models.DateTimeField('Дата изменения', auto_now=True)

    class Meta:
        abstract = True


class NotDeletedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SafeDeleteMixin(models.Model):
    is_deleted = models.BooleanField('Удален', default=False)

    objects = NotDeletedManager()

    class Meta:
        abstract = True


class RelatedManagerMixin(object):
    related_fields = set()
    prefetch_fields = set()

    def get_queryset(self):
        return (super().get_queryset()
                .select_related(*self.related_fields)
                .prefetch_related(*self.prefetch_fields))
