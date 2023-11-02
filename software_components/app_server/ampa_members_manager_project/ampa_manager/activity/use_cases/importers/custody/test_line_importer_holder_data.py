from typing import IO

from xlrd.sheet import Sheet

from ampa_manager.activity.use_cases.importers.custody.line_importer_holder_data import LineImporterHolderData
from ampa_manager.activity.use_cases.importers.custody.lines_importer import LinesImporter
from ampa_manager.activity.use_cases.importers.custody.lines_importer_error import LinesImporterErrors, \
    LinesImporterErrorType
from ampa_manager.activity.use_cases.importers.custody.test_lines_importer_asserts import TestLineImporterAsserts
from ampa_manager.activity.use_cases.importers.excel_extracted_types.holder_import_data import HolderImportData


class TestLineImporterHolderData(TestLineImporterAsserts):
    def test_import_lines_correct_complete(self):
        # Arrange
        file_handler: IO
        with open('./importers/custody/assets/correct/custody_one_line_correct_complete.xls', 'rb') as file_handler:
            sheet: Sheet = LinesImporter().obtain_sheet(file_handler.read())
            # Act
            holder_import_data: HolderImportData = LineImporterHolderData(sheet, 2).import_line()

        # Assert
        self.assert_holder(holder_import_data)

    def test_import_lines_correct_without_holder_data(self):
        # Arrange
        file_handler: IO
        with open('./importers/custody/assets/correct/custody_one_line_correct_without_holder_data.xls', 'rb') as file_handler:
            sheet: Sheet = LinesImporter().obtain_sheet(file_handler.read())
            # Act
            holder_import_data: HolderImportData = LineImporterHolderData(sheet, 2).import_line()

        # Assert
        self.assertIsNone(holder_import_data)

    def test_import_lines_error_no_email(self):
        # Arrange
        file_handler: IO
        with open('./importers/custody/assets/errors/holder/custody_one_line_no_email.xls', 'rb') as file_handler:
            sheet: Sheet = LinesImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(LinesImporterErrors) as errors:
                LineImporterHolderData(sheet, 2).import_line()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), LinesImporterErrorType.HOLDER_EMAIL_NOT_FOUND)

    def test_import_lines_error_no_phone_number(self):
        # Arrange
        file_handler: IO
        with open('./importers/custody/assets/errors/holder/custody_one_line_no_phone.xls', 'rb') as file_handler:
            sheet: Sheet = LinesImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(LinesImporterErrors) as errors:
                LineImporterHolderData(sheet, 2).import_line()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), LinesImporterErrorType.HOLDER_PHONE_NUMBER_NOT_FOUND)

    def test_import_lines_error_no_name_and_surnames(self):
        # Arrange
        file_handler: IO
        with open('./importers/custody/assets/errors/holder/custody_one_line_no_parent_name_and_surnames.xls', 'rb') as file_handler:
            sheet: Sheet = LinesImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(LinesImporterErrors) as errors:
                LineImporterHolderData(sheet, 2).import_line()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), LinesImporterErrorType.HOLDER_NAME_AND_SURNAMES_NOT_FOUND)

    def test_import_lines_error_no_iban(self):
        # Arrange
        file_handler: IO
        with open('./importers/custody/assets/errors/holder/custody_one_line_no_iban.xls', 'rb') as file_handler:
            sheet: Sheet = LinesImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(LinesImporterErrors) as errors:
                LineImporterHolderData(sheet, 2).import_line()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), LinesImporterErrorType.HOLDER_IBAN_NOT_FOUND)

    def test_import_lines_error_no_iban_and_no_email(self):
        # Arrange
        file_handler: IO
        with open('./importers/custody/assets/errors/holder/custody_one_line_no_iban_and_no_email.xls', 'rb') as file_handler:
            sheet: Sheet = LinesImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(LinesImporterErrors) as errors:
                LineImporterHolderData(sheet, 2).import_line()
        # Assert
        self.assertEqual(2, len(errors.exception.errors))
        self.assertIn(LinesImporterErrorType.HOLDER_IBAN_NOT_FOUND, errors.exception.errors)
        self.assertIn(LinesImporterErrorType.HOLDER_EMAIL_NOT_FOUND, errors.exception.errors)
