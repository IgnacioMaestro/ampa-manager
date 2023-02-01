from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition


class TestCustodyEdition(TestCase):
    def test_meet_a_constraint(self):
        baker.make('CustodyEdition')

        custody_edition: CustodyEdition = baker.make('CustodyEdition')

        self.assertIsNotNone(custody_edition)

    def test_no_meet_a_constraint(self):
        custody_edition: CustodyEdition = baker.make('CustodyEdition')

        with self.assertRaises(IntegrityError):
            baker.make(
                'CustodyEdition', academic_course=custody_edition.academic_course,
                period=custody_edition.period, primary=custody_edition.primary)
