import datetime

from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.baker_recipes import bank_account_recipe
from ampa_members_manager.charge.receipt import Receipt
from ampa_members_manager.family.models.authorization.authorization import Authorization
from ampa_members_manager.family.models.bank_account.bank_account import BankAccount


class TestAuthorization(TestCase):
    def test_str_1_digit(self):
        authorization: Authorization = baker.make(
            'Authorization', order=1, bank_account=baker.make_recipe(bank_account_recipe))
        self.assertEqual(
            str(authorization),
            f'{authorization.year}/001-{str(authorization.bank_account)}')

    def test_str_3_digits(self):
        authorization: Authorization = baker.make(
            'Authorization', order=123, bank_account=baker.make_recipe(bank_account_recipe))
        self.assertEqual(
            str(authorization),
            f'{authorization.year}/123-{str(authorization.bank_account)}')

    def test_next_order_for_year_no_authorization_that_year_returns_one(self):
        order = Authorization.objects.next_order_for_year(2020)
        self.assertEqual(order, 1)

    def test_next_order_for_year_one_authorization_that_year_returns_value_plus_one(self):
        initial_order: int = 16
        year: int = 2020
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        baker.make('Authorization', bank_account=bank_account, year=year, order=initial_order)
        next_number = Authorization.objects.next_order_for_year(2020)
        self.assertEqual(next_number, initial_order + 1)

    def test_next_order_for_year_two_authorizations_that_year_returns_max_value_plus_one(self):
        initial_order: int = 16
        year: int = 2020
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        other_bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        baker.make('Authorization', bank_account=bank_account, year=year, order=initial_order)
        baker.make('Authorization', bank_account=other_bank_account, year=year, order=2)
        next_number = Authorization.objects.next_order_for_year(2020)
        self.assertEqual(next_number, initial_order + 1)

    def test_create_next_authorization(self):
        year = 2020
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        authorization: Authorization = Authorization.objects.create_next_authorization(year, bank_account)
        self.assertEqual(authorization.year, year)
        self.assertEqual(authorization.order, 1)
        self.assertEqual(authorization.number, '2020/001')
        self.assertEqual(authorization.bank_account, bank_account)

    def test_generate_receipt_authorization_no_authorization(self):
        number, date = Authorization.generate_receipt_authorization(baker.make_recipe(bank_account_recipe))

        self.assertEqual(number, Receipt.NO_AUTHORIZATION_MESSAGE)
        self.assertIsNone(date)

    def test_generate_receipt_authorization_authorization(self):
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        authorization: Authorization = baker.make('Authorization', bank_account=bank_account)

        number, date = Authorization.generate_receipt_authorization(bank_account)

        self.assertEqual(number, authorization.full_number)
        self.assertEqual(date, datetime.date(authorization.date.year, authorization.date.month, authorization.date.day))
