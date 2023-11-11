from xlrd.sheet import Sheet

from .custody_import_row import CustodyImportRow
from .row_importer_child_data import RowImporterChildData
from .row_importer_holder_data import RowImporterHolderData


class RowImporter:
    def __init__(self, sheet: Sheet, row_index: int):
        self.__sheet = sheet
        self.__row_index = row_index

    def import_row(self) -> CustodyImportRow:
        custody_child_import_data = RowImporterChildData(self.__sheet, self.__row_index).import_row()
        holder_import_data = RowImporterHolderData(self.__sheet, self.__row_index).import_row()
        return CustodyImportRow(self.__row_index + 1, custody_child_import_data, holder_import_data)
