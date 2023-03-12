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
        group_header: GroupHeader39 = GroupHeader39()
        group_header.msg_id = self.remittance.name
        group_header.cre_dt_tm = self.generate_creation_date()
        group_header.nb_of_txs = len(self.remittance.obtain_receipts_grouped_by_iban())
        group_header.ctrl_sum = float(format(self.remittance.calculate_total_amount(), '.2f'))
        group_header.initg_pty = self.create_party_identification_32(self.party_identification)
        return group_header

    def generate_creation_date(self) -> XmlDateTime:
        now_str: str = self.remittance.created_date.strftime("%Y-%m-%dT%H:%M:%S")
        creation_date: XmlDateTime = XmlDateTime.from_string(now_str)
        return creation_date

    def create_party_identification_32(self, party_identification: str) -> PartyIdentification32:
        party_identification_32: PartyIdentification32 = PartyIdentification32()
        party_identification_32.nm = party_identification
        party_identification_32.id = self.create_party_6_choice()
        return party_identification_32

    def create_party_6_choice(self) -> Party6Choice:
        party_6_choice: Party6Choice = Party6Choice()
        organisation_identification_4: OrganisationIdentification4 = OrganisationIdentification4()
        generic_organisation_identification_1: GenericOrganisationIdentification1 = GenericOrganisationIdentification1()
        generic_organisation_identification_1.id = self.organization_id
        organisation_identification_4.othr.append(generic_organisation_identification_1)
        party_6_choice.org_id = organisation_identification_4
        return party_6_choice
