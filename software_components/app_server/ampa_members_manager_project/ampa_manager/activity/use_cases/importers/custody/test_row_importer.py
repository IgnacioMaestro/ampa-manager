from typing import IO

from xlrd.sheet import Sheet

from ampa_manager.activity.use_cases.importers.custody.custody_import_row import CustodyImportRow
from ampa_manager.activity.use_cases.importers.custody.row_importer import RowImporter
from ampa_manager.activity.use_cases.importers.custody.rows_importer import RowsImporter
from ampa_manager.activity.use_cases.importers.custody.test_rows_importer_asserts import TestRowImporterAsserts


class TestRowImporter(TestRowImporterAsserts):
    def test_import_row_correct_complete(self):
        # Arrange
        file_handler: IO
        with open('./assets/correct/custody_one_line_correct_complete.xls', 'rb') as file_handler:
            sheet: Sheet = RowsImporter().obtain_sheet(file_handler.read())
            # Act
            custody_import_line: CustodyImportRow = RowImporter(sheet, 2).import_row()

        # Assert
        self.assertEqual(custody_import_line.row, 3)
        self.assert_child(custody_import_line.custody_child_import_data)
        self.assert_holder(custody_import_line.holder_import_data)
