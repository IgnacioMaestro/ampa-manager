from pathlib import Path
from typing import IO, Optional

from xlrd.sheet import Sheet

from .rows_importer import CustodyImportRow
from .rows_importer import RowImporter
from .rows_importer import RowsImporter
from .rows_importer_error import RowsImporterErrorType
from .test_rows_importer_asserts import TestRowImporterAsserts


class TestRowImporter(TestRowImporterAsserts):
    LOCAL_PATH = Path(__file__).resolve().parent

    def test_import_row_correct_complete(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/correct/custody_one_line_correct_complete.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        custody_import_row: Optional[CustodyImportRow]
        errors: Optional[list[RowsImporterErrorType]]
        custody_import_row, errors = RowImporter(sheet, 2).import_row()

        # Assert
        self.assertIsNone(errors)
        self.assertEqual(custody_import_row.row, 3)
        self.assert_child(custody_import_row.custody_child_import_data)
        self.assert_holder(custody_import_row.holder_import_data)

    def test_import_row_correct_without_holder_data(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/correct/custody_one_line_correct_without_holder_data.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        custody_import_row: Optional[CustodyImportRow]
        errors: Optional[list[RowsImporterErrorType]]
        custody_import_row, errors = RowImporter(sheet, 2).import_row()

        # Assert
        self.assertIsNone(errors)
        self.assertEqual(custody_import_row.row, 3)
        self.assert_child(custody_import_row.custody_child_import_data)
        self.assertIsNone(custody_import_row.holder_import_data)

    def test_import_row_error_no_email(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/errors/holder/custody_one_line_no_email.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        custody_import_row: Optional[CustodyImportRow]
        errors: Optional[list[RowsImporterErrorType]]
        custody_import_row, errors = RowImporter(sheet, 2).import_row()

        # Assert
        self.assertIsNone(custody_import_row)
        self.assertEqual(errors, [RowsImporterErrorType.HOLDER_EMAIL_NOT_FOUND])

    def test_import_row_error_no_iban_no_name(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/errors/custody_one_line_no_iban_no_name.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        custody_import_row: Optional[CustodyImportRow]
        errors: Optional[list[RowsImporterErrorType]]
        custody_import_row, errors = RowImporter(sheet, 2).import_row()

        # Assert
        self.assertIsNone(custody_import_row)
        self.assertEqual(len(errors), 2)
        self.assertIn(RowsImporterErrorType.HOLDER_IBAN_NOT_FOUND, errors)
        self.assertIn(RowsImporterErrorType.CHILD_NAME_NOT_FOUND, errors)

    @classmethod
    def obtain_sheet(cls, file_path):
        file_handler: IO
        with open(file_path, 'rb') as file_handler:
            sheet: Sheet = RowsImporter(file_handler.read()).obtain_sheet()
        return sheet
