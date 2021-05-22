from django.contrib import admin
from django.utils.html import format_html

from .models import FileUpload


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'link', 'date_added')

    def link(self, obj: FileUpload):  # pragma: no cover
        if not obj.file:
            return "-"
        return format_html('<a href="{}" target="_blank" rel="noopener">{}</a>', obj.file.url,
                           obj.file.url)

    link.short_description = 'Ссылка на файл'
