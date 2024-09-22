from typing import List


class ExcelRow:

    def __init__(self, index: int):
        self.index = index
        self.values = {}
        self.error = None

    @property
    def number(self):
        return self.index + 1

    def get(self, column_name, default_value=None):
        return self.values.get(column_name, default_value)

    def any_column_has_value(self, columns_names: List[str]):
        for name in columns_names:
            if self.get(column_name=name) is not None:
                return True
