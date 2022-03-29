import phonenumbers
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.parent import Parent


class TestBankAccount(TestCase):
    def test_str(self):
        owner: Parent = baker.make('Parent', phone_number=phonenumbers.parse("695715902", 'ES'))
        bank_account: BankAccount = baker.make(
            'BankAccount', swift_bic="BASKES2BXXX", iban="ES60 0049 1500 0512 3456 7892", owner=owner)
        self.assertEqual(str(bank_account), bank_account.iban)
