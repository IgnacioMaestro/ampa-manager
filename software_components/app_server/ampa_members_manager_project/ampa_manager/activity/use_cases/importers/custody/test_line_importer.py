from typing import IO

from xlrd.sheet import Sheet

from ampa_manager.activity.use_cases.importers.custody.custody_import_line import CustodyImportLine
from ampa_manager.activity.use_cases.importers.custody.line_importer import LineImporter
from ampa_manager.activity.use_cases.importers.custody.lines_importer import LinesImporter
from ampa_manager.activity.use_cases.importers.custody.test_lines_importer_asserts import TestLineImporterAsserts


class TestLineImporter(TestLineImporterAsserts):
    def test_import_lines_correct_complete(self):
        # Arrange
        file_handler: IO
        with open('./importers/custody/assets/correct/custody_one_line_correct_complete.xls', 'rb') as file_handler:
            sheet: Sheet = LinesImporter().obtain_sheet(file_handler.read())
            # Act
            custody_import_line: CustodyImportLine = LineImporter(sheet, 2).import_line()

        # Assert
        self.assertEqual(custody_import_line.line, 3)
        self.assert_child(custody_import_line.custody_child_import_data)
        self.assert_holder(custody_import_line.holder_import_data)
