from typing import Final

from django.test import TestCase
from model_bakery import baker

from ampa_manager.baker_recipes import bank_account_recipe
from ampa_manager.charge.models.membership_receipt import MembershipReceipt
from ampa_manager.charge.models.receipt_exceptions import NoFeeForCourseException, \
    NoHolderException
from ampa_manager.charge.receipt import Receipt
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder


class TestMembershipReceipt(TestCase):
    FEE: Final[int] = 30

    def test_generate_receipt_no_default_bank_account(self):
        membership_receipt: MembershipReceipt = baker.make('MembershipReceipt')
        with self.assertRaises(NoHolderException):
            membership_receipt.generate_receipt()

    def test_generate_receipt_no_fee_for_course(self):
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        holder: Holder = baker.make('Holder', bank_account=bank_account)
        family: Family = baker.make('Family', membership_holder=holder)
        membership_receipt: MembershipReceipt = baker.make('MembershipReceipt', family=family)
        with self.assertRaises(NoFeeForCourseException):
            membership_receipt.generate_receipt()

    def test_generate_receipt_with_default_bank_account_and_authorization(self):
        baker.make('BankBicCode', bank_code='2095')
        holder: Holder = baker.make('Holder')
        family: Family = baker.make('Family', membership_holder=holder)
        membership_receipt: MembershipReceipt = baker.make('MembershipReceipt', family=family)
        baker.make('Fee', academic_course=membership_receipt.remittance.course, amount=self.FEE)

        receipt: Receipt = membership_receipt.generate_receipt()

        self.assertEqual(receipt.bank_account_owner, holder.parent.full_name)
        self.assertEqual(receipt.iban, str(holder.bank_account.iban))
        self.assertEqual(receipt.bic, str(holder.bank_account.swift_bic))
        self.assertEqual(receipt.amount, self.FEE)
        self.assertEqual(receipt.authorization.number, holder.authorization_full_number)
