from typing import IO

from xlrd.sheet import Sheet

from ampa_manager.activity.use_cases.importers.custody.custody_child_import_data import CustodyChildImportData
from ampa_manager.activity.use_cases.importers.custody.line_importer_child_data import LineImporterChildData
from ampa_manager.activity.use_cases.importers.custody.lines_importer import LinesImporter
from ampa_manager.activity.use_cases.importers.custody.test_lines_importer_asserts import TestLineImporterAsserts


class TestLineImporterChildData(TestLineImporterAsserts):
    def test_import_lines_correct_complete(self):
        # Arrange
        file_handler: IO
        with open('./importers/custody/assets/correct/custody_one_line_correct_complete.xls', 'rb') as file_handler:
            sheet: Sheet = LinesImporter().obtain_sheet(file_handler.read())
            # Act
            custody_child_import_data: CustodyChildImportData = LineImporterChildData(sheet, 2).import_line()

        # Assert
        self.assert_child(custody_child_import_data)
