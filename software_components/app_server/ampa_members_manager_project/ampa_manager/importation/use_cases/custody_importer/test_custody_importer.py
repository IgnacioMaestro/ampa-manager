from pathlib import Path
from typing import IO, Optional

from django.test import TestCase
from model_bakery import baker

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.importation.models.custody_importation import CustodyImportation
from ampa_manager.importation.models.custody_importation_row import CustodyImportationRow
from ampa_manager.importation.models.levels import Levels
from .custody_importer import CustodyImporter
from .rows_importer.errors_in_row import ErrorsInRow
from .rows_importer.rows_importer_error import RowsImporterErrorType


class TestCustodyImporter(TestCase):
    LOCAL_PATH = Path(__file__).resolve().parent
    FILENAME_NO_EMAIL: str = 'custody_one_line_no_email.xls'
    FILENAME_NO_EMAIL_PATH: Path = LOCAL_PATH / './rows_importer/assets/errors/holder/' / FILENAME_NO_EMAIL
    FILENAME_CORRECT: str = 'custody_one_line_correct_complete.xls'
    FILENAME_CORRECT_PATH: Path = LOCAL_PATH / './rows_importer/assets/correct/' / FILENAME_CORRECT

    custody_edition: CustodyEdition

    @classmethod
    def setUpTestData(cls):
        cls.custody_edition = baker.make(CustodyEdition)

    def test_import_custody_parse_errors(self):
        # Arrange
        file_content = self.obtain_file_content(self.FILENAME_NO_EMAIL_PATH)

        # Act
        custody_importation: Optional[CustodyImportation]
        errors_in_rows: Optional[list[ErrorsInRow]]
        custody_importation, errors_in_rows = CustodyImporter(
            self.FILENAME_NO_EMAIL, file_content, self.custody_edition).import_custody()

        # Assert
        self.assertIsNone(custody_importation)
        self.assertEqual(1, len(errors_in_rows))
        error_in_row = errors_in_rows.pop()
        self.assertEqual(error_in_row.get_row_number(), 2)
        self.assertEqual(error_in_row.get_errors(), [RowsImporterErrorType.HOLDER_EMAIL_NOT_FOUND])

    def test_import_custody_create(self):
        # Arrange
        file_content = self.obtain_file_content(self.FILENAME_CORRECT_PATH)

        # Act
        custody_importation: Optional[CustodyImportation]
        errors_in_rows: Optional[list[ErrorsInRow]]
        custody_importation, errors_in_rows = CustodyImporter(
            self.FILENAME_CORRECT, file_content, self.custody_edition).import_custody()

        # Assert
        self.assertIsNone(errors_in_rows)
        self.assertIsNotNone(custody_importation)
        self.assertEqual(custody_importation.custody_edition, self.custody_edition)
        self.assertEqual(custody_importation.filename, self.FILENAME_CORRECT)
        self.assertEqual(CustodyImportationRow.objects.filter(importation=custody_importation).count(), 1)
        custody_import_row: CustodyImportationRow = CustodyImportationRow.objects.get(importation=custody_importation)
        self.assertEqual(custody_import_row.surnames, 'Lopez Gonzalez')
        self.assertEqual(custody_import_row.name, 'Nahia')
        self.assertEqual(custody_import_row.year_of_birth, 2013)
        self.assertEqual(custody_import_row.level, Levels.LH4)
        self.assertEqual(custody_import_row.days_attended, 17)

    @classmethod
    def obtain_file_content(cls, file_path):
        file_handler: IO
        with open(file_path, 'rb') as file_handler:
            file_content: bytes = file_handler.read()
        return file_content
