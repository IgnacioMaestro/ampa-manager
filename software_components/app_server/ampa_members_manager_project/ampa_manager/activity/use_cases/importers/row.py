from typing import Optional

from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.use_cases.importers.column import Column
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult


class Row:
    STATE_OK = 'ok'
    STATE_WARNING = 'warning'
    STATE_ERROR = 'error'

    STATES_LABELS = {
        STATE_OK: _('Ok'),
        STATE_WARNING: _('Warning'),
        STATE_ERROR: _('Error')
    }

    def __init__(self, row_index: int):
        self.row_index: int = row_index
        self.columns: dict[str, Column] = {}
        self.imported_models_results: list[ImportModelResult] = []
        self.error: Optional[str] = None

    def __str__(self) -> str:
        return f'Index {self.row_index}, {len(self.columns)} columns, {len(self.imported_models_results)} models'

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

    @property
    def any_warning(self) -> bool:
        for imported_model_result in self.imported_models_results:
            if len(imported_model_result.warnings) > 0:
                return True
        return False

    @property
    def state(self) -> str:
        if self.any_error:
            return self.STATE_ERROR
        if self.any_warning:
            return self.STATE_WARNING
        return self.STATE_OK

    @property
    def state_label(self) -> str:
        return self.STATES_LABELS.get(self.state, self.state)

    def get_errors(self) -> [str]:
        errors = []
        if self.error:
            errors.append(self.error)
        for column_key, column_value in self.columns.items():
            if column_value.error:
                error = f'{column_key}: {column_value.error}'
                errors.append(error)
        for imported_model_result in self.imported_models_results:
            if imported_model_result.error_message:
                error = f'{imported_model_result.model_verbose_name}: {imported_model_result.error_message}'
                errors.append(error)
        return errors

    def get_warnings(self) -> [str]:
        warnings = []
        for imported_model_result in self.imported_models_results:
            if len(imported_model_result.warnings) > 0:
                warnings.extend(imported_model_result.warnings)
        return warnings
