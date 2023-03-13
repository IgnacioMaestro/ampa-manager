import codecs
import csv

from django.http import HttpResponse

from ampa_manager.charge.remittance import Remittance


class HttpResponseCSVCreator:
    TEXT_CSV = 'text/csv'

    def __init__(self, remittance: Remittance):
        self.remittance = remittance

    def create(self) -> HttpResponse:
        headers = {'Content-Disposition': f'attachment; filename="{self.remittance.name}.csv"'}
        response = HttpResponse(content_type=HttpResponseCSVCreator.TEXT_CSV, headers=headers)
        response.write(codecs.BOM_UTF8)
        rows_to_add: list[list[str]] = [['Titular', 'BIC', 'IBAN', 'Autorizacion', 'Fecha Autorizacion', 'Cantidad']]
        rows_to_add.extend(self.remittance.obtain_rows())
        csv.writer(response).writerows(rows_to_add)
        return response
