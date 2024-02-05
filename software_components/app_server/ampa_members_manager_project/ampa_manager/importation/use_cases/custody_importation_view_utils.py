from django.db.models import QuerySet

from ampa_manager.importation.models.custody_importation import CustodyImportation
from ampa_manager.importation.models.custody_importation_row import CustodyImportationRow
from ampa_manager.utils.excel.titled_list import TitledList


class CustodyImportationViewUtils:
    def __init__(self, custody_importation: CustodyImportation):
        self.__custody_importation = custody_importation

    def get_number_of_rows(self):
        return CustodyImportationRow.objects.filter(importation=self.__custody_importation).count()

    def get_summary(self) -> TitledList:
        rows: QuerySet[CustodyImportationRow] = CustodyImportationRow.objects.filter(
            importation=self.__custody_importation).order_by('-id')
        titled_list = TitledList('Summary')
        for row in rows:
            row_sublist = TitledList('Row number: ' + str(row.row))
            row_sublist.append_element(str(row))
            titled_list.append_sublist(row_sublist)
        return titled_list
