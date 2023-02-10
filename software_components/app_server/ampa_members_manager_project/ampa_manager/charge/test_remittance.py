import datetime
from unittest import TestCase

from .receipt import Receipt
from .remittance import Remittance


class TestRemittance(TestCase):
    receipt: Receipt

    @classmethod
    def setUpClass(cls):
        cls.receipt: Receipt = Receipt(
            amount=2.0, bank_account_owner='bank_account_owner', iban='iban', bic='bic', authorization=None)

    def test_obtain_rows_no_receipts(self):
        remittance: Remittance = Remittance([], 'Empty Remittance', datetime.datetime.now())

        rows = remittance.obtain_rows()

        self.assertEqual(len(rows), 0)

    def test_obtain_rows_one_receipt(self):
        remittance: Remittance = Remittance([self.receipt], 'One Receipt Remittance', datetime.datetime.now())

        rows = remittance.obtain_rows()

        self.assertEqual(len(rows), 1)

    def test_obtain_rows_two_receipts(self):
        remittance: Remittance = Remittance(
            [self.receipt, self.receipt], 'Two Receipt Remittance', datetime.datetime.now())

        rows = remittance.obtain_rows()

        self.assertEqual(len(rows), 2)
