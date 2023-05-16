from django.db.models import QuerySet
from django.test import TestCase
from model_bakery import baker

from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from ampa_manager.charge.no_camps_edition_error import NoCampsEditionError
from .camps_remittance import CampsRemittance


class TestCampsRemittanceManager(TestCase):
    def test_create_filled_no_camps_editions(self):
        camps_editions: QuerySet[CampsEdition] = CampsEdition.objects.none()
        with self.assertRaises(NoCampsEditionError):
            CampsRemittance.objects.create_filled(camps_editions=camps_editions)

    def test_create_filled_one_camps_edition_one(self):
        camps_edition: CampsEdition = baker.make('CampsEdition')
        camps_edition_one: QuerySet[CampsEdition] = CampsEdition.objects.all()

        camps_remittance: CampsRemittance = CampsRemittance.objects.create_filled(
            camps_editions=camps_edition_one)

        self.assertIsNone(camps_remittance.name)
        self.assertIsNotNone(camps_remittance.camps_editions)
        self.assertEqual(list(camps_remittance.camps_editions.all()), list([camps_edition]))
