from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from ampa_manager.baker_recipes import bank_account_recipe
from ..bank_account.bank_account import BankAccount
from .holder import Holder
from ..parent import Parent
from ..state import State


class TestHolder(TestCase):
    def test_unique_holder_bank_account_constraint(self):
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        holder: Holder = baker.make('Holder', bank_account=bank_account)
        with self.assertRaises(IntegrityError):
            baker.make('Holder', parent=holder.parent, bank_account=holder.bank_account)

    def test_unique_order_in_a_year_constraint(self):
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        holder: Holder = baker.make('Holder', bank_account=bank_account)
        with self.assertRaises(IntegrityError):
            baker.make('Holder', authorization_order=holder.authorization_order, year=holder.year)

    def test_str(self):
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        holder: Holder = baker.make('Holder', bank_account=bank_account)
        self.assertEqual(str(holder), f'{holder.parent}-{holder.bank_account}')

    def test_clean(self):
        with self.assertRaises(ValidationError):
            parent: Parent = baker.make('Parent')
            bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
            holder: Holder = Holder(parent=parent, bank_account=bank_account, state=State.SIGNED)
            holder.clean()

    def test_full_number(self):
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        holder: Holder = baker.make('Holder', bank_account=bank_account)
        self.assertEqual(holder.full_number, f'{holder.year}/{holder.authorization_order:03}')
