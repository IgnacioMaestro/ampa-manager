import xlrd

from ampa_manager.activity.use_cases.importers.column import Column
from ampa_manager.activity.use_cases.importers.row import Row


class ExcelDataExtractor:
    def __init__(self, excel_content, sheet_number: int, first_row_index: int, columns_to_extract: list):
        self.excel_content = excel_content
        self.sheet_number = sheet_number
        self.first_row_index = first_row_index
        self.columns_to_extract = columns_to_extract
        self.book = xlrd.open_workbook(file_contents=self.excel_content)
        self.sheet = self.book.sheet_by_index(self.sheet_number)

        if self.first_row_index > self.sheet.nrows:
            raise Exception('Invalid first row index')

    def extract(self) -> list[Row]:
        rows = []
        for row_index in range(self.first_row_index, self.sheet.nrows):
            row = Row(row_index)

            for column_settings in self.columns_to_extract:
                col_index = column_settings[0]
                formatter = column_settings[1]
                key = column_settings[2]
                row.add_value(key, self.get_column(row_index, col_index, formatter))

            rows.append(row)
        return rows

    def get_column(self, row_index: int, col_index: int, formatter) -> Column:
        raw_value = None
        formatted_value = None
        error = None

        try:
            raw_value = self.sheet.cell_value(rowx=row_index, colx=col_index)
            formatted_value = formatter(raw_value)
        except Exception as e:
            error = str(e)

        return Column(raw_value, formatted_value, error)
