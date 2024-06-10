from django.core.exceptions import ValidationError

from ampa_manager.utils.excel.import_model_result import ImportModelResult


class RowToImport:
    STATUS_EMPTY = 'empty'
    STATUS_ERROR = 'error'

    def __init__(self, index: int, values: dict, columns_to_import: list[list]):
        self.index = index
        self.raw_values = values
        self.cleaned_values = {}
        self.status = None
        self.error = None
        self.partial_results = []
        self.clean_values(columns_to_import)

    @property
    def number(self):
        return self.index + 1

    def set_empty(self):
        self.status = self.STATUS_EMPTY
        self.error = None

    def set_error(self, error: str):
        self.status = self.STATUS_ERROR
        self.error = error

    def add_partial_result(self, partial_result: ImportModelResult):
        self.partial_results.append(partial_result)

    def clean_values(self, columns_to_import: list[list]):
        for column_settings in columns_to_import:
            col_index = column_settings[0]
            formatter = column_settings[1]
            key = column_settings[2]

            value = self.raw_values[col_index]

            try:
                self.clean_values[key] = formatter(value)
            except ValidationError as e:
                self.clean_values[key] = None
                self.set_error(f'Error formatting column: {key} = {value}: {str(e)}')
                break

    def is_empty(self) -> bool:
        for value in self.cleaned_values.values():
            if value not in [None, '', '0', 0]:
                return False
        return True

    def get(self, column_name, default_value=None):
        return self.cleaned_values.get(column_name, default_value)
