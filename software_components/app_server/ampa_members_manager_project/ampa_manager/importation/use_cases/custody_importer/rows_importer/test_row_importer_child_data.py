from pathlib import Path
from typing import IO

from xlrd.sheet import Sheet

from .custody_child_import_data import CustodyChildImportData
from .row_importer_child_data import RowImporterChildData
from .rows_importer import RowsImporter
from .rows_importer_error import RowsImporterErrorType
from .test_rows_importer_asserts import TestRowImporterAsserts


class TestRowImporterChildData(TestRowImporterAsserts):
    LOCAL_PATH = Path(__file__).resolve().parent
    ROW_TO_IMPORT = 2

    def test_import_row_correct_complete(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/correct/custody_one_line_correct_complete.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        custody_child_import_data: CustodyChildImportData
        errors: list[RowsImporterErrorType]
        custody_child_import_data, errors = RowImporterChildData(sheet, self.ROW_TO_IMPORT).import_row()

        # Assert
        self.assertIsNone(errors)
        self.assert_child(custody_child_import_data)

    def test_import_row_error_no_name(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/errors/child/custody_one_line_no_name.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        custody_child_import_data: CustodyChildImportData
        errors: list[RowsImporterErrorType]
        custody_child_import_data, errors = RowImporterChildData(sheet, self.ROW_TO_IMPORT).import_row()

        # Assert
        self.assertIsNone(custody_child_import_data)
        self.assert_errors_to_check_in_errors([RowsImporterErrorType.CHILD_NAME_NOT_FOUND], errors)

    def test_import_row_error_no_surnames(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/errors/child/custody_one_line_no_surnames.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        custody_child_import_data: CustodyChildImportData
        errors: list[RowsImporterErrorType]
        custody_child_import_data, errors = RowImporterChildData(sheet, self.ROW_TO_IMPORT).import_row()

        # Assert
        self.assertIsNone(custody_child_import_data)
        self.assert_errors_to_check_in_errors([RowsImporterErrorType.CHILD_SURNAMES_NOT_FOUND], errors)

    def test_import_row_error_no_days(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/errors/child/custody_one_line_no_days.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        custody_child_import_data: CustodyChildImportData
        errors: list[RowsImporterErrorType]
        custody_child_import_data, errors = RowImporterChildData(sheet, self.ROW_TO_IMPORT).import_row()

        # Assert
        self.assertIsNone(custody_child_import_data)
        self.assert_errors_to_check_in_errors([RowsImporterErrorType.DAYS_ATTENDED_NOT_FOUND], errors)

    def test_import_row_error_no_days_int(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/errors/child/custody_one_line_no_days_int.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        custody_child_import_data: CustodyChildImportData
        errors: list[RowsImporterErrorType]
        custody_child_import_data, errors = RowImporterChildData(sheet, self.ROW_TO_IMPORT).import_row()

        # Assert
        self.assertIsNone(custody_child_import_data)
        self.assert_errors_to_check_in_errors(
            [RowsImporterErrorType.DAYS_ATTENDED_NOT_INTEGER], errors)

    def test_import_row_error_no_days_int_and_no_name(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/errors/child/custody_one_line_no_days_int_and_no_name.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        custody_child_import_data: CustodyChildImportData
        errors: list[RowsImporterErrorType]
        custody_child_import_data, errors = RowImporterChildData(sheet, self.ROW_TO_IMPORT).import_row()

        # Assert
        self.assertIsNone(custody_child_import_data)
        self.assert_errors_to_check_in_errors(
            [RowsImporterErrorType.DAYS_ATTENDED_NOT_INTEGER, RowsImporterErrorType.CHILD_NAME_NOT_FOUND],
            errors)

    def test_import_row_error_no_year_int(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/errors/child/custody_one_line_no_year_int.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        custody_child_import_data: CustodyChildImportData
        errors: list[RowsImporterErrorType]
        custody_child_import_data, errors = RowImporterChildData(sheet, self.ROW_TO_IMPORT).import_row()

        # Assert
        self.assertIsNone(custody_child_import_data)
        self.assert_errors_to_check_in_errors(
            [RowsImporterErrorType.CHILD_BIRTH_YEAR_NOT_INTEGER], errors)

    def test_import_row_error_no_name_and_no_surnames(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/errors/child/custody_one_line_no_name_and_no_surnames.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        custody_child_import_data: CustodyChildImportData
        errors: list[RowsImporterErrorType]
        custody_child_import_data, errors = RowImporterChildData(sheet, self.ROW_TO_IMPORT).import_row()

        # Assert
        self.assertIsNone(custody_child_import_data)
        self.assert_errors_to_check_in_errors(
            [RowsImporterErrorType.CHILD_NAME_NOT_FOUND, RowsImporterErrorType.CHILD_SURNAMES_NOT_FOUND],
            errors)

    def test_import_row_error_no_correct_level(self):
        # Arrange
        file_path = self.LOCAL_PATH / './assets/errors/child/custody_one_line_no_correct_level.xls'
        sheet = self.obtain_sheet(file_path)

        # Act
        custody_child_import_data: CustodyChildImportData
        errors: list[RowsImporterErrorType]
        custody_child_import_data, errors = RowImporterChildData(sheet, self.ROW_TO_IMPORT).import_row()

        # Assert
        self.assertIsNone(custody_child_import_data)
        self.assert_errors_to_check_in_errors([RowsImporterErrorType.CHILD_LEVEL_NOT_CORRECT], errors)

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
