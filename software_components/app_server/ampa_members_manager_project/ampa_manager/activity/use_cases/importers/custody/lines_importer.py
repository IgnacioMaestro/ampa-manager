import xlrd
from xlrd.sheet import Sheet

from .custody_import_line import CustodyImportLine
from .line_importer import LineImporter


class LinesImporter:
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2

    @classmethod
    def import_lines(cls, file_content: bytes) -> list[CustodyImportLine]:
        sheet: Sheet = LinesImporter.obtain_sheet(file_content)
        lines: list[CustodyImportLine] = []
        for row_index in range(cls.FIRST_ROW_INDEX, sheet.nrows):
            custody_import_line: CustodyImportLine = LineImporter(sheet, row_index).import_line()
            lines.append(custody_import_line)
        return lines

    @classmethod
    def obtain_sheet(cls, file_content):
        return xlrd.open_workbook(file_contents=file_content).sheet_by_index(cls.SHEET_NUMBER)
