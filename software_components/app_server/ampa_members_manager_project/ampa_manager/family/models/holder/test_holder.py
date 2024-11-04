from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from model_bakery import baker

from ampa_manager.baker_recipes import bank_account_recipe
from .holder import Holder
from ..bank_account.bank_account import BankAccount
from ..parent import Parent
from ..state import State


class TestHolder(TestCase):
    def test_unique_holder_bank_account_constraint(self):
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        holder: Holder = baker.make(Holder, bank_account=bank_account)
        with self.assertRaises(IntegrityError):
            baker.make(Holder, parent=holder.parent, bank_account=holder.bank_account)

    def test_unique_order_in_a_year_constraint(self):
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        holder: Holder = baker.make(Holder, bank_account=bank_account)
        with self.assertRaises(IntegrityError):
            baker.make(
                Holder, authorization_order=holder.authorization_order, authorization_year=holder.authorization_year)

    def test_str(self):
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        holder: Holder = baker.make(Holder, bank_account=bank_account)
        self.assertEqual(str(holder), f'{holder.parent}, {holder.bank_account}')

    def test_clean(self):
        with self.assertRaises(ValidationError):
            parent: Parent = baker.make(Parent)
            bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
            holder: Holder = Holder(parent=parent, bank_account=bank_account, authorization_state=State.SIGNED)
            holder.clean()

    def test_authorization_full_number(self):
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        holder: Holder = baker.make(Holder, bank_account=bank_account)
        self.assertEqual(
            holder.authorization_full_number, f'{holder.authorization_year}/{holder.authorization_order:03}')

    def test_authorization_full_number_1_digit(self):
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        holder: Holder = baker.make(Holder, bank_account=bank_account, authorization_order=1)
        self.assertEqual(
            holder.authorization_full_number, f'{holder.authorization_year}/001')

    def test_authorization_full_number_3_digits(self):
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        holder: Holder = baker.make(Holder, bank_account=bank_account, authorization_order=123)
        self.assertEqual(
            holder.authorization_full_number, f'{holder.authorization_year}/123')

