from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.charge.use_cases.create_charge_group_with_charges.charge_group_with_charges_creator import \
    ChargeGroupWithChargesCreator
from ampa_members_manager.charge.models.charge import Charge
from ampa_members_manager.charge.no_single_activity_error import NoSingleActivityError
from ampa_members_manager.tests.generator_adder import GeneratorAdder

GeneratorAdder.add_all()


class TestChargeGroupWithChargesCreator(TestCase):
    @classmethod
    def setUpTestData(cls):
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))

    def test_create_no_single_activity(self):
        with self.assertRaises(NoSingleActivityError):
            ChargeGroupWithChargesCreator(SingleActivity.objects.all()).create()

    def test_create_activity_registrations_same_bank_accounts(self):
        baker.make('ActivityRegistration', bank_account=baker.make('BankAccount'))

        ChargeGroupWithChargesCreator(SingleActivity.objects.all()).create()

        self.assertEqual(1, Charge.objects.count())
