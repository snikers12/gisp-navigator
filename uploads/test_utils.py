from django.core.files.uploadedfile import SimpleUploadedFile

from uploads.models import FileUpload


def get_file(extension='txt'):
    return SimpleUploadedFile(f'file.{extension}', b'test')


def create_test_file_upload(file=None) -> FileUpload:
    if isinstance(file, str):
        file = get_file(extension=file)
    file = file or get_file()
    return FileUpload.objects.create(file=file)
