from django.test import TestCase
from model_bakery import baker

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.baker_recipes import bank_account_recipe
from ampa_manager.charge.models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from ampa_manager.charge.models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ampa_manager.charge.no_after_school_edition_error import NoAfterSchoolEditionError
from ampa_manager.charge.use_cases.after_school.after_school_remittance_creator.after_school_remittance_creator import \
    AfterSchoolRemittanceCreator


class TestAfterSchoolRemittanceCreator(TestCase):
    def test_create_with_fraction_no_after_school_edition(self):
        with self.assertRaises(NoAfterSchoolEditionError):
            AfterSchoolRemittanceCreator(AfterSchoolEdition.objects.none()).create_full()
        with self.assertRaises(NoAfterSchoolEditionError):
            AfterSchoolRemittanceCreator(AfterSchoolEdition.objects.none()).create_half()
        with self.assertRaises(NoAfterSchoolEditionError):
            AfterSchoolRemittanceCreator(AfterSchoolEdition.objects.none()).create_left()

    def test_create_half_after_school_edition_with_after_school_registration(self):
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))
        after_school_registration: AfterSchoolRegistration = baker.make(
            'AfterSchoolRegistration', bank_account=baker.make_recipe(bank_account_recipe))

        after_school_remittance: AfterSchoolRemittance = AfterSchoolRemittanceCreator(
            AfterSchoolEdition.objects.all()).create_half()

        self.assertIsNotNone(after_school_remittance)
        after_school_receipt: AfterSchoolReceipt = AfterSchoolReceipt.objects.get(remittance=after_school_remittance)
        self.assertAlmostEqual(
            after_school_receipt.amount, after_school_registration.calculate_price() / 2, 2)

    def test_create_half_after_school_edition_with_two_after_school_registrations(self):
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))
        after_school_edition: AfterSchoolEdition = baker.make('AfterSchoolEdition')
        baker.make(
            'AfterSchoolRegistration', bank_account=baker.make_recipe(bank_account_recipe),
            after_school_edition=after_school_edition, _quantity=2)

        after_school_remittance: AfterSchoolRemittance = AfterSchoolRemittanceCreator(
            AfterSchoolEdition.objects.all()).create_half()

        self.assertIsNotNone(after_school_remittance)
        self.assertEqual(AfterSchoolReceipt.objects.filter(remittance=after_school_remittance).count(), 2)
