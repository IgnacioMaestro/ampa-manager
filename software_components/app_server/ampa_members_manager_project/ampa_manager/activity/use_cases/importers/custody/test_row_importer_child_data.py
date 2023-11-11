from typing import IO

from xlrd.sheet import Sheet

from ampa_manager.activity.use_cases.importers.custody.custody_child_import_data import CustodyChildImportData
from ampa_manager.activity.use_cases.importers.custody.row_importer_child_data import RowImporterChildData
from ampa_manager.activity.use_cases.importers.custody.rows_importer import RowsImporter
from ampa_manager.activity.use_cases.importers.custody.rows_importer_error import RowsImporterErrors, \
    RowsImporterErrorType, RowsImporterTotalErrors
from ampa_manager.activity.use_cases.importers.custody.test_rows_importer_asserts import TestRowImporterAsserts


class TestRowImporterChildData(TestRowImporterAsserts):
    def test_import_row_correct_complete(self):
        # Arrange
        file_handler: IO
        with open('./assets/correct/custody_one_line_correct_complete.xls', 'rb') as file_handler:
            sheet: Sheet = RowsImporter().obtain_sheet(file_handler.read())
            # Act
            custody_child_import_data: CustodyChildImportData = RowImporterChildData(sheet, 2).import_row()

        # Assert
        self.assert_child(custody_child_import_data)

    def test_import_row_error_no_name(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/child/custody_one_line_no_name.xls', 'rb') as file_handler:
            sheet: Sheet = RowsImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(RowsImporterTotalErrors) as errors:
                RowImporterChildData(sheet, 2).import_row()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), RowsImporterErrorType.NAME_NOT_FOUND)

    def test_import_row_error_no_surnames(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/child/custody_one_line_no_surnames.xls', 'rb') as file_handler:
            sheet: Sheet = RowsImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(RowsImporterTotalErrors) as errors:
                RowImporterChildData(sheet, 2).import_row()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), RowsImporterErrorType.SURNAMES_NOT_FOUND)

    def test_import_row_error_no_days(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/child/custody_one_line_no_days.xls', 'rb') as file_handler:
            sheet: Sheet = RowsImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(RowsImporterTotalErrors) as errors:
                RowImporterChildData(sheet, 2).import_row()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), RowsImporterErrorType.DAYS_ATTENDED_NOT_FOUND)

    def test_import_row_error_no_days_int(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/child/custody_one_line_no_days_int.xls', 'rb') as file_handler:
            sheet: Sheet = RowsImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(RowsImporterTotalErrors) as errors:
                RowImporterChildData(sheet, 2).import_row()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), RowsImporterErrorType.DAYS_ATTENDED_NOT_INTEGER)

    def test_import_row_error_no_days_int_and_no_name(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/child/custody_one_line_no_days_int_and_no_name.xls', 'rb') as file_handler:
            sheet: Sheet = RowsImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(RowsImporterTotalErrors) as errors:
                RowImporterChildData(sheet, 2).import_row()
        # Assert
        self.assertEqual(2, len(errors.exception.errors))
        self.assertIn(RowsImporterErrorType.DAYS_ATTENDED_NOT_INTEGER, errors.exception.errors)
        self.assertIn(RowsImporterErrorType.NAME_NOT_FOUND, errors.exception.errors)

    def test_import_row_error_no_year_int(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/child/custody_one_line_no_year_int.xls', 'rb') as file_handler:
            sheet: Sheet = RowsImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(RowsImporterTotalErrors) as errors:
                RowImporterChildData(sheet, 2).import_row()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), RowsImporterErrorType.BIRTH_YEAR_NOT_INTEGER)

    def test_import_row_error_no_name_and_no_surnames(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/child/custody_one_line_no_name_and_no_surnames.xls', 'rb') as file_handler:
            sheet: Sheet = RowsImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(RowsImporterTotalErrors) as errors:
                RowImporterChildData(sheet, 2).import_row()
        # Assert
        self.assertEqual(2, len(errors.exception.errors))
        self.assertIn(RowsImporterErrorType.NAME_NOT_FOUND, errors.exception.errors)
        self.assertIn(RowsImporterErrorType.SURNAMES_NOT_FOUND, errors.exception.errors)

    def test_import_row_error_no_correct_level(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/child/custody_one_line_no_correct_level.xls', 'rb') as file_handler:
            sheet: Sheet = RowsImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(RowsImporterTotalErrors) as errors:
                RowImporterChildData(sheet, 2).import_row()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), RowsImporterErrorType.LEVEL_NOT_CORRECT)
