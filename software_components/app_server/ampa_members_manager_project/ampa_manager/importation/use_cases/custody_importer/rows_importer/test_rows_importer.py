from pathlib import Path
from typing import IO

from .custody_import_row import CustodyImportRow
from .rows_importer import RowsImporter
from .rows_importer_error import RowsImporterErrors, RowsImporterErrorType
from .test_rows_importer_asserts import TestRowImporterAsserts


class TestRowsImporter(TestRowImporterAsserts):
    LOCAL_PATH = Path(__file__).resolve().parent

    def test_import_rows_correct_complete(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/correct/custody_one_line_correct_complete.xls'
        file_handler: IO
        with open(file_path, 'rb') as file_handler:
            # Act
            imported_lines: list[CustodyImportRow] = RowsImporter(file_handler.read()).import_rows()

        # Assert
        self.assert_correct_import_child_data(imported_lines)
        self.assert_holder(imported_lines[0].holder_import_data)

    def test_import_rows_correct_without_holder_data(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/correct/custody_one_line_correct_without_holder_data.xls'
        file_handler: IO
        with open(file_path, 'rb') as file_handler:
            # Act
            imported_lines: list[CustodyImportRow] = RowsImporter(file_handler.read()).import_rows()

        # Assert
        self.assert_correct_import_child_data(imported_lines)
        self.assertIsNone(imported_lines[0].holder_import_data)

    def test_import_rows_error_no_email(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/errors/holder/custody_one_line_no_email.xls'
        file_handler: IO
        with open(file_path, 'rb') as file_handler:
            # Act
            with self.assertRaises(RowsImporterErrors) as errors:
                RowsImporter(file_handler.read()).import_rows()

        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), RowsImporterErrorType.HOLDER_EMAIL_NOT_FOUND)

    def assert_correct_import_child_data(self, imported_lines):
        self.assertEqual(1, len(imported_lines))
        self.assertEqual(imported_lines[0].row, 3)
        self.assert_child(imported_lines[0].custody_child_import_data)
