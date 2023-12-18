from .parent_import_data import ParentImportData


class HolderImportData:
    def __init__(self, parent_import_data: ParentImportData, iban: str):
        self.__parent_import_data: ParentImportData = parent_import_data
        self.__iban: str = iban

    @property
    def parent_import_data(self) -> ParentImportData:
        return self.__parent_import_data

    @property
    def iban(self) -> str:
        return self.__iban
