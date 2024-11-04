from django.db.models import QuerySet
from django.test import TestCase
from model_bakery import baker

from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from .after_school_remittance import AfterSchoolRemittance
from ...no_after_school_edition_error import NoAfterSchoolEditionError


class TestAfterSchoolRemittanceManager(TestCase):
    def test_create_filled_no_after_school_editions(self):
        after_school_editions: QuerySet[AfterSchoolEdition] = AfterSchoolEdition.objects.none()
        with self.assertRaises(NoAfterSchoolEditionError):
            AfterSchoolRemittance.objects.create_filled(after_school_editions=after_school_editions)

    def test_create_filled_one_after_school_edition_one(self):
        after_school_edition: AfterSchoolEdition = baker.make(AfterSchoolEdition)
        after_school_edition_one: QuerySet[AfterSchoolEdition] = AfterSchoolEdition.objects.all()

        after_school_remittance: AfterSchoolRemittance = AfterSchoolRemittance.objects.create_filled(
            after_school_editions=after_school_edition_one)

        self.assertIsNone(after_school_remittance.name)
        self.assertIsNotNone(after_school_remittance.after_school_editions)
        self.assertEqual(list(after_school_remittance.after_school_editions.all()), list([after_school_edition]))
