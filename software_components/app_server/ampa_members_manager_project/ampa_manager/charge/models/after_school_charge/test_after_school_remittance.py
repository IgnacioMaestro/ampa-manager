import datetime
from unittest import mock

from django.db.models import QuerySet
from django.test import TestCase
from django.utils import timezone
from model_bakery import baker

from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.charge.models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ampa_manager.charge.no_after_school_edition_error import NoAfterSchoolEditionError


class TestAfterSchoolRemittance(TestCase):
    timezone_now: datetime

    @classmethod
    def setUpTestData(cls):
        cls.timezone_now = timezone.now()

    @mock.patch('django.utils.timezone.now')
    def test_str_with_name(self, now):
        now.return_value = self.timezone_now
        name = 'name'
        after_school_remittance = baker.make('AfterSchoolRemittance', name=name)
        self.assertEqual(str(after_school_remittance), name + '_' + self.timezone_now.strftime("%Y%m%d_%H%M%S"))

    @mock.patch('django.utils.timezone.now')
    def test_str_without_name(self, now):
        now.return_value = self.timezone_now
        after_school_remittance = baker.make('AfterSchoolRemittance')
        self.assertEqual(str(after_school_remittance), '_' + self.timezone_now.strftime("%Y%m%d_%H%M%S"))

    def test_create_filled_no_after_school_editions(self):
        after_school_editions: QuerySet[AfterSchoolEdition] = AfterSchoolEdition.objects.none()
        with self.assertRaises(NoAfterSchoolEditionError):
            AfterSchoolRemittance.create_filled(after_school_editions=after_school_editions)

    def test_create_filled_one_after_school_edition_one(self):
        after_school_edition: AfterSchoolEdition = baker.make('AfterSchoolEdition')
        after_school_edition_one: QuerySet[AfterSchoolEdition] = AfterSchoolEdition.objects.all()

        after_school_remittance: AfterSchoolRemittance = AfterSchoolRemittance.create_filled(
            after_school_editions=after_school_edition_one)

        self.assertIsNone(after_school_remittance.name)
        self.assertIsNotNone(after_school_remittance.after_school_editions)
        self.assertEqual(list(after_school_remittance.after_school_editions.all()), list([after_school_edition]))
