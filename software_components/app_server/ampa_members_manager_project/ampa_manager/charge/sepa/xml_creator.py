from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from ampa_manager.charge.remittance import Remittance
from .document_creator import DocumentCreator


class XMLCreator:
    NS_MAP = {None: "urn:iso:std:iso:20022:tech:xsd:pain.008.001.02"}

    def __init__(self, remittance: Remittance, remittance_id):
        self.remittance = remittance
        self.remittance_id = remittance_id

    def create(self) -> str:
        document = DocumentCreator(self.remittance, self.remittance_id).create()
        return XmlSerializer(SerializerConfig(pretty_print=True)).render(document, ns_map=self.NS_MAP)
