# from abc import ABCMeta, abstractmethod
# from datetime import timedelta
# from unittest.mock import patch
#
# from django.contrib.auth.models import Group, User
# from django.urls import reverse
# from django.utils import timezone
# from freezegun import freeze_time
# from model_mommy import mommy
# from rest_framework import status
# from rest_framework.authtoken.models import Token
# from rest_framework.test import APITestCase
#
# from accounts.serializers import UserSerializer
# from pictures.test_utils import create_test_picture
#
#
# class AbstractAuthApiTestCase(APITestCase):
#     def setUp(self):
#         self.user = mommy.make('accounts.User', email='test@test.com')
#         self.user.set_password('password1')
#         self.user.save()
#
#     def test_user_can_login(self):
#         url = reverse('api:auth-login')
#         data = {
#             'username': 'test@test.com',
#             'password': 'password1',
#         }
#
#         for mod_status, is_auth_allowed in dict(approved=True, rejected=True,
#                                                 waiting=True, blocked=False).items():
#             self.user.moderation_status = mod_status
#             self.user.save()
#
#             response = self.client.post(url, data)
#             self.assertEqual(response.status_code,
#                              status.HTTP_200_OK if is_auth_allowed
#                              else status.HTTP_423_LOCKED)
#             self.assertTrue((response.get('Token') is not None) is is_auth_allowed)
#
#     def test_failed_auth(self):
#         url = reverse('api:auth-login')
#         response = self.client.post(url, {
#             'username': 'test@test.com',
#             'password': '123123123'
#         })
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIsNone(response.get('Token'))
#
#     def test_logout(self):
#         response = self.client.post(reverse('api:auth-login'), {
#             'username': 'test@test.com',
#             'password': 'password1'
#         })
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(Token.objects.count(), 1)
#
#         response = self.client.post(reverse('api:auth-logout'))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(Token.objects.count(), 0)
#
#     def test_user_update(self):
#         data = {
#             'email': 'test@mail.com',
#             'phone': '+79502223344',
#             'birth_date': '1997-11-11',
#         }
#
#         url = reverse('api:user-detail', kwargs={'pk': self.user.id})
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#
#         self.client.force_authenticate(self.user)
#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         for key in data.keys():
#             self.assertEqual(response.data[key], data[key])
#
#         # test update phone
#         mommy.make('accounts.User', phone='+79503331111')
#         data = {
#             'phone': '+79502223344'
#         }
#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         for key in data.keys():
#             self.assertEqual(response.data[key], data[key])
#
#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         for key in data.keys():
#             self.assertEqual(response.data[key], data[key])
#         data['phone'] = '+79503331111'
#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#
#         mommy.make('accounts.User', phone='')
#
#         data = {
#             'phone': '+79992223333'
#         }
#         response = self.client.patch(url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['phone'], data['phone'])
#
#     def test_change_password(self):
#         data = {
#             'old_password': 'poop',
#             'new_password': 'secure-password-i-swear'
#         }
#         self.user.password = 'invalid-hash'
#         self.user.save()
#         url = reverse('api:user-change-password')
#
#         # guests can't change
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#
#         self.client.force_authenticate(user=self.user)
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertSetEqual(set(response.data.keys()), {'old_password'})
#
#         self.user.set_password(data['old_password'])
#         self.user.save()
#
#         response = self.client.post(url, {**data, 'new_password': 's'})
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertSetEqual(set(response.data.keys()), {'new_password'})
#
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#         self.user.refresh_from_db()
#         self.assertTrue(self.user.check_password(data['new_password']))
#
#         # set password first time
#         self.user.password = ''
#         self.user.save()
#         response =
#         self.client.post(url, {'old_password': '', 'new_password': data['new_password']})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.user.refresh_from_db()
#         self.assertTrue(self.user.check_password(data['new_password']))
#
#         response =
#         self.client.post(url, {'old_password': '', 'new_password': data['new_password']})
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#
#
# class AbstractRegistrationApiTestCase(metaclass=ABCMeta):
#     default_email = "test@example.com"
#     default_password = "l3atjvymirwd7"
#     model = User
#     serializer = UserSerializer
#
#     user_data = {
#         "email": default_email,
#         "password": default_password,
#     }
#
#     invalid_username = ["", "🤡", "#hash"]
#     invalid_values = {
#         "email": ["", "@", "test@", "🙁@test.com", None],
#         "password": [""],
#     }
#
#     def setUp(self):
#         self.url = reverse(f'api:{self.model.__name__.lower()}-list')
#
#     def test_successful_registration(self):
#
#         # email in upper case save as lower
#         data = {**self.user_data, 'email': self.user_data['email'].upper(),
#                 'username': 'Петя Иванов', 'phone': '+79992223333'}
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(status.HTTP_201_CREATED, response.status_code)
#         self.assertEqual(response.data['email'].lower(), self.user_data['email'].lower())
#         self.assertEqual(1, self.model.objects.count())
#         user = self.model.objects.get()
#         self.assertEqual(self.default_email, user.email.lower())
#         self.assertTrue(Token.objects.get(key=response['Token']))
#         # ensure that the created user model matches sent data
#         self.verify_user_data(user, self.user_data)
#         # ensure that the returned user matches the created model data
#         self.verify_user_data(user, response.data)
#
#         # test with same email in lower case
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
#
#         # test with same phone
#         data = {
#             "email": 'test@mail.ru',
#             "password": 'fgasyb1234a',
#             'phone': '+79502221313'
#         }
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(status.HTTP_201_CREATED, response.status_code)
#
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
#
#     @abstractmethod
#     def verify_user_data(self, model, user_data):
#         pass
#
#     def create_user(self, **user_data):
#         self.model.objects.create_user(**user_data)
#
#     def test_registration_with_existing_email(self):
#         self.create_user(**self.user_data)
#         response = self.client.post(self.url, self.user_data, format='json')
#         self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
#         self.assertEqual(1, self.model.objects.count())
#
#     def test_registration_with_corrupt_data(self):
#         for key in self.invalid_values:
#             for value in self.invalid_values[key]:
#                 response = self.client.post(
#                     self.url,
#                     {
#                         **self.user_data,
#                         key: value
#                     },
#                     format='json'
#                 )
#                 self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
#                 self.assertEqual(self.model.objects.count(), 0)
#
#
# class UserRegistrationTestCase(AbstractRegistrationApiTestCase, APITestCase):
#     user_data = {
#         **AbstractRegistrationApiTestCase.user_data,
#     }
#
#     invalid_values = {
#         **AbstractRegistrationApiTestCase.invalid_values,
#     }
#
#     def create_user(self, **user_data):
#         super().create_user(
#             **user_data,
#         )
#
#
# class ExpertsApiTest(APITestCase):
#     def setUp(self):
#         self.user = mommy.make('accounts.User')
#         self.experts = mommy.make('accounts.User', _quantity=6)
#         self.moderator = mommy.make('accounts.User')
#
#     def test_list(self):
#         url = reverse('api:experts-list')
#
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#
#         self.client.force_authenticate(user=self.user)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#
#         self.client.logout()
#         self.client.force_authenticate(user=self.moderator)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['count'], 6)
#
#     def test_create(self):
#         url = reverse('api:experts-list')
#
#         data = {
#             'password': 'testpassword',
#             'email': 'testemail@mail.ru',
#             'username': 'testusernam',
#             'phone': '+79992223333'
#         }
#
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#
#         self.client.force_authenticate(user=self.user)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#
#         self.client.logout()
#         self.client.force_authenticate(user=self.moderator)
#         response = self.client.post(url, data=data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#
#     def test_detail_update(self):
#         url = reverse('api:experts-detail', kwargs={'pk': self.experts[0].pk})
#
#         # test detail
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#
#         self.client.force_authenticate(user=self.user)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#
#         self.client.logout()
#         self.client.force_authenticate(user=self.moderator)
#
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
