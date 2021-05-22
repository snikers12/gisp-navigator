from logging import getLogger
from rest_framework import serializers

from .models import FileUpload

logger = getLogger(__name__)


class FileUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField()

    class Meta:
        model = FileUpload
        fields = '__all__'


class InlineFileUploadSerializer(serializers.ModelSerializer):
    """
    При использование сериализатора `InlineFileUploadSerializer` в сериализаторе сущности
    нужно проверить, что автор файла и автор сущности является одиним и тем же пользователем.
    Иначе можно будет перебирать подряд айдишки файлов и смотреть чужие документы.
    """
    file = serializers.FileField(read_only=True)

    class Meta:
        model = FileUpload
        fields = ('file',)

    def to_representation(self, instance):
        return self.fields['file'].to_representation(instance.file)
