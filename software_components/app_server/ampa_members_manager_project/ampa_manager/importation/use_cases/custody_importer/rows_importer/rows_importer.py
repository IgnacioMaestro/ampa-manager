from typing import Optional

import xlrd
from xlrd.sheet import Sheet

from .custody_import_row import CustodyImportRow
from .errors_in_row import ErrorsInRow
from .row_importer import RowImporter
from .rows_importer_error import RowsImporterErrorType


class RowsImporter:
    SHEET_NUMBER = 0
    FIRST_ROW_INDEX = 2

    def __init__(self, file_content: bytes):
        self.__file_content = file_content

    def import_rows(self) -> tuple[Optional[list[CustodyImportRow]], Optional[list[ErrorsInRow]]]:
        sheet: Sheet = self.obtain_sheet()
        return self.import_rows_from_sheet(sheet)

    @classmethod
    def import_rows_from_sheet(cls, sheet) -> tuple[Optional[list[CustodyImportRow]], Optional[list[ErrorsInRow]]]:
        rows: list[CustodyImportRow] = []
        errors_in_rows: list[ErrorsInRow] = []
        for row_index in range(cls.FIRST_ROW_INDEX, sheet.nrows):
            row: Optional[CustodyImportRow]
            errors: Optional[list[RowsImporterErrorType]]
            row, errors = RowImporter(sheet, row_index).import_row()
            if row is not None:
                rows.append(row)
            else:
                errors_in_rows.append(ErrorsInRow(row_index, errors))
        optional_errors, optional_rows = cls.prepare_optional_return_values(errors_in_rows, rows)
        return optional_rows, optional_errors

    @classmethod
    def prepare_optional_return_values(cls, errors_in_rows, rows) -> tuple[
        Optional[list[CustodyImportRow]], Optional[list[ErrorsInRow]]]:
        optional_errors: Optional[list[ErrorsInRow]] = None
        optional_rows: Optional[list[CustodyImportRow]] = None
        if len(errors_in_rows) > 0:
            optional_errors = errors_in_rows
        else:
            optional_rows = rows
        return optional_errors, optional_rows

    def obtain_sheet(self) -> Sheet:
        return xlrd.open_workbook(file_contents=self.__file_content).sheet_by_index(self.SHEET_NUMBER)
