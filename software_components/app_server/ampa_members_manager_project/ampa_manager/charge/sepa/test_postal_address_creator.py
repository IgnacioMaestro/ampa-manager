import datetime
from unittest import TestCase

from ampa_manager.charge.receipt import AuthorizationReceipt, Receipt
from ampa_manager.charge.remittance import Remittance
from ampa_manager.charge.sepa.postal_address_creator import PostalAddressCreator
from ampa_manager.charge.sepa.xml_pain_008_001_02 import PostalAddress6


class TestPostalAddressCreator(TestCase):
    COUNTRY = 'country'

    @classmethod
    def setUpClass(cls) -> None:
        authorization_receipt = AuthorizationReceipt(number='2323123', date=datetime.date.today())
        receipt: Receipt = Receipt(
            amount=2.0, bank_account_owner='bank_account_owner', iban='iban', bic='bic',
            authorization=authorization_receipt)
        cls.remittance = Remittance(
            [receipt], 'One Receipt Remittance', '2023/001', datetime.datetime.now(), datetime.datetime.now(), '')

    def test_create(self):
        postal_address: PostalAddress6 = PostalAddressCreator().create(self.COUNTRY)
        self.assertEqual(postal_address.pst_cd, PostalAddressCreator.POSTAL_CODE)
        self.assertEqual(postal_address.twn_nm, PostalAddressCreator.TOWN)
        self.assertEqual(postal_address.ctry, self.COUNTRY)
        self.assertEqual(postal_address.adr_line, PostalAddressCreator.ADDRESS_LINE)
