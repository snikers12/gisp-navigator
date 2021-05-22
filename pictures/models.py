from django.db import models
from stdimage.models import StdImageField
from stdimage.utils import UploadToUUID
from stdimage.validators import MaxSizeValidator

PICTURE_VARIATIONS = {
    'thumbnail': dict(width=256, height=256, crop=True),
    'medium': dict(width=512, height=512),
    'large': dict(height=1024),
}


class Picture(models.Model):
    max_width = 5000
    max_height = 7000

    image = StdImageField(
        verbose_name='Изображение',
        upload_to=UploadToUUID(path='pictures'),
        validators=[MaxSizeValidator(max_width, max_height)],
        variations=PICTURE_VARIATIONS
    )
    date_added = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'

    def __str__(self):
        return self.image.url
