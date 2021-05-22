import os
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse, NoReverseMatch
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from freezegun import freeze_time

from pictures.models import Picture
from pictures.test_utils import get_raw_image, get_image_file

User = get_user_model()

_datetime = timezone.localtime()
_datetime_str_format = _datetime.isoformat()


class _PictureCountMixin:
    # Some data migrations (namely `contest_dobr/migrations/0005_data_dobr2017_winners.py`)
    # create Photo instances, so we should subtract their count when asserting
    # the count increase.

    def init_count(self):
        self.count_initial = self.model.objects.count()

    def assertPictureCountInc(self, expected):
        self.assertEqual(self.model.objects.count() - self.count_initial, expected)


@freeze_time(_datetime)
class PictureUploadAuthorizedUserApiTestCase(_PictureCountMixin, APITestCase):
    model = Picture

    @staticmethod
    def get_image_urls(data):
        # Looks like: http://testserver/media/pictures/50e6c09ad5754f8abe54da660ca6bb44.jpeg
        return {key: data[key] for key in data.keys()}

    def setUp(self):
        self.user = User.objects.create(**{
            'username': 'test1',
            'password': 'test123456',
            'email': 'test@test.ru',
        })
        self.client.force_authenticate(user=self.user)
        self.init_count()

    def test_valid_jpeg_upload_multipart(self):
        url = reverse('api:picture-list')

        image_input = get_image_file()
        response = self.client.post(url, dict(image=image_input))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Looks like: http://testserver/media/pictures/50e6c09ad5754f8abe54da660ca6bb44.jpeg
        received_im_url = response.data['image']['original']

        # extract generated image name from url
        im_filename = re.match(
            f"^{settings.MEDIA_URL}pictures/([^/]+)$",
            received_im_url
        ).group(1)

        # Ensure that the file actually exists
        self.assertTrue(os.path.isfile(
            os.path.join(settings.MEDIA_ROOT, 'pictures', im_filename)))

        received_im_urls = self.get_image_urls(response.data['image'])
        self.assertDictEqual(
            response.data, {
                'id': response.data['id'],
                'image': received_im_urls,
                'date_added': _datetime_str_format
            })
        self.assertPictureCountInc(1)

    def test_valid_jpeg_upload_raw_body(self):
        url = reverse('api:picture-list')

        mime_format = 'jpeg'
        raw_image, size = get_raw_image(mime_format=mime_format)

        response = self.client.put(
            url, raw_image.read(),
            content_type=f"image/{mime_format}",
            HTTP_CONTENT_LENGTH=size,
            HTTP_CONTENT_DISPOSITION=f"attachment; filename=img.{mime_format}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        received_im_urls = self.get_image_urls(response.data['image'])

        self.assertDictEqual(
            response.data, {
                'id': response.data['id'],
                'image': received_im_urls,
                'date_added': _datetime_str_format
            })
        self.assertPictureCountInc(1)

    def test_no_put_for_multipart(self):
        url = reverse('api:picture-list')

        image_input = get_image_file()
        response = self.client.put(url, dict(image=image_input))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_post_for_raw(self):
        url = reverse('api:picture-list')

        mime_format = 'jpeg'
        raw_image, size = get_raw_image(mime_format=mime_format)

        response = self.client.post(
            url, raw_image.read(),
            content_type=f"image/{mime_format}",
            HTTP_CONTENT_LENGTH=size,
            HTTP_CONTENT_DISPOSITION=f"attachment; filename=img.{mime_format}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_passed_date_added_is_ignored(self):
        url = reverse('api:picture-list')

        image_input = get_image_file()

        response = self.client.post(url, dict(image=image_input,
                                              date_added='2010-01-01T10:00:00.000001Z'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        received_im_urls = self.get_image_urls(response.data['image'])

        self.assertDictEqual(
            response.data, {
                'id': response.data['id'],
                'image': received_im_urls,
                'date_added': _datetime_str_format
            })

    def test_invalid_upload(self):
        url = reverse('api:picture-list')

        file = """<?php echo 'hacked. hahaha.'; ?>"""

        pseudo_image_input = SimpleUploadedFile("img.jpeg", file.encode(),
                                                content_type="image/jpeg")

        response = self.client.post(url, dict(image=pseudo_image_input))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.data,
            {'image': [
                'Загрузите корректное изображение. Загруженный файл не является '
                'изображением, либо является испорченным.'
            ]})
        self.assertPictureCountInc(0)

    def test_large_image(self):
        url = reverse('api:picture-list')

        image_input = get_image_file(width=500, height=8000)

        response = self.client.post(url, dict(image=image_input))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.data,
            {'image': [
                # todo translate the message.
                # https://github.com/codingjoe/django-stdimage/tree/master/stdimage/locale
                # https://stackoverflow.com/questions/26753663/django-translations-of-third-party-apps  # noqa
                # https://stackoverflow.com/questions/17837149/makemessages-for-an-app-installed-in-virtualenv  # noqa
                'The image you uploaded is too large. The required maximum '
                f'resolution is: {self.model.max_width}x{self.model.max_height} px.'
            ]})
        self.assertPictureCountInc(0)

    def test_only_create_allowed(self):
        # test no update, no delete, no get, no list
        url = reverse('api:picture-list')

        image_input = get_image_file()
        response = self.client.post(url, dict(image=image_input))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertPictureCountInc(1)

        # Test no list:
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertDictEqual(response.data,
                             {'detail': 'Метод "GET" не разрешен.'})

        with self.assertRaises(NoReverseMatch):
            # http://www.django-rest-framework.org/api-guide/routers/#simplerouter

            # Test no retrieve (GET):
            # Test no update (PUT):
            # Test no partial_update (PATCH):
            # Test no destroy (DELETE):
            reverse('api:picture-detail', kwargs=dict(pk=1))


class PictureUploadUnauthorizedUserApiTestCase(_PictureCountMixin, APITestCase):
    model = Picture

    def setUp(self):
        self.init_count()

    def test_unauthorized_cannot_upload(self):
        url = reverse('api:picture-list')

        image_input = get_image_file()
        response = self.client.post(url, dict(image=image_input))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertPictureCountInc(1)
