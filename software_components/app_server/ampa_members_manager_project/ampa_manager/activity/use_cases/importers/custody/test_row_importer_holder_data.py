from typing import IO

from xlrd.sheet import Sheet

from ampa_manager.activity.use_cases.importers.custody.row_importer_holder_data import RowImporterHolderData
from ampa_manager.activity.use_cases.importers.custody.rows_importer import RowsImporter
from ampa_manager.activity.use_cases.importers.custody.rows_importer_error import RowsImporterErrors, \
    RowsImporterErrorType
from ampa_manager.activity.use_cases.importers.custody.test_rows_importer_asserts import TestRowImporterAsserts
from ampa_manager.activity.use_cases.importers.excel_extracted_types.holder_import_data import HolderImportData


class TestRowImporterHolderData(TestRowImporterAsserts):
    def test_import_row_correct_complete(self):
        # Arrange
        file_handler: IO
        with open('./assets/correct/custody_one_line_correct_complete.xls', 'rb') as file_handler:
            sheet: Sheet = RowsImporter().obtain_sheet(file_handler.read())
            # Act
            holder_import_data: HolderImportData = RowImporterHolderData(sheet, 2).import_row()

        # Assert
        self.assert_holder(holder_import_data)

    def test_import_row_correct_without_holder_data(self):
        # Arrange
        file_handler: IO
        with open('./assets/correct/custody_one_line_correct_without_holder_data.xls', 'rb') as file_handler:
            sheet: Sheet = RowsImporter().obtain_sheet(file_handler.read())
            # Act
            holder_import_data: HolderImportData = RowImporterHolderData(sheet, 2).import_row()

        # Assert
        self.assertIsNone(holder_import_data)

    def test_import_row_error_no_email(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/holder/custody_one_line_no_email.xls', 'rb') as file_handler:
            sheet: Sheet = RowsImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(RowsImporterErrors) as errors:
                RowImporterHolderData(sheet, 2).import_row()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), RowsImporterErrorType.HOLDER_EMAIL_NOT_FOUND)

    def test_import_row_error_no_phone_number(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/holder/custody_one_line_no_phone.xls', 'rb') as file_handler:
            sheet: Sheet = RowsImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(RowsImporterErrors) as errors:
                RowImporterHolderData(sheet, 2).import_row()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), RowsImporterErrorType.HOLDER_PHONE_NUMBER_NOT_FOUND)

    def test_import_row_error_no_name_and_surnames(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/holder/custody_one_line_no_parent_name_and_surnames.xls', 'rb') as file_handler:
            sheet: Sheet = RowsImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(RowsImporterErrors) as errors:
                RowImporterHolderData(sheet, 2).import_row()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), RowsImporterErrorType.HOLDER_NAME_AND_SURNAMES_NOT_FOUND)

    def test_import_row_error_no_iban(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/holder/custody_one_line_no_iban.xls', 'rb') as file_handler:
            sheet: Sheet = RowsImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(RowsImporterErrors) as errors:
                RowImporterHolderData(sheet, 2).import_row()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), RowsImporterErrorType.HOLDER_IBAN_NOT_FOUND)

    def test_import_row_error_no_iban_and_no_email(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/holder/custody_one_line_no_iban_and_no_email.xls', 'rb') as file_handler:
            sheet: Sheet = RowsImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(RowsImporterErrors) as errors:
                RowImporterHolderData(sheet, 2).import_row()
        # Assert
        self.assertEqual(2, len(errors.exception.errors))
        self.assertIn(RowsImporterErrorType.HOLDER_IBAN_NOT_FOUND, errors.exception.errors)
        self.assertIn(RowsImporterErrorType.HOLDER_EMAIL_NOT_FOUND, errors.exception.errors)
