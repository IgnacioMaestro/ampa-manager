from django.db.models import QuerySet
from django.test import TestCase
from model_bakery import baker

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.charge.models.custody.custody_remittance import CustodyRemittance
from ampa_manager.charge.no_custody_edition_error import NoCustodyEditionError


class TestCustodyRemittanceManager(TestCase):
    def test_create_filled_no_custody_editions(self):
        custody_editions: QuerySet[CustodyEdition] = CustodyEdition.objects.none()
        with self.assertRaises(NoCustodyEditionError):
            CustodyRemittance.objects.create_filled(custody_editions=custody_editions)

    def test_create_filled_one_custody_edition_one(self):
        custody_edition: CustodyEdition = baker.make(CustodyEdition)
        custody_edition_one: QuerySet[CustodyEdition] = CustodyEdition.objects.all()

        custody_remittance: CustodyRemittance = CustodyRemittance.objects.create_filled(
            custody_editions=custody_edition_one)

        self.assertIsNone(custody_remittance.name)
        self.assertIsNotNone(custody_remittance.custody_editions)
        self.assertEqual(list(custody_remittance.custody_editions.all()), list([custody_edition]))
