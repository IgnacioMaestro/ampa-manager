from typing import Optional

from .custody_child_import_data import CustodyChildImportData
from ampa_manager.activity.use_cases.importers.excel_extracted_types.holder_import_data import HolderImportData


class CustodyImportLine:
    def __init__(self, line: int, custody_child_import_data: CustodyChildImportData,
                 holder_import_data: Optional[HolderImportData] = None):
        self.__line: int = line
        self.__custody_child_import_data: CustodyChildImportData = custody_child_import_data
        self.__holder_import_data: Optional[HolderImportData] = holder_import_data

    @property
    def line(self) -> int:
        return self.__line

    @property
    def custody_child_import_data(self) -> CustodyChildImportData:
        return self.__custody_child_import_data

    @property
    def holder_import_data(self) -> Optional[HolderImportData]:
        return self.__holder_import_data

