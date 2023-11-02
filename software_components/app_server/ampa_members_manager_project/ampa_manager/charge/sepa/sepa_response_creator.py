import codecs
from django.http import HttpResponse
from ampa_manager.charge.remittance import Remittance
from .xml_creator import XMLCreator


class SEPAResponseCreator:
    TEXT_XML = 'text/xml'

    def create_sepa_response(self, remittance: Remittance) -> HttpResponse:
        xml: str = XMLCreator(remittance).create()
        return self.__create_response(remittance.name, xml)

    def __create_response(self, remittance_name, xml):
        headers = {'Content-Disposition': f'attachment; filename="{remittance_name}.xml"'}
        response = HttpResponse(content_type=self.TEXT_XML, headers=headers)
        response.write(codecs.BOM_UTF8)
        response.write(xml)
        return response
