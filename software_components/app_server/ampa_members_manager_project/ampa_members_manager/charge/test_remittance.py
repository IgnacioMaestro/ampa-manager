from unittest import TestCase

from ampa_members_manager.charge.receipt import Receipt, AuthorizationReceipt
from ampa_members_manager.charge.remittance import Remittance


class TestRemittance(TestCase):
    def test_obtain_rows_no_receipts(self):
        remittance: Remittance = Remittance([], 'Empty Remittance')

        rows = remittance.obtain_rows()

        self.assertEqual(len(rows), 0)

    def test_obtain_rows_one_receipt(self):
        authorization_receipt: AuthorizationReceipt = AuthorizationReceipt(
            number='authorization_number', date='authorization_date')
        receipt: Receipt = Receipt(
            amount='2', bank_account_owner='bank_account_owner', iban='iban', authorization=authorization_receipt)
        remittance: Remittance = Remittance([receipt], 'One Receipt Remittance')

        rows = remittance.obtain_rows()

        self.assertEqual(len(rows), 1)

    def test_obtain_rows_two_receipts(self):
        authorization_receipt: AuthorizationReceipt = AuthorizationReceipt(
            number='authorization_number', date='authorization_date')
        receipt: Receipt = Receipt(
            amount='2', bank_account_owner='bank_account_owner', iban='iban', authorization=authorization_receipt)
        remittance: Remittance = Remittance([receipt, receipt], 'Two Receipt Remittance')

        rows = remittance.obtain_rows()

        self.assertEqual(len(rows), 2)
