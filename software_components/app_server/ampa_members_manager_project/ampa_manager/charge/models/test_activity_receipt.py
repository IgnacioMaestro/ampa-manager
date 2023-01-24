from django.test import TestCase
from model_bakery import baker

from ampa_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_manager.baker_recipes import bank_account_recipe
from ampa_manager.charge.models.activity_receipt import ActivityReceipt
from ampa_manager.charge.models.receipt_exceptions import NoBankAccountException
from ampa_manager.charge.receipt import Receipt
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.holder.holder import Holder


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

    def test_generate_receipt_with_default_bank_account_and_authorization(self):
        activity_receipt: ActivityReceipt = baker.make('ActivityReceipt')
        activity_receipt.activity_registrations.add(self.activity_registration)

        receipt: Receipt = activity_receipt.generate_receipt()

        holder: Holder = activity_receipt.activity_registrations.first().holder
        self.assertEqual(receipt.bank_account_owner, str(holder.parent))
        self.assertEqual(receipt.iban, str(holder.bank_account.iban))
        self.assertEqual(receipt.bic, str(holder.bank_account.swift_bic))
        self.assertIsNone(receipt.amount)
        self.assertEqual(receipt.authorization.number, holder.authorization_full_number)
        self.assertEqual(receipt.authorization.date, holder.authorization_sign_date)
