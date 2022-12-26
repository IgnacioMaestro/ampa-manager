from django.test import TestCase
from model_bakery import baker

from ampa_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_manager.baker_recipes import bank_account_recipe
from ampa_manager.charge.models.activity_receipt import ActivityReceipt
from ampa_manager.charge.models.receipt_exceptions import NoBankAccountException
from ampa_manager.charge.receipt import Receipt
from ampa_manager.family.models.authorization.authorization import Authorization
from ampa_manager.family.models.bank_account.bank_account import BankAccount


class TestActivityReceipt(TestCase):
    bank_account: BankAccount
    activity_registration: ActivityRegistration

    @classmethod
    def setUpTestData(cls):
        cls.bank_account = baker.make_recipe(bank_account_recipe)
        cls.activity_registration = baker.make('ActivityRegistration', bank_account=cls.bank_account)

    def test_generate_receipt_no_activity_registration(self):
        activity_receipt: ActivityReceipt = baker.make('ActivityReceipt')
        with self.assertRaises(NoBankAccountException):
            activity_receipt.generate_receipt()

    def test_generate_receipt_with_default_bank_account_no_authorization(self):
        activity_receipt: ActivityReceipt = baker.make('ActivityReceipt')
        activity_receipt.activity_registrations.add(self.activity_registration)

        receipt: Receipt = activity_receipt.generate_receipt()

        self.assert_params_without_authorization(receipt)
        self.assertIsNone(receipt.authorization)

    def test_generate_receipt_with_default_bank_account_and_authorization(self):
        authorization: Authorization = baker.make('Authorization', bank_account=self.bank_account)
        activity_receipt: ActivityReceipt = baker.make('ActivityReceipt')
        activity_receipt.activity_registrations.add(self.activity_registration)

        receipt: Receipt = activity_receipt.generate_receipt()

        self.assert_params_without_authorization(receipt)
        self.assertEqual(receipt.authorization.number, authorization.full_number)
        self.assertEqual(receipt.authorization.date, authorization.sign_date)
        self.assertEqual(receipt.authorization.date, authorization.sign_date)

    def assert_params_without_authorization(self, receipt: Receipt):
        self.assertEqual(receipt.bank_account_owner, str(self.bank_account.owner))
        self.assertEqual(receipt.iban, str(self.bank_account.iban))
        self.assertIsNone(receipt.amount)
