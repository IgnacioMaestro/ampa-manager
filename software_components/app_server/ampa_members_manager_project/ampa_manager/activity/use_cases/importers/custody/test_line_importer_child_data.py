from typing import IO

from xlrd.sheet import Sheet

from ampa_manager.activity.use_cases.importers.custody.custody_child_import_data import CustodyChildImportData
from ampa_manager.activity.use_cases.importers.custody.line_importer_child_data import LineImporterChildData
from ampa_manager.activity.use_cases.importers.custody.lines_importer import LinesImporter
from ampa_manager.activity.use_cases.importers.custody.lines_importer_error import LinesImporterErrors, \
    LinesImporterErrorType, LinesImporterTotalErrors
from ampa_manager.activity.use_cases.importers.custody.test_lines_importer_asserts import TestLineImporterAsserts


class TestLineImporterChildData(TestLineImporterAsserts):
    def test_import_lines_correct_complete(self):
        # Arrange
        file_handler: IO
        with open('./assets/correct/custody_one_line_correct_complete.xls', 'rb') as file_handler:
            sheet: Sheet = LinesImporter().obtain_sheet(file_handler.read())
            # Act
            custody_child_import_data: CustodyChildImportData = LineImporterChildData(sheet, 2).import_line()

        # Assert
        self.assert_child(custody_child_import_data)

    def test_import_lines_error_no_name(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/child/custody_one_line_no_name.xls', 'rb') as file_handler:
            sheet: Sheet = LinesImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(LinesImporterTotalErrors) as errors:
                LineImporterChildData(sheet, 2).import_line()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), LinesImporterErrorType.NAME_NOT_FOUND)

    def test_import_lines_error_no_surnames(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/child/custody_one_line_no_surnames.xls', 'rb') as file_handler:
            sheet: Sheet = LinesImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(LinesImporterTotalErrors) as errors:
                LineImporterChildData(sheet, 2).import_line()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), LinesImporterErrorType.SURNAMES_NOT_FOUND)

    def test_import_lines_error_no_days(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/child/custody_one_line_no_days.xls', 'rb') as file_handler:
            sheet: Sheet = LinesImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(LinesImporterTotalErrors) as errors:
                LineImporterChildData(sheet, 2).import_line()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), LinesImporterErrorType.DAYS_ATTENDED_NOT_FOUND)

    def test_import_lines_error_no_days_int(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/child/custody_one_line_no_days_int.xls', 'rb') as file_handler:
            sheet: Sheet = LinesImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(LinesImporterTotalErrors) as errors:
                LineImporterChildData(sheet, 2).import_line()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), LinesImporterErrorType.DAYS_ATTENDED_NOT_INTEGER)

    def test_import_lines_error_no_days_int_and_no_name(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/child/custody_one_line_no_days_int_and_no_name.xls', 'rb') as file_handler:
            sheet: Sheet = LinesImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(LinesImporterTotalErrors) as errors:
                LineImporterChildData(sheet, 2).import_line()
        # Assert
        self.assertEqual(2, len(errors.exception.errors))
        self.assertIn(LinesImporterErrorType.DAYS_ATTENDED_NOT_INTEGER, errors.exception.errors)
        self.assertIn(LinesImporterErrorType.NAME_NOT_FOUND, errors.exception.errors)

    def test_import_lines_error_no_year_int(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/child/custody_one_line_no_year_int.xls', 'rb') as file_handler:
            sheet: Sheet = LinesImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(LinesImporterTotalErrors) as errors:
                LineImporterChildData(sheet, 2).import_line()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), LinesImporterErrorType.BIRTH_YEAR_NOT_INTEGER)

    def test_import_lines_error_no_name_and_no_surnames(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/child/custody_one_line_no_name_and_no_surnames.xls', 'rb') as file_handler:
            sheet: Sheet = LinesImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(LinesImporterTotalErrors) as errors:
                LineImporterChildData(sheet, 2).import_line()
        # Assert
        self.assertEqual(2, len(errors.exception.errors))
        self.assertIn(LinesImporterErrorType.NAME_NOT_FOUND, errors.exception.errors)
        self.assertIn(LinesImporterErrorType.SURNAMES_NOT_FOUND, errors.exception.errors)

    def test_import_lines_error_no_correct_level(self):
        # Arrange
        file_handler: IO
        with open('./assets/errors/child/custody_one_line_no_correct_level.xls', 'rb') as file_handler:
            sheet: Sheet = LinesImporter().obtain_sheet(file_handler.read())
            # Act
            with self.assertRaises(LinesImporterTotalErrors) as errors:
                LineImporterChildData(sheet, 2).import_line()
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), LinesImporterErrorType.LEVEL_NOT_CORRECT)
