from pathlib import Path
from typing import IO, Optional

from xlrd.sheet import Sheet

from ..excel_extracted_types.holder_import_data import HolderImportData
from ..rows_importer.row_importer_holder_data import RowImporterHolderData
from ..rows_importer.rows_importer import RowsImporter
from ..rows_importer.rows_importer_error import RowsImporterErrorType
from ..rows_importer.test_rows_importer_asserts import TestRowImporterAsserts


class TestRowImporterHolderData(TestRowImporterAsserts):
    LOCAL_PATH = Path(__file__).resolve().parent

    def test_import_row_correct_complete(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/correct/custody_one_line_correct_complete.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        holder_import_data: Optional[HolderImportData]
        errors: Optional[list[RowsImporterErrorType]]
        holder_import_data, errors = RowImporterHolderData(sheet, 2).import_row()

        # Assert
        self.assertIsNone(errors)
        self.assert_holder(holder_import_data)

    def test_import_row_correct_without_holder_data(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/correct/custody_one_line_correct_without_holder_data.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        holder_import_data: Optional[HolderImportData]
        errors: Optional[list[RowsImporterErrorType]]
        holder_import_data, errors = RowImporterHolderData(sheet, 2).import_row()

        # Assert
        self.assertIsNone(errors)
        self.assertIsNone(holder_import_data)

    def test_import_row_error_no_email(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/errors/holder/custody_one_line_no_email.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        holder_import_data: Optional[HolderImportData]
        errors: Optional[list[RowsImporterErrorType]]
        holder_import_data, errors = RowImporterHolderData(sheet, 2).import_row()

        # Assert
        self.assertIsNone(holder_import_data)
        self.assert_errors_to_check_in_errors([RowsImporterErrorType.HOLDER_EMAIL_NOT_FOUND], errors)

    def test_import_row_error_no_phone_number(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/errors/holder/custody_one_line_no_phone.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        holder_import_data: Optional[HolderImportData]
        errors: Optional[list[RowsImporterErrorType]]
        holder_import_data, errors = RowImporterHolderData(sheet, 2).import_row()

        # Assert
        self.assertIsNone(holder_import_data)
        self.assert_errors_to_check_in_errors(
            [RowsImporterErrorType.HOLDER_PHONE_NUMBER_NOT_FOUND], errors)

    def test_import_row_error_no_name_and_surnames(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/errors/holder/custody_one_line_no_parent_name_and_surnames.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        holder_import_data: Optional[HolderImportData]
        errors: Optional[list[RowsImporterErrorType]]
        holder_import_data, errors = RowImporterHolderData(sheet, 2).import_row()

        # Assert
        self.assertIsNone(holder_import_data)
        self.assert_errors_to_check_in_errors(
            [RowsImporterErrorType.HOLDER_NAME_AND_SURNAMES_NOT_FOUND], errors)

    def test_import_row_error_no_iban(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/errors/holder/custody_one_line_no_iban.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        holder_import_data: Optional[HolderImportData]
        errors: Optional[list[RowsImporterErrorType]]
        holder_import_data, errors = RowImporterHolderData(sheet, 2).import_row()

        # Assert
        self.assertIsNone(holder_import_data)
        self.assert_errors_to_check_in_errors(
            [RowsImporterErrorType.HOLDER_IBAN_NOT_FOUND], errors)

    def test_import_row_error_no_iban_and_no_email(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/errors/holder/custody_one_line_no_iban_and_no_email.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        holder_import_data: Optional[HolderImportData]
        errors: Optional[list[RowsImporterErrorType]]
        holder_import_data, errors = RowImporterHolderData(sheet, 2).import_row()

        # Assert
        self.assertIsNone(holder_import_data)
        self.assert_errors_to_check_in_errors(
            [RowsImporterErrorType.HOLDER_IBAN_NOT_FOUND, RowsImporterErrorType.HOLDER_EMAIL_NOT_FOUND],
            errors)

    @classmethod
    def obtain_sheet(cls, file_path):
        file_handler: IO
        with open(file_path, 'rb') as file_handler:
            sheet: Sheet = RowsImporter(file_handler.read()).obtain_sheet()
        return sheet

    def assert_errors_to_check_in_errors(self, errors_to_check: list[RowsImporterErrorType], errors):
        self.assertEqual(len(errors_to_check), len(errors))
        for error_to_check in errors_to_check:
            self.assertIn(error_to_check, errors)
