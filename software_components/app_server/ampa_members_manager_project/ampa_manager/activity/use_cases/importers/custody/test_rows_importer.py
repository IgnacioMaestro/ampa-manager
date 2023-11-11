from typing import IO

from .custody_import_row import CustodyImportRow
from .rows_importer import RowsImporter
from .rows_importer_error import RowsImporterErrors, RowsImporterErrorType
from .test_rows_importer_asserts import TestRowImporterAsserts


class TestRowsImporter(TestRowImporterAsserts):
    def test_import_rows_correct_complete(self):
        # Arrange
        file_handler: IO
        with open('./custody/assets/correct/custody_one_line_correct_complete.xls', 'rb') as file_handler:
            # Act
            imported_lines: list[CustodyImportRow] = RowsImporter().import_rows(file_handler.read())

        # Assert
        self.assertEqual(1, len(imported_lines))
        imported_line: CustodyImportRow = imported_lines.pop()
        self.assertEqual(imported_line.row, 3)
        self.assert_child(imported_line.custody_child_import_data)
        self.assert_holder(imported_line.holder_import_data)

    def test_import_rows_correct_without_holder_data(self):
        # Arrange
        file_handler: IO
        with open('./custody/assets/correct/custody_one_line_correct_without_holder_data.xls', 'rb') as file_handler:
            # Act
            imported_lines: list[CustodyImportRow] = RowsImporter().import_rows(file_handler.read())

        # Assert
        self.assertEqual(1, len(imported_lines))
        imported_line: CustodyImportRow = imported_lines.pop()
        self.assertEqual(imported_line.row, 3)
        self.assert_child(imported_line.custody_child_import_data)
        self.assertIsNone(imported_line.holder_import_data)

    def test_import_rows_error_no_email(self):
        # Arrange
        file_handler: IO
        with open('./custody/assets/errors/holder/custody_one_line_no_email.xls', 'rb') as file_handler:
            # Act
            with self.assertRaises(RowsImporterErrors) as errors:
                RowsImporter().import_rows(file_handler.read())
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), RowsImporterErrorType.HOLDER_EMAIL_NOT_FOUND)
