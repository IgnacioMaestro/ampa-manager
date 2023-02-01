import datetime
from unittest import mock

from django.db.models import QuerySet
from django.test import TestCase
from django.utils import timezone
from model_bakery import baker

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.charge.models.custody.custody_remittance import CustodyRemittance
from ampa_manager.charge.no_custody_edition_error import NoCustodyEditionError


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

    def test_create_filled_no_custody_editions(self):
        custody_editions: QuerySet[CustodyEdition] = CustodyEdition.objects.none()
        with self.assertRaises(NoCustodyEditionError):
            CustodyRemittance.create_filled(custody_editions=custody_editions)

    def test_create_filled_one_custody_edition_one(self):
        custody_edition: CustodyEdition = baker.make('CustodyEdition')
        custody_edition_one: QuerySet[CustodyEdition] = CustodyEdition.objects.all()

        custody_remittance: CustodyRemittance = CustodyRemittance.create_filled(
            custody_editions=custody_edition_one)

        self.assertIsNone(custody_remittance.name)
        self.assertIsNotNone(custody_remittance.custody_editions)
        self.assertEqual(list(custody_remittance.custody_editions.all()), list([custody_edition]))
