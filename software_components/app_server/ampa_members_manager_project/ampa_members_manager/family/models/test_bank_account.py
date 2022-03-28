from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.family.models.bank_account import BankAccount


class TestBankAccount(TestCase):
    def test_str(self):
        bank_account: BankAccount = baker.make('BankAccount')
        self.assertEqual(str(bank_account), bank_account.iban)
