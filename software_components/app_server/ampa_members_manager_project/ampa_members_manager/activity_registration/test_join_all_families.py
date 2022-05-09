import phonenumbers
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.activity_registration.join_all_families import JoinAllFamilies
from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.parent import Parent


class TestJoinAllFamilies(TestCase):
    def setUp(self):
        self.single_activity: SingleActivity = baker.make('SingleActivity')
        parent: Parent = baker.make('Parent', phone_number=phonenumbers.parse("695715902", 'ES'))
        self.bank_account: BankAccount = baker.make(
            'BankAccount', swift_bic="BASKES2BXXX", iban="ES60 0049 1500 0512 3456 7892", owner=parent)

    def test_join_no_families(self):
        JoinAllFamilies.join(self.single_activity)
        self.assertEqual(ActivityRegistration.objects.count(), 0)

    def test_join_one_family(self):
        baker.make('Family', default_bank_account=self.bank_account)
        JoinAllFamilies.join(self.single_activity)
        self.assertEqual(ActivityRegistration.objects.count(), 1)

    def test_join_more_than_one_family(self):
        baker.make('Family', default_bank_account=self.bank_account, _quantity=3)
        JoinAllFamilies.join(self.single_activity)
        self.assertEqual(ActivityRegistration.objects.count(), 3)

    def test_join_family(self):
        family: Family = baker.make('Family', default_bank_account=self.bank_account)
        JoinAllFamilies.join_family(family, self.single_activity)
        self.assertEqual(ActivityRegistration.objects.count(), 1)
        activity_registration: ActivityRegistration = ActivityRegistration.objects.all().first()
        self.assertEqual(activity_registration.registered_family, family)
        self.assertEqual(activity_registration.single_activity, self.single_activity)
        self.assertEqual(activity_registration.bank_account, self.bank_account)
