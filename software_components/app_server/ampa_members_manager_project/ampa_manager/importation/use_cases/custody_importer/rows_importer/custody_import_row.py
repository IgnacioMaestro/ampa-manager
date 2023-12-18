from typing import Optional

from .custody_child_import_data import CustodyChildImportData
from ampa_manager.importation.use_cases.custody_importer.excel_extracted_types.holder_import_data import HolderImportData


class CustodyImportRow:
    def __init__(self, row: int, custody_child_import_data: CustodyChildImportData,
                 holder_import_data: Optional[HolderImportData] = None):
        self.__row: int = row
        self.__custody_child_import_data: CustodyChildImportData = custody_child_import_data
        self.__holder_import_data: Optional[HolderImportData] = holder_import_data

    @property
    def row(self) -> int:
        return self.__row

    @property
    def custody_child_import_data(self) -> CustodyChildImportData:
        return self.__custody_child_import_data

    @property
    def holder_import_data(self) -> Optional[HolderImportData]:
        return self.__holder_import_data

