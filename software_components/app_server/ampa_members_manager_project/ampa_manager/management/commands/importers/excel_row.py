from typing import List


class ExcelRow:

    def __init__(self, index: int, values: dict):
        self.index = index
        self.values = values

    def get(self, column_name, default_value=None):
        return self.values.get(column_name, default_value)

    def any_column_has_value(self, columns_names: List[str]):
        for name in columns_names:
            if self.get(column_name=name) is not None:
                return True
