from typing import Final

from django.test import TestCase
from model_bakery import baker

from ampa_manager.baker_recipes import bank_account_recipe, membership_receipt_family_bank_account_recipe
from ampa_manager.charge.models.membership_receipt import MembershipReceipt
from ampa_manager.charge.models.receipt_exceptions import NoBankAccountException, NoFeeForCourseException
from ampa_manager.charge.receipt import Receipt
from ampa_manager.family.models.authorization.authorization import Authorization
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.family import Family


class TestMembershipReceipt(TestCase):
    FEE: Final[int] = 30

    def test_generate_receipt_no_default_bank_account(self):
        membership_receipt: MembershipReceipt = baker.make('MembershipReceipt')
        with self.assertRaises(NoBankAccountException):
            membership_receipt.generate_receipt()

    def test_generate_receipt_no_fee_for_course(self):
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        family: Family = baker.make('Family', default_bank_account=bank_account)
        membership_receipt: MembershipReceipt = baker.make('MembershipReceipt', family=family)
        with self.assertRaises(NoFeeForCourseException):
            membership_receipt.generate_receipt()

    def test_generate_receipt_with_default_bank_account_no_authorization(self):
        membership_receipt: MembershipReceipt = baker.make_recipe(membership_receipt_family_bank_account_recipe)
        baker.make('Fee', academic_course=membership_receipt.remittance.course, amount=self.FEE)

        receipt: Receipt = membership_receipt.generate_receipt()

        self.assert_params_without_authorization(membership_receipt, receipt)
        self.assertIsNone(receipt.authorization)

    def test_generate_receipt_with_default_bank_account_and_authorization(self):
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        authorization: Authorization = baker.make('Authorization', bank_account=bank_account)
        family: Family = baker.make('Family', default_bank_account=bank_account)
        membership_receipt: MembershipReceipt = baker.make('MembershipReceipt', family=family)
        baker.make('Fee', academic_course=membership_receipt.remittance.course, amount=self.FEE)

        receipt: Receipt = membership_receipt.generate_receipt()

        self.assert_params_without_authorization(membership_receipt, receipt)
        self.assertEqual(receipt.authorization.number, authorization.full_number)

    def assert_params_without_authorization(self, membership_receipt, receipt):
        self.assertEqual(receipt.bank_account_owner, str(membership_receipt.family.default_bank_account.owner))
        self.assertEqual(receipt.iban, str(membership_receipt.family.default_bank_account.iban))
        self.assertEqual(receipt.amount, self.FEE)
