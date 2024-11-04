import datetime
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from model_bakery import baker

from .camps_remittance import CampsRemittance


class TestCampsRemittance(TestCase):
    timezone_now: datetime

    @classmethod
    def setUpTestData(cls):
        cls.timezone_now = timezone.now()

    @mock.patch('django.utils.timezone.now')
    def test_str_with_name(self, now):
        now.return_value = self.timezone_now
        name = 'name'
        camps_remittance: CampsRemittance = baker.make(CampsRemittance, name=name)
        self.assertEqual(str(camps_remittance), name + '_' + self.timezone_now.strftime("%Y%m%d_%H%M%S"))

    @mock.patch('django.utils.timezone.now')
    def test_str_without_name(self, now):
        now.return_value = self.timezone_now
        camps_remittance: CampsRemittance = baker.make(CampsRemittance)
        self.assertEqual(str(camps_remittance), '_' + self.timezone_now.strftime("%Y%m%d_%H%M%S"))
