from typing import Optional

from ampa_manager.activity.use_cases.importers.column import Column
from ampa_manager.utils.excel.import_model_result import ImportModelResult


class Row:
    def __init__(self, row_index: int):
        self.row_index: int = row_index
        self.columns: dict[str, Column] = {}
        self.imported_models: list[ImportModelResult] = []
        self.error: Optional[str] = None

    def set_error(self, error: str):
        self.error = error

    def add_value(self, key: str, column: Column):
        self.columns[key] = column

    def add_imported_model(self, imported_model: ImportModelResult):
        self.imported_models.append(imported_model)

    def get_value(self, key: str):
        return self.columns[key].formatted_value

    @property
    def any_error(self) -> bool:
        if self.error:
            return True
        for value in self.columns.values():
            if value.error:
                return True
        return False