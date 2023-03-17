from decimal import Decimal
from xsdata.models.datatype import XmlDateTime

from ampa_manager.charge.remittance import Remittance
from ampa_manager.charge.sepa.xml_pain_008_001_02 import GroupHeader39, PartyIdentification32, Party6Choice, \
    OrganisationIdentification4, GenericOrganisationIdentification1


class GroupHeaderCreator:

    def __init__(self, remittance: Remittance, party_identification: str, organization_id: str):
        self.remittance = remittance
        self.party_identification = party_identification
        self.organization_id = organization_id

    def create(self) -> GroupHeader39:
        return GroupHeader39(
            msg_id=self.remittance.name,
            cre_dt_tm=XmlDateTime.from_string(self.remittance.created_date.strftime("%Y-%m-%dT%H:%M:%S")),
            nb_of_txs=str(len(self.remittance.obtain_receipts_grouped_by_iban())),
            ctrl_sum=Decimal(format(self.remittance.calculate_total_amount(), '.2f')),
            initg_pty=self.create_party_identification())

    def create_party_identification(self) -> PartyIdentification32:
        return PartyIdentification32(nm=self.party_identification, id=self.create_party_choice())

    def create_party_choice(self) -> Party6Choice:
        return Party6Choice(
            org_id=(OrganisationIdentification4(othr=[GenericOrganisationIdentification1(id=self.organization_id)])))
