from django.contrib import admin
from django.utils.html import format_html

from pictures.models import Picture


@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_tag', 'date_added')

    def image_tag(self, obj):  # pragma: no cover
        if not obj.image:
            return "-"
        return format_html('<img src="{}" width="150" height="150">', obj.image.url)

    image_tag.short_description = 'Изображение'
