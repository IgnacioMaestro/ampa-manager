from xlrd.sheet import Sheet

from .custody_import_line import CustodyImportLine
from .line_importer_child_data import LineImporterChildData
from .line_importer_holder_data import LineImporterHolderData


class LineImporter:
    def __init__(self, sheet: Sheet, row_index: int):
        self.__sheet = sheet
        self.__row_index = row_index

    def import_line(self) -> CustodyImportLine:
        custody_child_import_data = LineImporterChildData(self.__sheet, self.__row_index).import_line()
        holder_import_data = LineImporterHolderData(self.__sheet, self.__row_index).import_line()
        return CustodyImportLine(self.__row_index + 1, custody_child_import_data, holder_import_data)
