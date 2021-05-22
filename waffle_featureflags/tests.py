from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import NoReverseMatch, reverse
from rest_framework import status
from rest_framework.test import APITestCase
from waffle.models import Flag
from waffle.testutils import override_sample, override_flag, override_switch

User = get_user_model()


class FeatureFlagsAPITestCase(APITestCase):
    def setUp(self):
        pass

    def test_no_detail(self):
        with self.assertRaises(NoReverseMatch):
            # Test no retrieve (GET):
            # Test no update (PUT):
            # Test no partial_update (PATCH):
            # Test no destroy (DELETE):
            reverse('api:featureflags-detail', kwargs=dict(pk=1))

    def test_no_create(self):
        url = reverse('api:featureflags-list')
        response = self.client.post(url, dict())
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @override_settings(WAFFLE_FEATUREFLAGS_EXPOSE=[
        ('switch', 'visible_switch'),
        ('switch', 'missing_switch'),
        ('flag', 'visible_flag'),
        ('sample', 'visible_sample'),
        ('bad_waffle_type', 'invisible_switch'),  # should be ignored
    ])
    @override_switch('visible_switch', active=True)
    @override_switch('invisible_switch', active=True)
    @override_flag('visible_flag', active=True)
    @override_flag('invisible_flag', active=True)
    @override_sample('visible_sample', active=True)
    @override_sample('invisible_sample', active=True)
    def test_exposed_featureflags(self):
        url = reverse('api:featureflags-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSetEqual({'visible_switch', 'missing_switch',
                             'visible_flag', 'visible_sample'},
                            set(response.data.keys()))

    @override_settings(WAFFLE_FEATUREFLAGS_EXPOSE=[
        ('flag', 'visible_flag'),
    ])
    def test_waffle_flags_individual_per_user(self):
        url = reverse('api:featureflags-list')

        # check default
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['visible_flag'])

        # setup users
        user_regular = User.objects.create(username='regular', email='regular@test')
        user_special = User.objects.create(username='special', email='special@test')

        flag = Flag.objects.create(name='visible_flag')
        flag.users.add(user_special)

        # still disabled for guests
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['visible_flag'])

        # enabled for a special user
        self.client.force_authenticate(user=user_special)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['visible_flag'])

        # but still disabled for a regular one
        self.client.force_authenticate(user=user_regular)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['visible_flag'])
