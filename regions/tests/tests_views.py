"""
Note that this app comes with some pre-filled data with migrations
"""
import os
from unittest.mock import patch

from django.core.cache import cache
from model_mommy import mommy
from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APITestCase
from waffle.testutils import override_flag

from regions.models import FederalSubject, FederalDistrict

User = get_user_model()


class FederalSubjectApiTestCase(APITestCase):
    user_data = dict(
        username='test1',
        email='test1@test.com',
        password='fakehash',
    )

    def test_list_readonly(self):
        user = User.objects.create(**self.user_data)
        self.client.force_authenticate(user=user)  # it's 403 for a guest

        url = reverse('api:federalsubject-list')
        data = FederalSubject.objects.values().last()
        data['id'] += 9999
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_filters(self):
        user = User.objects.create(**self.user_data)
        self.client.force_authenticate(user=user)
        url = reverse('api:federalsubject-list')
        response = self.client.get(url, data={'name': 'Татарстан'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], 78)

    # def test_search(self):
    #     for region in FederalSubject.objects.all():
    #         region.save()
    #     user = User.objects.create(**self.user_data)
    #     self.client.force_authenticate(user=user)
    #     url = reverse('api:federalsubject-list')
    #     response = self.client.get(url, data={'search': 'Татарстан'})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data[0]['id'], 78)
    #     response = self.client.get(url, data={'search': 'Республика Татарстан'})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data[0]['id'], 78)
    #     response = self.client.get(url, data={'search': 'Алтайский край'})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data[0]['id'], 6)
    #     response = self.client.get(url, data={'search': 'Москва'})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data[0]['id'], 48)

    def test_detail_readonly(self):
        user = User.objects.create(**self.user_data)
        self.client.force_authenticate(user=user)  # it's 403 for a guest

        data = FederalSubject.objects.values().last()
        url = reverse('api:federalsubject-detail', kwargs=dict(pk=data['id']))

        for method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            response = getattr(self.client, method.lower())(url, data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list_is_without_pagination(self):
        url = reverse('api:federalsubject-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        db_data = list(FederalSubject.objects.all())
        retrieved_data = response.data
        self.assertEqual(len(db_data), len(retrieved_data))
        self.assertEqual({fs.id for fs in db_data},
                         {fs['id'] for fs in retrieved_data})

    def test_get(self):
        data = FederalSubject.objects.values().last()
        url = reverse('api:federalsubject-detail', kwargs=dict(pk=data['id']))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['id'], response.data['id'])
        assert 'full_pretty_name' in response.data
        assert 'timezones' in response.data
        assert isinstance(response.data['timezones'], list)


class FederalDistrictApiTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('api:federaldistrict-list')
        user_data = dict(
            username='test1',
            email='test1@test.com',
            password='fakehash',
        )
        self.user = mommy.make('accounts.User', **user_data)
        self.client.force_authenticate(user=self.user)

    def test_list_readonly(self):
        data = FederalDistrict.objects.values().last()
        data['id'] += 9999
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_filters(self):
        response = self.client.get(self.url, data={'name': 'Южный'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], 3)

    # def test_search(self):
    #     response = self.client.get(self.url, data={'search': 'СКФО'})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data[0]['id'], 4)
    #     response = self.client.get(self.url, data={'search': 'Северо-Кавказский'})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data[0]['id'], 4)
    #     response = self.client.get(self.url, data={'search': 'Приволжский'})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data[0]['id'], 5)

    def test_detail_readonly(self):
        data = FederalDistrict.objects.values().last()
        url = reverse('api:federaldistrict-detail', kwargs=dict(pk=data['id']))

        for method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            response = getattr(self.client, method.lower())(url, data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list_is_without_pagination(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        db_data = list(FederalDistrict.objects.all())
        retrieved_data = response.data
        self.assertEqual(len(db_data), len(retrieved_data))
        self.assertEqual({fd.id for fd in db_data},
                         {fd['id'] for fd in retrieved_data})

    def test_get(self):
        data = FederalDistrict.objects.values().last()
        url = reverse('api:federaldistrict-detail', kwargs=dict(pk=data['id']))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['id'], response.data['id'])
