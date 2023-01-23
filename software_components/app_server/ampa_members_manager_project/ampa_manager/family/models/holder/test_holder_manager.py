from django.test import TestCase
from model_bakery import baker

from ampa_manager.baker_recipes import bank_account_recipe
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.holder.holder import Holder


class TestHolderManager(TestCase):
    def test_next_order_for_year_no_authorization_that_year_returns_one(self):
        order = Holder.objects.next_order_for_year(2020)
        self.assertEqual(order, 1)

    def test_next_order_for_year_one_authorization_that_year_returns_value_plus_one(self):
        initial_order: int = 16
        year: int = 2020
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        baker.make('Holder', bank_account=bank_account, year=year, order=initial_order)
        next_number = Holder.objects.next_order_for_year(2020)
        self.assertEqual(next_number, initial_order + 1)

    def test_next_order_for_year_two_authorizations_that_year_returns_max_value_plus_one(self):
        initial_order: int = 16
        year: int = 2020
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        other_bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        baker.make('Holder', bank_account=bank_account, year=year, order=initial_order)
        baker.make('Holder', bank_account=other_bank_account, year=year, order=2)
        next_number = Holder.objects.next_order_for_year(2020)
        self.assertEqual(next_number, initial_order + 1)
