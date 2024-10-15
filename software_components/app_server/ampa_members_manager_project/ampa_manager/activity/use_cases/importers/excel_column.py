from typing import Callable

from ampa_manager.utils.string_utils import StringUtils


class ExcelColumn:

    def __init__(self, index: int, formatter: Callable, key: str, label: str, short_label: str):
        self.index = index
        self.formatter = formatter
        self.key = key
        self.label = label
        self.short_label = short_label
        self.letter = StringUtils.get_excel_column_letter(index).upper()

    @classmethod
    def get_column_short_label(cls, columns: list, key: str):
        for column in columns:
            if column.key == key:
                return column.short_label
        return ''
