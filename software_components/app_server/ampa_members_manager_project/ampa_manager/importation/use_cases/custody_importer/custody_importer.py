from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.importation.use_cases.custody_importer.rows_importer.rows_importer import RowsImporter


class CustodyImporter:

    def __init__(self, file_content: bytes, custody_edition: CustodyEdition):
        self.__file_content = file_content
        self.__custody_edition = custody_edition

    def import_custody(self):
        RowsImporter(self.__file_content).import_rows()
