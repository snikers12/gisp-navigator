from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from django.utils import timezone
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from uploads.validators import FileUploadExtensionValidator
from .models import FileUpload
from .test_utils import get_file, create_test_file_upload
from pictures.test_utils import get_raw_image

User = get_user_model()

_datetime = timezone.localtime()
_datetime_str_format = _datetime.isoformat()


@freeze_time(_datetime)
class FileUploadAuthorizedUserApiTestCase(APITestCase):
    model = FileUpload

    def setUp(self):
        self.user = User.objects.create(**{
            'username': 'test1',
            'password': 'test123456',
            'email': 'test@test.ru',
        })
        self.client.force_authenticate(user=self.user)

    def test_only_create_allowed(self):
        # test no update, no delete, no get, no list
        url = reverse('api:fileupload-list')

        # Test no list:
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        with self.assertRaises(NoReverseMatch):
            # http://www.django-rest-framework.org/api-guide/routers/#simplerouter

            # Test no retrieve (GET):
            # Test no update (PUT):
            # Test no partial_update (PATCH):
            # Test no destroy (DELETE):
            reverse('api:fileupload-detail', kwargs=dict(pk=1))

    def test_upload_raw_body(self):
        url = reverse('api:fileupload-list')

        mime_format = 'jpeg'
        for count, is_post in enumerate([True, False]):
            print(f'Method is {"post" if is_post else "put"}')
            request_method = self.client.post if is_post else self.client.put

            raw_image, size = get_raw_image(mime_format=mime_format)

            response = request_method(
                url, raw_image.read(),
                content_type=f"image/{mime_format}",
                HTTP_CONTENT_LENGTH=size,
                HTTP_CONTENT_DISPOSITION=f"attachment; filename=img.{mime_format}")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(self.model.objects.count(), count + 1)
            self.assertEqual(response.data['file'].split('/')[-1], f'img.{mime_format}')

            with raw_image as sent, self.model.objects.get(id=response.data['id']).file as saved:
                sent.seek(0)
                saved.seek(0)
                self.assertEqual(sent.read(), saved.read())

    def test_upload_for_multipart(self):
        url = reverse('api:fileupload-list')
        for file_count, is_post in enumerate([True, False]):
            print(f'Method is {"post" if is_post else "put"}')
            request_method = self.client.post if is_post else self.client.put

            file_input = get_file()
            response = request_method(url, dict(file=file_input))
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(self.model.objects.count(), file_count + 1)

            filename = response.data['file'].split('/')[-1]
            self.assertEqual(filename, 'file.txt')

            with file_input as sent, self.model.objects.get(id=response.data['id']).file as saved:
                sent.seek(0)
                saved.seek(0)
                self.assertEqual(sent.read(), saved.read())

    def test_upload_file_path_is_different(self):
        url = reverse('api:fileupload-list')
        file_input = get_file()

        response1 = self.client.post(url, dict(file=file_input))
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        file_input.seek(0)
        response2 = self.client.post(url, dict(file=file_input))
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        with self.model.objects.get(id=response1.data['id']).file as file1, \
                self.model.objects.get(id=response2.data['id']).file as file2:
            file1.seek(0)
            file2.seek(0)
            self.assertEqual(file1.read(), file2.read())

        self.assertNotEqual(response1.data['file'], response2.data['file'])


class FileUploadUnauthorizedUserApiTestCase(APITestCase):
    model = FileUpload

    def test_unauthorized_can_upload(self):
        url = reverse('api:fileupload-list')

        file_input = get_file()
        response = self.client.post(url, dict(file=file_input))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.model.objects.count(), 1)


class ValidatorsTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(**{
            'username': 'test1',
            'password': 'test123456',
            'email': 'test@test.ru',
        })

    def test_extension_validator(self):
        allowed = ['pdf', 'pdF']
        disallowed = ['pdff', 'doc']
        m = ExtensionsValidatorModel()

        for ext in allowed:
            file_upload = create_test_file_upload(get_file(ext))
            m.upload = file_upload
            m.full_clean()  # should not raise

        for ext in disallowed:
            file_upload = create_test_file_upload(get_file(ext))
            m.upload = file_upload
            with self.assertRaises(ValidationError):
                m.full_clean()


class ExtensionsValidatorModel(models.Model):
    upload = models.ForeignKey(FileUpload, on_delete=models.PROTECT,
                               validators=[FileUploadExtensionValidator(['pdf', 'txt'])])

    class Meta:
        managed = False
