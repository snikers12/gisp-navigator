from django.core.validators import FileExtensionValidator
from django.utils.deconstruct import deconstructible

from uploads.models import FileUpload


@deconstructible
class FileUploadExtensionValidator(FileExtensionValidator):
    """
    Validates file extension of a FileUpload in a FK.
    Usage example:
    upload = models.ForeignKey(FileUpload, on_delete=models.PROTECT,
                               validators=[FileUploadExtensionValidator(['pdf', 'txt'])])

    Usage in DRF serializers:
    my_file = InlineFileUploadSerializer(read_only=True)
    my_file_id = serializers.PrimaryKeyRelatedField(
        queryset=FileUpload.objects.all(), source='my_file', required=False,
        validators=MyModel._meta.get_field('my_file').validators)

    """

    def __call__(self, file_upload_pk):
        if isinstance(file_upload_pk, FileUpload):  # when used with DRF
            file_upload = file_upload_pk
        else:
            file_upload = FileUpload.objects.get(pk=file_upload_pk)
        return super().__call__(file_upload.file)
