from datetime import date
from unittest import TestCase

from charge.receipt import Receipt, AuthorizationReceipt


class TestReceipt(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.amount = 3.2
        cls.bank_account_owner = 'paco'
        cls.iban = 'iban'
        cls.bic = 'bic'
        cls.authorization_receipt = AuthorizationReceipt('2/2022', date(2022, 2, 2))

    def test_obtain_row_with_authorization(self):
        receipt = Receipt(self.amount, self.bank_account_owner, self.iban, self.bic, self.authorization_receipt)
        self.assertEqual(
            receipt.obtain_row(),
            [self.bank_account_owner, self.bic, self.iban, self.authorization_receipt.number,
             self.authorization_receipt.obtain_date(), '3,20'])

    def test_obtain_row_without_authorization(self):
        receipt = Receipt(self.amount, self.bank_account_owner, self.iban, self.bic, None)
        self.assertEqual(
            receipt.obtain_row(),
            [self.bank_account_owner, self.bic, self.iban, Receipt.NO_AUTHORIZATION_MESSAGE, '', '3,20'])
