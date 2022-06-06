from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.tests.generator_adder import GeneratorAdder

GeneratorAdder.add_all()


class TestBankAccount(TestCase):
    def test_str(self):
        bank_account: BankAccount = baker.make('BankAccount')
        self.assertEqual(str(bank_account), f'{bank_account.iban} {bank_account.owner}')
