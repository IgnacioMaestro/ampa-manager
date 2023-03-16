import datetime
from unittest import TestCase

from ampa_manager.charge.receipt import Receipt, AuthorizationReceipt
from ampa_manager.charge.remittance import Remittance
from ampa_manager.charge.sepa.document_creator import DocumentCreator
from ampa_manager.charge.sepa.xml_pain_008_001_02 import Document, CustomerDirectDebitInitiationV02


class TestDocumentCreator(TestCase):
    def test_create_receipt_with_authorization(self):
        authorization_receipt = AuthorizationReceipt('2323123', datetime.date.today())
        receipt: Receipt = Receipt(
            amount=2.0, bank_account_owner='bank_account_owner', iban='iban', bic='bic',
            authorization=authorization_receipt)
        remittance = Remittance(
            [receipt], 'One Receipt Remittance', datetime.datetime.now(), datetime.datetime.now(), '')
        document: Document = DocumentCreator(remittance).create()
        self.assertTrue(isinstance(document.cstmr_drct_dbt_initn, CustomerDirectDebitInitiationV02))
        self.assertTrue(hasattr(document, 'cstmr_drct_dbt_initn'))
