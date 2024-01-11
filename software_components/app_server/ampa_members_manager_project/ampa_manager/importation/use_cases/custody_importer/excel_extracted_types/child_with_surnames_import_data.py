from .child_import_data import ChildImportData


class ChildWithSurnamesImportData:
    def __init__(self, child_import_data: ChildImportData, surnames: str):
        self.__child_import_data: ChildImportData = child_import_data
        self.__surnames: str = surnames

    @property
    def child_import_data(self) -> ChildImportData:
        return self.__child_import_data

    @property
    def surnames(self) -> str:
        return self.__surnames
