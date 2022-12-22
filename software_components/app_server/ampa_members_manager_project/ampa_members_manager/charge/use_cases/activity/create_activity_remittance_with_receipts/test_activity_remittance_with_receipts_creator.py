from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.activity.models.activity_period import ActivityPeriod
from ampa_members_manager.charge.use_cases.activity.create_activity_remittance_with_receipts.activity_remittance_with_receipts_creator import \
    ActivityRemittanceWithReceiptsCreator
from ampa_members_manager.charge.models.activity_receipt import ActivityReceipt
from ampa_members_manager.charge.no_activity_period_error import NoActivityPeriodError
from ampa_members_manager.tests.generator_adder import GeneratorAdder

GeneratorAdder.add_all()


class TestActivityRemittanceWithReceiptsCreator(TestCase):
    @classmethod
    def setUpTestData(cls):
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))

    def test_create_no_activity_period(self):
        with self.assertRaises(NoActivityPeriodError):
            ActivityRemittanceWithReceiptsCreator(ActivityPeriod.objects.all()).create()

    def test_create_activity_registrations_same_bank_accounts(self):
        baker.make('ActivityRegistration', bank_account=baker.make('BankAccount'))

        ActivityRemittanceWithReceiptsCreator(ActivityPeriod.objects.all()).create()

        self.assertEqual(1, ActivityReceipt.objects.count())
