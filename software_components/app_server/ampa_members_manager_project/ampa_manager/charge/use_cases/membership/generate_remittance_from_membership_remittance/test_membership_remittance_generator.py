from typing import Final

from django.test import TestCase
from model_bakery import baker

from ampa_manager.baker_recipes import bank_account_recipe
from ampa_manager.charge.models.membership_receipt import MembershipReceipt
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.receipt import Receipt
from ampa_manager.charge.remittance import Remittance
from ampa_manager.charge.use_cases.membership.generate_remittance_from_membership_remittance.membership_remittance_generator import \
    MembershipRemittanceGenerator
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder


class TestMembershipRemittanceGenerator(TestCase):
    FEE: Final[int] = 30

    def test_generate_remittance_no_membership_receipt(self):
        membership_remittance: MembershipRemittance = baker.make('MembershipRemittance')

        remittance: Remittance = MembershipRemittanceGenerator(membership_remittance).generate()

        self.assertEqual(remittance.name, membership_remittance.name)
        self.assertEqual(len(remittance.receipts), 0)

    def test_generate_remittance_one_membership_receipt(self):
        membership_remittance: MembershipRemittance = baker.make('MembershipRemittance')
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        holder: Holder = baker.make('Holder', bank_account=bank_account)
        family: Family = baker.make('Family', default_holder=holder)
        membership_receipt: MembershipReceipt = baker.make(
            'MembershipReceipt', family=family, remittance=membership_remittance)
        baker.make('Fee', academic_course=membership_remittance.course, amount=self.FEE)

        remittance: Remittance = MembershipRemittanceGenerator(membership_remittance).generate()

        self.assertEqual(remittance.name, membership_remittance.name)
        self.assertEqual(len(remittance.receipts), 1)
        receipt: Receipt = remittance.receipts[0]
        self.assertEqual(receipt.amount, self.FEE)
        self.assertEqual(receipt.bank_account_owner, membership_receipt.family.default_holder.parent.full_name)
        self.assertEqual(receipt.iban, membership_receipt.family.default_holder.bank_account.iban)

    def test_generate_remittance_two_membership_receipts(self):
        receipt_count: Final[int] = 2
        membership_remittance: MembershipRemittance = baker.make('MembershipRemittance')
        bank_account: BankAccount = baker.make_recipe(bank_account_recipe)
        holder: Holder = baker.make('Holder', bank_account=bank_account)
        family: Family = baker.make('Family', default_holder=holder)
        baker.make('MembershipReceipt', family=family, remittance=membership_remittance, _quantity=receipt_count)
        baker.make('Fee', academic_course=membership_remittance.course, amount=self.FEE)

        remittance: Remittance = MembershipRemittanceGenerator(membership_remittance).generate()

        self.assertEqual(remittance.name, membership_remittance.name)
        self.assertEqual(len(remittance.receipts), receipt_count)
