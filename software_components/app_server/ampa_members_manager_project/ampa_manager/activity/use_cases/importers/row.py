from typing import Optional

from ampa_manager.activity.use_cases.importers.column import Column
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult


class Row:
    def __init__(self, row_index: int):
        self.row_index: int = row_index
        self.columns: dict[str, Column] = {}
        self.imported_models_results: list[ImportModelResult] = []
        self.error: Optional[str] = None

    def set_error(self, error: str):
        self.error = error

    def add_value(self, key: str, column: Column):
        self.columns[key] = column

    def add_imported_model_result(self, result: ImportModelResult):
        self.imported_models_results.append(result)

    def get_value(self, key: str):
        return self.columns[key].formatted_value

    @property
    def any_error(self) -> bool:
        if self.error:
            return True
        for column_value in self.columns.values():
            if column_value.error:
                return True
        for imported_model_result in self.imported_models_results:
            if imported_model_result.error:
                return True
        return False

    def get_errors(self) -> [str]:
        errors = []
        if self.error:
            errors.append(self.error)
        for column_value in self.columns.values():
            if column_value.error:
                errors.append(column_value.error)
        for imported_model_result in self.imported_models_results:
            if imported_model_result.error_message:
                errors.append(imported_model_result.error_message)
        return errors

    def get_warnings(self) -> [str]:
        warnings = []
        for imported_model_result in self.imported_models_results:
            if len(imported_model_result.warnings) > 0:
                warnings.extend(imported_model_result.warnings)
        return warnings
