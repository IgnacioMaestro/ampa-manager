import datetime
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from model_bakery import baker


class TestCustodyRemittance(TestCase):
    timezone_now: datetime

    @classmethod
    def setUpTestData(cls):
        cls.timezone_now = timezone.now()

    @mock.patch('django.utils.timezone.now')
    def test_str_with_name(self, now):
        now.return_value = self.timezone_now
        name = 'name'
        custody_remittance = baker.make('CustodyRemittance', name=name)
        self.assertEqual(str(custody_remittance), name + '_' + self.timezone_now.strftime("%Y%m%d_%H%M%S"))

    @mock.patch('django.utils.timezone.now')
    def test_str_without_name(self, now):
        now.return_value = self.timezone_now
        custody_remittance = baker.make('CustodyRemittance')
        self.assertEqual(str(custody_remittance), '_' + self.timezone_now.strftime("%Y%m%d_%H%M%S"))
