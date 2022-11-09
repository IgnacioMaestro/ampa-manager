import phonenumbers
from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.baker_recipes import bank_account_recipe
from ampa_members_manager.family.models.authorization.authorization import Authorization
from ampa_members_manager.family.models.bank_account.bank_account import BankAccount
from ampa_members_manager.family.models.parent import Parent


class TestAuthorization(TestCase):
    def test_str(self):
        owner: Parent = baker.make('Parent', phone_number=phonenumbers.parse("695715902", 'ES'))
        bank_account: BankAccount = baker.make(
            'BankAccount', swift_bic="BASKES2BXXX", iban="ES60 0049 1500 0512 3456 7892", owner=owner)
        authorization: Authorization = baker.make('Authorization', bank_account=bank_account)
        self.assertEqual(
            str(authorization),
            f'{authorization.year}/{authorization.number}-{str(authorization.bank_account)}')

    def test_next_number_for_year_no_authorization_that_year_returns_one(self):
        number = Authorization.objects.next_number_for_year(2020)
        self.assertEqual(number, 1)

    def test_next_number_for_year_one_authorization_that_year_returns_value_plus_one(self):
        initial_number: int = 16
        year: int = 2020
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        baker.make('Authorization', bank_account=bank_account, year=year, number=str(initial_number))
        next_number = Authorization.objects.next_number_for_year(2020)
        self.assertEqual(next_number, initial_number + 1)

    def test_next_number_for_year_two_authorizations_that_year_returns_max_value_plus_one(self):
        initial_number: int = 16
        year: int = 2020
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        other_bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        baker.make('Authorization', bank_account=bank_account, year=year, number=str(initial_number))
        baker.make('Authorization', bank_account=other_bank_account, year=year, number='2')
        next_number = Authorization.objects.next_number_for_year(2020)
        self.assertEqual(next_number, initial_number + 1)

    def test_create_next_authorization(self):
        year = 2020
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        authorization: Authorization = Authorization.objects.create_next_authorization(year, bank_account)
        self.assertEqual(authorization.year, year)
        self.assertEqual(authorization.number, '1')
        self.assertEqual(authorization.bank_account, bank_account)
