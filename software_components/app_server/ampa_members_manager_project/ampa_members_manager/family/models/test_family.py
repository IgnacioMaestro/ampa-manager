from typing import List

import phonenumbers
from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.family.models.bank_account.bank_account import BankAccount
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.parent import Parent


class TestFamily(TestCase):

    def test_create_unique_surnames(self):
        baker.make('Family')
        Family.objects.create(surnames="surnames")

    def test_str(self):
        family: Family = baker.make('Family')
        self.assertEqual(str(family), str(family.surnames))

    def test_all_families_no_families(self):
        self.assertQuerysetEqual(Family.all_families(), Family.objects.none())

    def test_all_families_one_family(self):
        family: Family = baker.make('Family')
        self.assertQuerysetEqual(Family.all_families(), [family])

    def test_all_families_more_than_one_family(self):
        families: List[Family] = baker.make('Family', _quantity=3)
        self.assertListEqual(list(Family.all_families()), families)

    def test_all_families_with_bank_account_no_families(self):
        self.assertQuerysetEqual(Family.objects.with_default_bank_account(), Family.objects.none())

    def test_all_families_with_bank_account_one_family(self):
        parent: Parent = baker.make('Parent', phone_number=phonenumbers.parse("695715902", 'ES'))
        bank_account: BankAccount = baker.make(
            'BankAccount', swift_bic="BASKES2BXXX", iban="ES60 0049 1500 0512 3456 7892", owner=parent)
        family: Family = baker.make('Family', default_bank_account=bank_account)
        self.assertQuerysetEqual(Family.objects.with_default_bank_account(), [family])

    def test_all_families_with_bank_account_more_than_one_family(self):
        parent: Parent = baker.make('Parent', phone_number=phonenumbers.parse("695715902", 'ES'))
        bank_account: BankAccount = baker.make(
            'BankAccount', swift_bic="BASKES2BXXX", iban="ES60 0049 1500 0512 3456 7892", owner=parent)
        families: List[Family] = baker.make('Family', _quantity=3)
        families[0].default_bank_account = bank_account
        families[0].save()
        families[1].default_bank_account = bank_account
        families[1].save()

        self.assertEqual(len(Family.objects.with_default_bank_account()), 2)
