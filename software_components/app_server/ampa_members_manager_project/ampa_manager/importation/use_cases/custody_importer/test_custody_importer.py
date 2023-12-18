from pathlib import Path
from typing import IO, Optional

from django.test import TestCase
from model_bakery import baker

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.importation.models.custody_importation import CustodyImportation
from ampa_manager.importation.use_cases.custody_importer.custody_importer import CustodyImporter
from ampa_manager.importation.use_cases.custody_importer.rows_importer.errors_in_row import ErrorsInRow
from ampa_manager.importation.use_cases.custody_importer.rows_importer.rows_importer_error import RowsImporterErrorType


class TestCustodyImporter(TestCase):
    LOCAL_PATH = Path(__file__).resolve().parent

    def test_import_custody_parse_errors(self):
        # Arrange
        custody_edition: CustodyEdition = baker.make('CustodyEdition')
        filename: str = 'custody_one_line_no_email.xls'
        file_content = self.obtain_file_content(self.LOCAL_PATH / './rows_importer/assets/errors/holder/' / filename)

        # Act
        custody_importation: Optional[CustodyImportation]
        errors_in_rows: Optional[list[ErrorsInRow]]
        custody_importation, errors_in_rows = CustodyImporter(
            filename, file_content, custody_edition).import_custody()

        self.assertIsNone(custody_importation)
        self.assertEqual(1, len(errors_in_rows))
        error_in_row = errors_in_rows.pop()
        self.assertEqual(error_in_row.get_row_number(), 2)
        self.assertEqual(error_in_row.get_errors(), [RowsImporterErrorType.HOLDER_EMAIL_NOT_FOUND])

    def test_import_custody_create(self):
        # Arrange
        custody_edition: CustodyEdition = baker.make('CustodyEdition')
        filename: str = 'custody_one_line_correct_complete.xls'
        file_content = self.obtain_file_content(self.LOCAL_PATH / './rows_importer/assets/correct/' / filename)

        # Act
        custody_importation: Optional[CustodyImportation]
        errors_in_rows: Optional[list[ErrorsInRow]]
        custody_importation, errors_in_rows = CustodyImporter(
            filename, file_content, custody_edition).import_custody()

        # Assert
        self.assertIsNone(errors_in_rows)
        self.assertIsNotNone(custody_importation)
        self.assertEqual(custody_importation.custody_edition, custody_edition)
        self.assertEqual(custody_importation.filename, filename)

    @classmethod
    def obtain_file_content(cls, file_path):
        file_handler: IO
        with open(file_path, 'rb') as file_handler:
            file_content: bytes = file_handler.read()
        return file_content
