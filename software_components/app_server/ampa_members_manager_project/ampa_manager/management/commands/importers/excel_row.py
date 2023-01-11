class ExcelRow:

    def __init__(self, index: int, values: dict):
        self.index = index
        self.values = values

    def get(self, column_name, default_value=None):
        return self.values.get(column_name, default_value)
