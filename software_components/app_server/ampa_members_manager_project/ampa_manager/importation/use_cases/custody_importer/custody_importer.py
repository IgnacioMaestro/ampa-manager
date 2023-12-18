from typing import Optional

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from .rows_importer.custody_import_row import CustodyImportRow
from .rows_importer.errors_in_row import ErrorsInRow
from .rows_importer.rows_importer import RowsImporter
from ...models.custody_importation import CustodyImportation
from ...models.custody_importation_row import CustodyImportationRow


class CustodyImporter:

    def __init__(self, file_name: str, file_content: bytes, custody_edition: CustodyEdition):
        self.__file_name = file_name
        self.__file_content = file_content
        self.__custody_edition = custody_edition

    def import_custody(self) -> tuple[Optional[CustodyImportation], Optional[list[ErrorsInRow]]]:
        imported_rows: Optional[list[CustodyImportRow]]
        error_rows: Optional[list[ErrorsInRow]]
        imported_rows, error_rows = RowsImporter(self.__file_content).import_rows()
        if error_rows is not None:
            return None, error_rows
        return self.__create_custody_importation(imported_rows), None

    def __create_custody_importation(self, imported_rows: list[CustodyImportRow]) -> CustodyImportation:
        custody_importation: CustodyImportation = CustodyImportation.objects.create(
            custody_edition=self.__custody_edition, filename=self.__file_name)
        # row: CustodyImportRow
        # for row in imported_rows:
        #     custody_importation_row: CustodyImportationRow = CustodyImportationRow.objects.create(
        #         row=row.row, custody_importation=custody_importation)

        return custody_importation
