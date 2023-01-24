from django.test import TestCase
from model_bakery import baker

from ampa_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_manager.charge.models.activity_receipt import ActivityReceipt
from ampa_manager.charge.models.receipt_exceptions import NoBankAccountException
from ampa_manager.charge.receipt import Receipt
from ampa_manager.family.models.bank_account.bank_bic_code import BankBicCode
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.tests.generator_adder import iban_generator

baker.generators.add('localflavor.generic.models.IBANField', iban_generator)


class TestActivityReceipt(TestCase):
    activity_registration: ActivityRegistration

    @classmethod
    def setUpTestData(cls):
        baker.make('BankBicCode', bank_code='2095')
        cls.activity_registration = baker.make('ActivityRegistration')

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
