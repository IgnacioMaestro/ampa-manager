from typing import Optional

from ampa_manager.importation.use_cases.custody_importer.excel_extracted_types.holder_import_data import \
    HolderImportData
from .custody_child_import_data import CustodyChildImportData


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

    @property
    def child_surnames(self) -> str:
        return self.__custody_child_import_data.child_with_surnames_import_data.surnames

    @property
    def child_name(self) -> str:
        return self.__custody_child_import_data.child_with_surnames_import_data.child_import_data.name

    @property
    def child_year_of_birth(self) -> Optional[int]:
        return self.__custody_child_import_data.child_with_surnames_import_data.child_import_data.birth_year

    @property
    def child_level(self) -> str:
        return self.__custody_child_import_data.child_with_surnames_import_data.child_import_data.level

    @property
    def days_attended(self) -> int:
        return self.__custody_child_import_data.days_attended
