from ampa_manager.charge.sepa.xml_pain_008_001_02 import PostalAddress6


class PostalAddressCreator:
    POSTAL_CODE = "01008"
    TOWN = "VITORIA-GASTEIZ"
    ADDRESS_LINE = "Mexico Kalea, 9"

    def create(self, country: str) -> PostalAddress6:
        return PostalAddress6(
            pst_cd=self.POSTAL_CODE, twn_nm=self.TOWN, ctry=country, adr_line=self.ADDRESS_LINE)
