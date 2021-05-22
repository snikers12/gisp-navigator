import pytz
from django.test import TestCase

from regions.models import FederalSubject


class FederalSubjectModelTestCase(TestCase):

    def test_default_timezone(self):
        yakutia = FederalSubject.objects.get(name__icontains='якутия')
        self.assertEqual(yakutia.default_timezone, pytz.timezone('Asia/Yakutsk'))

        moscow = FederalSubject.objects.get(name__icontains='москва')
        self.assertEqual(moscow.default_timezone, pytz.timezone('Europe/Moscow'))
