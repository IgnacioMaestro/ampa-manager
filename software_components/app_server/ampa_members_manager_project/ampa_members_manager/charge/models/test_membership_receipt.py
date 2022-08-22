from typing import Final

from django.test import TestCase
from model_bakery import baker

from ampa_members_manager.charge.models.membership_receipt import MembershipReceipt, NoFamilyBankAccountException, \
    NoFeeForCourseException
from ampa_members_manager.charge.receipt import Receipt
from ampa_members_manager.family.models.authorization import Authorization
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.baker_recipes import bank_account_recipe, membership_receipt_family_bank_account_recipe


class TestMembershipReceipt(TestCase):
    FEE: Final[int] = 30

    def test_generate_receipt_no_default_bank_account(self):
        membership_receipt: MembershipReceipt = baker.make('MembershipReceipt')
        with self.assertRaises(NoFamilyBankAccountException):
            membership_receipt.generate_receipt()

    def test_generate_receipt_no_fee_for_course(self):
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        family: Family = baker.make('Family', default_bank_account=bank_account)
        membership_receipt: MembershipReceipt = baker.make('MembershipReceipt', family=family)
        with self.assertRaises(NoFeeForCourseException):
            membership_receipt.generate_receipt()

    def test_generate_receipt_with_default_bank_account_no_authorization(self):
        membership_receipt: MembershipReceipt = baker.make_recipe(membership_receipt_family_bank_account_recipe)
        membership_receipt.remittance.course.fee = self.FEE
        membership_receipt.remittance.course.save()
        receipt: Receipt = membership_receipt.generate_receipt()
        self.assert_params_without_authorization(membership_receipt, receipt)
        self.assertEqual(receipt.authorization, Receipt.NO_AUTHORIZATION_MESSAGE)

    def test_generate_receipt_with_default_bank_account_and_authorization(self):
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        authorization: Authorization = baker.make('Authorization', bank_account=bank_account)
        family: Family = baker.make('Family', default_bank_account=bank_account)
        membership_receipt: MembershipReceipt = baker.make('MembershipReceipt', family=family)
        membership_receipt.remittance.course.fee = self.FEE
        membership_receipt.remittance.course.save()
        receipt: Receipt = membership_receipt.generate_receipt()
        self.assert_params_without_authorization(membership_receipt, receipt)
        self.assertEqual(receipt.authorization, authorization.number)

    def assert_params_without_authorization(self, membership_receipt, receipt):
        self.assertEqual(receipt.bank_account_owner, str(membership_receipt.family.default_bank_account.owner))
        self.assertEqual(receipt.iban, str(membership_receipt.family.default_bank_account.iban))
        self.assertEqual(receipt.amount, self.FEE)
