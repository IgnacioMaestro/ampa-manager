from typing import IO

from .custody_import_line import CustodyImportLine
from .lines_importer import LinesImporter
from .lines_importer_error import LinesImporterErrors, LinesImporterErrorType
from .test_lines_importer_asserts import TestLineImporterAsserts


class TestLinesImporter(TestLineImporterAsserts):
    def test_import_lines_correct_complete(self):
        # Arrange
        file_handler: IO
        with open('./importers/custody/assets/correct/custody_one_line_correct_complete.xls', 'rb') as file_handler:
            # Act
            imported_lines: list[CustodyImportLine] = LinesImporter().import_lines(file_handler.read())

        # Assert
        self.assertEqual(1, len(imported_lines))
        imported_line: CustodyImportLine = imported_lines.pop()
        self.assertEqual(imported_line.line, 3)
        self.assert_child(imported_line.custody_child_import_data)
        self.assert_holder(imported_line.holder_import_data)

    def test_import_lines_correct_without_holder_data(self):
        # Arrange
        file_handler: IO
        with open('./importers/custody/assets/correct/custody_one_line_correct_without_holder_data.xls', 'rb') as file_handler:
            # Act
            imported_lines: list[CustodyImportLine] = LinesImporter().import_lines(file_handler.read())

        # Assert
        self.assertEqual(1, len(imported_lines))
        imported_line: CustodyImportLine = imported_lines.pop()
        self.assertEqual(imported_line.line, 3)
        self.assert_child(imported_line.custody_child_import_data)
        self.assertIsNone(imported_line.holder_import_data)

    def test_import_lines_error_no_email(self):
        # Arrange
        file_handler: IO
        with open('./importers/custody/assets/errors/holder/custody_one_line_no_email.xls', 'rb') as file_handler:
            # Act
            with self.assertRaises(LinesImporterErrors) as errors:
                LinesImporter().import_lines(file_handler.read())
        # Assert
        self.assertEqual(1, len(errors.exception.errors))
        self.assertEqual(errors.exception.errors.pop(), LinesImporterErrorType.HOLDER_EMAIL_NOT_FOUND)
