import xlrd
from xlrd.sheet import Sheet

from .custody_import_row import CustodyImportRow
from .row_importer import RowImporter


class RowsImporter:
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2

    @classmethod
    def import_rows(cls, file_content: bytes) -> list[CustodyImportRow]:
        sheet: Sheet = RowsImporter.obtain_sheet(file_content)
        rows: list[CustodyImportRow] = []
        for row_index in range(cls.FIRST_ROW_INDEX, sheet.nrows):
            custody_import_row: CustodyImportRow = RowImporter(sheet, row_index).import_row()
            rows.append(custody_import_row)
        return rows

    @classmethod
    def obtain_sheet(cls, file_content):
        return xlrd.open_workbook(file_contents=file_content).sheet_by_index(cls.SHEET_NUMBER)
