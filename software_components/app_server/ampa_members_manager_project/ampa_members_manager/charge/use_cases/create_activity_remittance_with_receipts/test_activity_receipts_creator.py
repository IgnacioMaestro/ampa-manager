from typing import List, Final

from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.activity.models.activity_payable_part import ActivityPayablePart
from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_members_manager.baker_recipes import activity_registration_with_payable_part
from ampa_members_manager.charge.use_cases.create_activity_remittance_with_receipts.activity_receipts_creator import \
    ActivityReceiptsCreator
from ampa_members_manager.charge.models.activity_receipt import ActivityReceipt
from ampa_members_manager.charge.models.activity_remittance import ActivityRemittance
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.tests.generator_adder import GeneratorAdder

GeneratorAdder.add_all()


class TestActivityReceiptsCreator(TestCase):
    ACTIVITY_REGISTRATION_COUNT: Final[int] = 3

    @classmethod
    def setUpTestData(cls):
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))

    def test_create_without_payable_parts(self):
        activity_remittance: ActivityRemittance = baker.make('ActivityRemittance')

        ActivityReceiptsCreator(activity_remittance).create()

        self.assertEqual(ActivityReceipt.objects.filter(remittance=activity_remittance).count(), 0)

    def test_create_activity_registrations_different_bank_accounts(self):
        activity_registrations: List[ActivityRegistration] = baker.make_recipe(
            activity_registration_with_payable_part, _quantity=self.ACTIVITY_REGISTRATION_COUNT)
        activity_remittance: ActivityRemittance = ActivityRemittance.create_filled(
            ActivityPayablePart.objects.all())

        ActivityReceiptsCreator(activity_remittance).create()

        self.assertEqual(
            self.ACTIVITY_REGISTRATION_COUNT, ActivityReceipt.objects.filter(remittance=activity_remittance).count())
        for activity_registration in activity_registrations:
            amount = activity_registration.payable_part.calculate_price(
                times=activity_registration.amount, membership=activity_registration.is_membership())
            ActivityReceipt.objects.get(activity_registrations__exact=activity_registration, amount=amount)

    def test_create_activity_registrations_same_bank_accounts(self):
        bank_account: BankAccount = baker.make('BankAccount')
        activity_registrations: List[ActivityRegistration] = baker.make_recipe(
            activity_registration_with_payable_part, _quantity=self.ACTIVITY_REGISTRATION_COUNT,
            bank_account=bank_account, amount=2.3)
        activity_remittance: ActivityRemittance = ActivityRemittance.create_filled(
            ActivityPayablePart.objects.all())

        ActivityReceiptsCreator(activity_remittance).create()

        self.assertEqual(ActivityReceipt.objects.count(), 1)
        activity_receipt = ActivityReceipt.objects.first()
        self.assertEqual(activity_registrations, list(activity_receipt.activity_registrations.all()))
        amount = 0
        for activity_registration in activity_registrations:
            amount += activity_registration.payable_part.calculate_price(
                times=activity_registration.amount, membership=activity_registration.is_membership())
        self.assertEqual(amount, activity_receipt.amount)

    def test_find_or_create_receipt_create(self):
        activity_remittance: ActivityRemittance = baker.make('ActivityRemittance')
        activity_registration: ActivityRegistration = baker.make_recipe(
            activity_registration_with_payable_part, amount=2.3)

        activity_receipt: ActivityReceipt = ActivityReceiptsCreator(activity_remittance).find_or_create_receipt(
            activity_registration)

        self.assertEqual(activity_receipt.remittance, activity_remittance)
        self.assertEqual(activity_receipt.amount, 0)

    def test_find_or_create_receipt_find(self):
        activity_remittance: ActivityRemittance = baker.make('ActivityRemittance')
        activity_registration: ActivityRegistration = baker.make_recipe(activity_registration_with_payable_part)
        previous_activity_receipt: ActivityReceipt = baker.make('ActivityReceipt', remittance=activity_remittance)
        previous_activity_receipt.activity_registrations.add(activity_registration)

        activity_receipt: ActivityReceipt = ActivityReceiptsCreator(activity_remittance).find_or_create_receipt(
            activity_registration)

        self.assertEqual(activity_receipt, previous_activity_receipt)

    def test_find_or_create_receipt_create_instead_other_receipt(self):
        activity_remittance: ActivityRemittance = baker.make('ActivityRemittance')
        bank_account: BankAccount = baker.make('BankAccount')
        activity_registration: ActivityRegistration = baker.make_recipe(
            activity_registration_with_payable_part, amount=2.3, bank_account=bank_account)
        other_activity_registration: ActivityRegistration = baker.make_recipe(
            activity_registration_with_payable_part, bank_account=bank_account)
        other_activity_receipt: ActivityReceipt = baker.make('ActivityReceipt')
        other_activity_receipt.activity_registrations.add(other_activity_registration)

        activity_receipt: ActivityReceipt = ActivityReceiptsCreator(activity_remittance).find_or_create_receipt(
            activity_registration)

        self.assertNotEqual(activity_receipt, other_activity_receipt)
        self.assertEqual(activity_receipt.remittance, activity_remittance)
        self.assertEqual(activity_receipt.amount, 0)
