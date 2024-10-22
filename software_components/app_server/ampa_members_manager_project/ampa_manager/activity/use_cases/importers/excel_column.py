from ampa_manager.activity.use_cases.importers.excel_column_definition import ExcelColumnDefinition
from ampa_manager.utils.string_utils import StringUtils


class ExcelColumn:

    def __init__(self, index: int, column_definition: ExcelColumnDefinition):
        self.index = index
        self.formatter = column_definition.formatter
        self.key = column_definition.key
        self.label = column_definition.label
        self.short_label = column_definition.short_label
        self.letter = StringUtils.get_excel_column_letter(index).upper()

    @classmethod
    def get_column_short_label(cls, columns: list, key: str):
        for column in columns:
            if column.key == key:
                return column.short_label
        return ''
