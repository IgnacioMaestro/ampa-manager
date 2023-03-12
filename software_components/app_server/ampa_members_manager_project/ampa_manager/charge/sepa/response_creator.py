import codecs
from django.http import HttpResponse
from ampa_manager.charge.remittance import Remittance
from .xml_creator import XMLCreator


class ResponseCreator:
    TEXT_XML = 'text/xml'

    def create(self, remittance: Remittance) -> HttpResponse:
        headers = {'Content-Disposition': f'attachment; filename="{remittance.name}.xml"'}
        response = HttpResponse(content_type=self.TEXT_XML, headers=headers)
        response.write(codecs.BOM_UTF8)
        xml: str = XMLCreator(remittance).create()
        response.write(xml)
        return response
