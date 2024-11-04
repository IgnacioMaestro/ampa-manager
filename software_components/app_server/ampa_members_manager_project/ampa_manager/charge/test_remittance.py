import datetime
from unittest import TestCase

from .receipt import Receipt, AuthorizationReceipt
from .remittance import Remittance


class TestRemittance(TestCase):
    receipt: Receipt

    @classmethod
    def setUpClass(cls):
        cls.receipt: Receipt = Receipt(
            amount=2.0, bank_account_owner='bank_account_owner', iban='iban', bic='bic',
            authorization=AuthorizationReceipt('2/2022', datetime.date(2022, 2, 2)))
        cls.empty_remittance = Remittance(
            [], 'Empty Remittance', '2023/001', datetime.datetime.now(), datetime.datetime.now(), '', 'bic', 'iban')
        cls.one_receipt_remittance = Remittance(
            [cls.receipt], 'One Receipt Remittance', '2023/001', datetime.datetime.now(), datetime.datetime.now(), '',
            'bic', 'iban')
        cls.two_receipts_remittance = Remittance(
            [cls.receipt, cls.receipt], 'Two Receipt Remittance', '2023/001', datetime.datetime.now(),
            datetime.datetime.now(), '', 'bic', 'iban')

    def test_obtain_rows_no_receipts(self):
        # Act
        rows = self.empty_remittance.obtain_rows()

        # Assert
        self.assertEqual(len(rows), 0)

    def test_obtain_rows_one_receipt(self):
        # Act
        rows = self.one_receipt_remittance.obtain_rows()

        # Assert
        self.assertEqual(len(rows), 1)

    def test_obtain_rows_two_receipts(self):
        # Act
        rows = self.two_receipts_remittance.obtain_rows()

        # Assert
        self.assertEqual(len(rows), 2)

    def test_calculate_total_amount_no_receipts(self):
        # Assert
        self.assertEqual(self.empty_remittance.calculate_total_amount(), 0.0)

    def test_calculate_total_amount_one_receipt(self):
        # Assert
        self.assertEqual(self.one_receipt_remittance.calculate_total_amount(), self.receipt.amount)

    def test_calculate_total_amount_two_receipts(self):
        # Assert
        self.assertEqual(self.two_receipts_remittance.calculate_total_amount(), self.receipt.amount * 2)

    def test_obtain_receipts_grouped_by_iban_by_iban_no_receipts(self):
        receipts_by_iban: list[Receipt] = self.empty_remittance.obtain_receipts_grouped_by_iban()
        self.assertEqual(len(receipts_by_iban), 0)

    def test_obtain_receipts_grouped_by_iban_by_iban_one_receipt(self):
        receipts_by_iban: list[Receipt] = self.one_receipt_remittance.obtain_receipts_grouped_by_iban()
        self.assertEqual(len(receipts_by_iban), 1)

    def test_obtain_receipts_grouped_by_iban_by_iban_two_receipts(self):
        receipts_by_iban: list[Receipt] = self.two_receipts_remittance.obtain_receipts_grouped_by_iban()
        self.assertEqual(len(receipts_by_iban), 1)
        self.assertEqual(receipts_by_iban[0].amount, self.receipt.amount * 2)
