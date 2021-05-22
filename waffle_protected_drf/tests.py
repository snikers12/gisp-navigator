import json
from collections import Mapping

from django.conf.urls import url, include
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from django.test import override_settings
from rest_framework import status, viewsets, mixins, serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.test import APITestCase
from waffle.testutils import override_flag

from waffle_protected_drf import FLAG_NAME, GROUP_NAME
from waffle_protected_drf.routers import WaffleProtectedDefaultRouter

User = get_user_model()


class WaffleProtectedDrfAPITestCase(APITestCase):

    HTML_ACCEPT = 'text/html;q=0.9,*/*;q=0.8'
    JSON_ACCEPT = 'application/json;q=0.9,*/*;q=0.8'

    @override_settings(DEBUG=False)
    def test_waffle_override_is_denied(self):
        with self.assertRaises(AssertionError):
            with override_settings(WAFFLE_OVERRIDE=True):
                self.client.get('/', HTTP_ACCEPT=self.HTML_ACCEPT)

    @override_settings(DEBUG=True)
    def test_on_debug_always_accessible(self):
        self._test_accessible()

    @override_settings(DEBUG=False)
    def test_user_permissions(self):
        user = User.objects.create(username='test', password='a', email='aa@aa.com')

        # - force_authenticate() is for DRF;
        # - force_login() is for Django (admin).
        #
        # We need exactly the latter here.
        self.client.force_login(user=user)

        # no access for a regular user
        self._test_inaccessible()

        # access for user of a special group
        user.groups.add(Group.objects.get(name=GROUP_NAME))
        self._test_accessible()

        # reset
        user.groups.clear()
        self._test_inaccessible()

        # access for superuser
        user.is_superuser = True
        user.save()
        self._test_accessible()

    @override_settings(DEBUG=False)
    def test_access_by_flag(self):
        self._test_inaccessible()  # w/o flag set, by default it should be inaccessible

        with override_flag(FLAG_NAME, active=False):
            self._test_inaccessible()

        with override_flag(FLAG_NAME, active=True):
            self._test_accessible()

    def _test_accessible(self):
        # HTML is rendered when requesting HTML
        response = self.client.get('/', HTTP_ACCEPT=self.HTML_ACCEPT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('text/html; charset=utf-8', response['Content-Type'])
        assert b'https://www.django-rest-framework.org' in response.content  # header logo

        # ... even with format
        response = self.client.get('/', HTTP_ACCEPT=self.HTML_ACCEPT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('text/html; charset=utf-8', response['Content-Type'])
        assert b'https://www.django-rest-framework.org' in response.content  # header logo

        # JSON is rendered when requesting JSON
        response = self.client.get('/', HTTP_ACCEPT=self.JSON_ACCEPT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('application/json', response['Content-Type'])
        self.assertTrue(isinstance(response.data, Mapping))  # dict of endpoints
        self.assertTrue(response.data)  # not empty

        with override_settings(ROOT_URLCONF=__name__):
            # For endpoints
            # HTML is rendered when requesting HTML
            response = self.client.get('/example/', HTTP_ACCEPT=self.HTML_ACCEPT)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual('text/html; charset=utf-8', response['Content-Type'])
            assert b'https://www.django-rest-framework.org' in response.content  # header logo

            # JSON is rendered when requesting JSON
            response = self.client.get('/example/', HTTP_ACCEPT=self.JSON_ACCEPT)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual('application/json', response['Content-Type'])
            self.assertDictEqual(response.data, ExampleViewSet.test_response.copy())

            # OPTIONS returns metadata
            response = self.client.options('/example/')
            self.assertTrue(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['description'], ExampleViewSet.__doc__)
            self.assertTrue(response.data['renders'])
            self.assertTrue(response.data['parses'])

            response = self.client.options('/')
            self.assertTrue(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['name'], 'Api Root')
            self.assertTrue(response.data['renders'])
            self.assertTrue(response.data['parses'])

    def _test_inaccessible(self):
        # JSON is rendered when requesting HTML
        response = self.client.get('/', HTTP_ACCEPT=self.HTML_ACCEPT)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # When browsable api is disabled, we should always render JSON.
        self.assertEqual('application/json', response['Content-Type'])
        self.assertDictEqual({}, json.loads(response.content))  # no routes list

        # ... even with format
        response = self.client.get('/?format=api', HTTP_ACCEPT=self.HTML_ACCEPT)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual('application/json', response['Content-Type'])
        self.assertDictEqual({}, json.loads(response.content))  # no routes list

        # JSON is rendered when requesting JSON
        response = self.client.get('/', HTTP_ACCEPT=self.JSON_ACCEPT)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual('application/json', response['Content-Type'])
        self.assertDictEqual({}, json.loads(response.content))  # no routes list

        with override_settings(ROOT_URLCONF=__name__):
            # For endpoints
            # JSON is rendered when requesting HTML
            response = self.client.get('/example/', HTTP_ACCEPT=self.HTML_ACCEPT)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual('application/json', response['Content-Type'])
            self.assertDictEqual(response.data, ExampleViewSet.test_response.copy())

            # JSON is rendered when requesting JSON
            response = self.client.get('/example/', HTTP_ACCEPT=self.JSON_ACCEPT)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual('application/json', response['Content-Type'])
            self.assertDictEqual(response.data, ExampleViewSet.test_response.copy())

            # OPTIONS doesn't return sensitive metadata
            response = self.client.options('/example/')
            self.assertTrue(response.status_code, status.HTTP_200_OK)
            self.assertSetEqual(set(response.data.keys()), {'renders', 'parses'})
            self.assertTrue(response.data['renders'])
            self.assertTrue(response.data['parses'])

            # OPTIONS returns choices
            response = self.client.options('/choices/')
            self.assertTrue(response.status_code, status.HTTP_200_OK)
            self.assertDictEqual(
                {'POST': {'myfield': {'choices': [
                    {'display_name': 'A Value', 'value': 'akey'},
                    {'display_name': 'B Value', 'value': 'bkey'}
                ]}}}, response.data['actions'])

            response = self.client.options('/')
            self.assertTrue(response.status_code, status.HTTP_404_NOT_FOUND)


class ChoicesModel(models.Model):
    myfield = models.CharField(choices=[('akey', 'A Value'), ('bkey', 'B Value')], max_length=4)

    class Meta:
        managed = False


class ChoicesModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoicesModel
        fields = '__all__'


class ChoicesViewSet(viewsets.ModelViewSet):
    queryset = ChoicesModel.objects.all()
    serializer_class = ChoicesModelSerializer
    permission_classes = (AllowAny,)


class ExampleViewSet(mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """FRONTEND IS PAIN, PYTHON IS GREAT"""
    queryset = None
    serializer_class = None
    test_response = {'life': 'is complicated'}

    def list(self, request, *args, **kwargs):
        return Response(self.test_response.copy())


router = WaffleProtectedDefaultRouter()
router.register('choices', ChoicesViewSet, basename='choices')
router.register('example', ExampleViewSet, basename='example')

app_name = __name__
urlpatterns = [
    url('', include((router.urls, app_name), namespace='test')),
]
