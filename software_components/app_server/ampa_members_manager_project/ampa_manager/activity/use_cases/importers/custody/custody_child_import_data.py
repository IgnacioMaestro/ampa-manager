from ampa_manager.activity.use_cases.importers.excel_extracted_types.child_with_surnames_import_data import \
    ChildWithSurnamesImportData


class CustodyChildImportData:
    def __init__(self, child_with_surnames_import_data: ChildWithSurnamesImportData, days_attended: int):
        self.__child_with_surnames_import_data: ChildWithSurnamesImportData = child_with_surnames_import_data
        self.__days_attended: int = days_attended

    @property
    def child_with_surnames_import_data(self) -> ChildWithSurnamesImportData:
        return self.__child_with_surnames_import_data

    @property
    def days_attended(self) -> int:
        return self.__days_attended
