import datetime
from decimal import Decimal
from unittest import TestCase

from xsdata.models.datatype import XmlDate

from ampa_manager.charge.receipt import Receipt, AuthorizationReceipt
from ampa_manager.charge.remittance import Remittance
from ampa_manager.charge.sepa.document_creator import DocumentCreator
from ampa_manager.charge.sepa.xml_pain_008_001_02 import Document, CustomerDirectDebitInitiationV02, GroupHeader39, \
    PaymentInstructionInformation4, PaymentMethod2Code, PaymentTypeInformation20, PartyIdentification32, CashAccount16, \
    BranchAndFinancialInstitutionIdentification4


class TestDocumentCreator(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        authorization_receipt = AuthorizationReceipt(number='2323123', date=datetime.date.today())
        receipt: Receipt = Receipt(
            amount=2.0, bank_account_owner='bank_account_owner', iban='iban', bic='bic',
            authorization=authorization_receipt)
        cls.remittance = Remittance(
            [receipt], 'One Receipt Remittance', '2023/001', datetime.datetime.now(), datetime.datetime.now(), '',
            'bic', 'iban')

    def test_create_receipt_with_authorization(self):
        document: Document = DocumentCreator(self.remittance).create()
        self.assertTrue(hasattr(document, 'cstmr_drct_dbt_initn'))
        self.assertIsInstance(document.cstmr_drct_dbt_initn, CustomerDirectDebitInitiationV02)
        self.assertTrue(hasattr(document.cstmr_drct_dbt_initn, 'grp_hdr'))
        self.assertIsInstance(document.cstmr_drct_dbt_initn.grp_hdr, GroupHeader39)
        self.assertTrue(hasattr(document.cstmr_drct_dbt_initn, 'pmt_inf'))
        self.assertIsInstance(document.cstmr_drct_dbt_initn.pmt_inf, list)
        self.assertEqual(len(document.cstmr_drct_dbt_initn.pmt_inf), 1)
        self.assertIsInstance(document.cstmr_drct_dbt_initn.pmt_inf[0], PaymentInstructionInformation4)

    def test_create_customer_direct_debit_initiation(self):
        cstmr_drct_dbt_initn: CustomerDirectDebitInitiationV02 = DocumentCreator(
            self.remittance).create_customer_direct_debit_initiation()
        self.assertIsInstance(cstmr_drct_dbt_initn, CustomerDirectDebitInitiationV02)
        self.assertTrue(hasattr(cstmr_drct_dbt_initn, 'grp_hdr'))
        self.assertIsInstance(cstmr_drct_dbt_initn.grp_hdr, GroupHeader39)
        self.assertTrue(hasattr(cstmr_drct_dbt_initn, 'pmt_inf'))
        self.assertIsInstance(cstmr_drct_dbt_initn.pmt_inf, list)
        self.assertEqual(len(cstmr_drct_dbt_initn.pmt_inf), 1)
        self.assertIsInstance(cstmr_drct_dbt_initn.pmt_inf[0], PaymentInstructionInformation4)

    def test_create_payment_instruction_information_list(self):
        remittance_id = "2023/001"
        pmt_inf: list[PaymentInstructionInformation4] = DocumentCreator(
            self.remittance).create_payment_information_list()
        self.assertIsInstance(pmt_inf, list)
        self.assertEqual(len(pmt_inf), 1)
        self.assertIsInstance(pmt_inf[0], PaymentInstructionInformation4)
        self.assertIsInstance(pmt_inf[0].pmt_inf_id, str)
        self.assertEqual(pmt_inf[0].pmt_inf_id, remittance_id)
        self.assertEqual(pmt_inf[0].pmt_mtd, PaymentMethod2Code.DD)
        self.assertIsInstance(pmt_inf[0].nb_of_txs, str)
        self.assertIsInstance(pmt_inf[0].ctrl_sum, Decimal)
        self.assertTrue(pmt_inf[0].btch_bookg)
        self.assertIsInstance(pmt_inf[0].pmt_tp_inf, PaymentTypeInformation20)
        self.assertIsInstance(pmt_inf[0].reqd_colltn_dt, XmlDate)
        self.assertIsInstance(pmt_inf[0].cdtr, PartyIdentification32)
        self.assertIsInstance(pmt_inf[0].cdtr_acct, CashAccount16)
        self.assertIsInstance(pmt_inf[0].cdtr_agt, BranchAndFinancialInstitutionIdentification4)
        self.assertIsInstance(pmt_inf[0].cdtr_schme_id, PartyIdentification32)
        self.assertIsInstance(pmt_inf[0].drct_dbt_tx_inf, list)
        self.assertEqual(len(pmt_inf[0].drct_dbt_tx_inf), 1)
