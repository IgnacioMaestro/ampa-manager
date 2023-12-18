import xlrd
from xlrd.sheet import Sheet

from .custody_import_row import CustodyImportRow
from .row_importer import RowImporter


class RowsImporter:
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2

    def __init__(self, file_content: bytes):
        self.__file_content = file_content

    def import_rows(self) -> list[CustodyImportRow]:
        sheet: Sheet = self.obtain_sheet()
        return self.import_rows_from_sheet(sheet)

    @classmethod
    def import_rows_from_sheet(cls, sheet) -> list[CustodyImportRow]:
        rows: list[CustodyImportRow] = []
        for row_index in range(cls.FIRST_ROW_INDEX, sheet.nrows):
            custody_import_row: CustodyImportRow = RowImporter(sheet, row_index).import_row()
            rows.append(custody_import_row)
        return rows

    def obtain_sheet(self) -> Sheet:
        return xlrd.open_workbook(file_contents=self.__file_content).sheet_by_index(self.SHEET_NUMBER)
