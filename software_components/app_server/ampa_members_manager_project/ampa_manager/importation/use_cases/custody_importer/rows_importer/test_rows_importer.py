from pathlib import Path
from typing import IO, Optional

from .custody_import_row import CustodyImportRow
from .errors_in_row import ErrorsInRow
from .rows_importer import RowsImporter
from .rows_importer_error import RowsImporterErrorType
from .test_rows_importer_asserts import TestRowImporterAsserts


class TestRowsImporter(TestRowImporterAsserts):
    LOCAL_PATH = Path(__file__).resolve().parent

    def test_import_rows_correct_complete(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/correct/custody_one_line_correct_complete.xls'
        imported_rows: Optional[list[CustodyImportRow]]
        error_rows: Optional[list[ErrorsInRow]]
        file_handler: IO
        with open(file_path, 'rb') as file_handler:
            # Act
            imported_rows, error_rows = RowsImporter(file_handler.read()).import_rows()

        # Assert
        self.assertIsNone(error_rows)
        self.assert_correct_import_child_data(imported_rows)
        self.assert_holder(imported_rows[0].holder_import_data)

    def test_import_rows_correct_without_holder_data(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/correct/custody_one_line_correct_without_holder_data.xls'
        imported_rows: Optional[list[CustodyImportRow]]
        error_rows: Optional[list[ErrorsInRow]]
        file_handler: IO
        with open(file_path, 'rb') as file_handler:
            # Act
            imported_rows, error_rows = RowsImporter(file_handler.read()).import_rows()

        # Assert
        self.assertIsNone(error_rows)
        self.assert_correct_import_child_data(imported_rows)
        self.assertIsNone(imported_rows[0].holder_import_data)

    def test_import_rows_error_no_email(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/errors/holder/custody_one_line_no_email.xls'
        imported_rows: Optional[list[CustodyImportRow]]
        error_rows: Optional[list[ErrorsInRow]]
        file_handler: IO
        with open(file_path, 'rb') as file_handler:
            # Act
            imported_rows, error_rows = RowsImporter(file_handler.read()).import_rows()

        # Assert
        self.assertIsNone(imported_rows)
        self.assertEqual(1, len(error_rows))
        error_row = error_rows.pop()
        self.assertEqual(error_row.get_row_number(), 2)
        self.assertEqual(error_row.get_errors(), [RowsImporterErrorType.HOLDER_EMAIL_NOT_FOUND])

    def assert_correct_import_child_data(self, imported_rows):
        self.assertEqual(1, len(imported_rows))
        self.assertEqual(imported_rows[0].row, 3)
        self.assert_child(imported_rows[0].custody_child_import_data)
