from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.family.models.bank_account import BankAccount


class TestBankAccount(TestCase):
    def test_str(self):
        bank_account: BankAccount = baker.make(
            'BankAccount', swift_bic="BASKES2BXXX", iban="ES60 0049 1500 0512 3456 7892")
        self.assertEqual(str(bank_account), bank_account.iban)
