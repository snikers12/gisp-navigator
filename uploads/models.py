from django.conf import settings
from django.db import models
from .utils import UploadToClassNameDirUUIDDirOriginalFileName


# Don't use get_user_model() here, because the User model might depend on
# this app, which would create a cyclic dependency. But using AUTH_USER_MODEL
# as string is fine.


class FileUpload(models.Model):
    file = models.FileField(verbose_name='Файл',
                            upload_to=UploadToClassNameDirUUIDDirOriginalFileName())
    date_added = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'

    def __str__(self):
        return self.file.url
