from typing import List, Final

from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_members_manager.charge.use_cases.create_charge_group_with_charges.charges_creator import ChargesCreator
from ampa_members_manager.charge.models.charge import Charge
from ampa_members_manager.charge.models.charge_group import ChargeGroup
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.tests.generator_adder import GeneratorAdder

GeneratorAdder.add_all()


class TestChargesCreator(TestCase):
    ACTIVITY_REGISTRATION_COUNT: Final[int] = 3

    @classmethod
    def setUpTestData(cls):
        ActiveCourse.objects.create(course=baker.make('AcademicCourse'))

    def test_create_charge_group_without_single_activities(self):
        charge_group: ChargeGroup = baker.make('ChargeGroup')

        ChargesCreator(charge_group).create()

        self.assertEqual(Charge.objects.filter(group=charge_group).count(), 0)

    def test_create_activity_registrations_different_bank_accounts(self):
        activity_registrations: List[ActivityRegistration] = baker.make(
            'ActivityRegistration', _quantity=self.ACTIVITY_REGISTRATION_COUNT)
        charge_group: ChargeGroup = ChargeGroup.create_filled_charge_group(SingleActivity.objects.all())

        ChargesCreator(charge_group).create()

        self.assertEqual(self.ACTIVITY_REGISTRATION_COUNT, Charge.objects.filter(group=charge_group).count())
        for activity_registration in activity_registrations:
            amount = activity_registration.single_activity.calculate_price(
                times=activity_registration.amount, membership=activity_registration.is_membership())
            Charge.objects.get(activity_registrations__exact=activity_registration, amount=amount)

    def test_create_activity_registrations_same_bank_accounts(self):
        bank_account: BankAccount = baker.make('BankAccount')
        activity_registrations: List[ActivityRegistration] = baker.make(
            'ActivityRegistration', _quantity=self.ACTIVITY_REGISTRATION_COUNT, bank_account=bank_account)
        charge_group: ChargeGroup = ChargeGroup.create_filled_charge_group(SingleActivity.objects.all())

        ChargesCreator(charge_group).create()

        self.assertEqual(Charge.objects.count(), 1)
        charge = Charge.objects.first()
        self.assertEqual(activity_registrations, list(charge.activity_registrations.all()))
        amount = 0
        for activity_registration in activity_registrations:
            amount += activity_registration.single_activity.calculate_price(
                times=activity_registration.amount, membership=activity_registration.is_membership())
        self.assertEqual(amount, charge.amount)

    def test_find_or_create_charge_create(self):
        charge_group: ChargeGroup = baker.make('ChargeGroup')
        activity_registration: ActivityRegistration = baker.make('ActivityRegistration')
        charge: Charge = ChargesCreator(charge_group).find_or_create_charge(activity_registration)
        self.assertEqual(charge.group, charge_group)

    def test_find_or_create_charge_find(self):
        charge_group: ChargeGroup = baker.make('ChargeGroup')
        activity_registration: ActivityRegistration = baker.make('ActivityRegistration')
        previous_charge: Charge = baker.make('Charge', group=charge_group)
        previous_charge.activity_registrations.add(activity_registration)
        charge: Charge = ChargesCreator(charge_group).find_or_create_charge(activity_registration)
        self.assertEqual(charge, previous_charge)

    def test_find_or_create_charge_create_instead_other_charge(self):
        charge_group: ChargeGroup = baker.make('ChargeGroup')
        bank_account: BankAccount = baker.make('BankAccount')
        activity_registration: ActivityRegistration = baker.make('ActivityRegistration', bank_account=bank_account)
        other_activity_registration: ActivityRegistration = baker.make(
            'ActivityRegistration', bank_account=bank_account)
        other_charge: Charge = baker.make('Charge')
        other_charge.activity_registrations.add(other_activity_registration)
        charge: Charge = ChargesCreator(charge_group).find_or_create_charge(activity_registration)
        self.assertNotEqual(charge, other_charge)
        self.assertEqual(charge.group, charge_group)
