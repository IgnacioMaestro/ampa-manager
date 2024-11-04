import datetime
from decimal import Decimal
from unittest import TestCase

from xsdata.models.datatype import XmlDateTime

from ampa_manager.charge.receipt import AuthorizationReceipt, Receipt
from ampa_manager.charge.remittance import Remittance
from ampa_manager.charge.sepa.group_header_creator import GroupHeaderCreator
from ampa_manager.charge.sepa.xml_pain_008_001_02 import GroupHeader39, PartyIdentification32, Party6Choice, \
    OrganisationIdentification4, GenericOrganisationIdentification1


class TestGroupHeaderCreator(TestCase):
    PARTY = 'party'
    ID = 'id'

    @classmethod
    def setUpClass(cls) -> None:
        authorization_receipt = AuthorizationReceipt(number='2323123', date=datetime.date.today())
        receipt: Receipt = Receipt(
            amount=2.0, bank_account_owner='bank_account_owner', iban='iban', bic='bic',
            authorization=authorization_receipt)
        cls.remittance = Remittance(
            [receipt], 'One Receipt Remittance', '2023/001', datetime.datetime.now(), datetime.datetime.now(), '',
            'bic', 'iban')

    def test_create(self):
        group_header_39: GroupHeader39 = GroupHeaderCreator(
            remittance=self.remittance, party_identification=self.PARTY, organization_id=self.ID).create()
        self.assertEqual(group_header_39.msg_id, self.remittance.name)
        self.assertEqual(
            group_header_39.cre_dt_tm,
            XmlDateTime.from_string(self.remittance.created_date.strftime("%Y-%m-%dT%H:%M:%S")))
        self.assertEqual(group_header_39.nb_of_txs, str(len(self.remittance.obtain_receipts_grouped_by_iban())))
        self.assertEqual(group_header_39.ctrl_sum, Decimal(format(self.remittance.calculate_total_amount(), '.2f')))
        self.assertIsInstance(group_header_39.initg_pty, PartyIdentification32)

    def test_create_party_identification(self):
        party_identification_32: PartyIdentification32 = GroupHeaderCreator(
            remittance=self.remittance, party_identification=self.PARTY,
            organization_id=self.ID).create_party_identification()
        self.assertEqual(party_identification_32.nm, self.PARTY)
        self.assertIsInstance(party_identification_32.id, Party6Choice)

    def test_create_party_choice(self):
        party_choice: Party6Choice = GroupHeaderCreator(
            remittance=self.remittance, party_identification=self.PARTY, organization_id=self.ID).create_party_choice()
        self.assertIsInstance(party_choice.org_id, OrganisationIdentification4)
        self.assertIsInstance(party_choice.org_id.othr, list)
        self.assertEqual(len(party_choice.org_id.othr), 1)
        self.assertIsInstance(party_choice.org_id.othr[0], GenericOrganisationIdentification1)
        self.assertEqual(party_choice.org_id.othr[0].id, self.ID)
