from pathlib import Path
from typing import IO

from xlrd.sheet import Sheet

from .rows_importer import CustodyImportRow
from .rows_importer import RowImporter
from .rows_importer import RowsImporter
from .test_rows_importer_asserts import TestRowImporterAsserts


class TestRowImporter(TestRowImporterAsserts):
    def test_import_row_correct_complete(self):
        # Arrange
        file_path = Path(__file__).resolve().parent / './assets/correct/custody_one_line_correct_complete.xls'
        file_handler: IO
        with open(file_path, 'rb') as file_handler:
            sheet: Sheet = RowsImporter(file_handler.read()).obtain_sheet()

        # Act
        custody_import_line: CustodyImportRow = RowImporter(sheet, 2).import_row()

        # Assert
        self.assertEqual(custody_import_line.row, 3)
        self.assert_child(custody_import_line.custody_child_import_data)
        self.assert_holder(custody_import_line.holder_import_data)
