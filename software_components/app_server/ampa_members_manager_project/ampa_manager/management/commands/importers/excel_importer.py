import traceback
from typing import Dict, List

import xlrd

from ampa_manager.management.commands.importers.excel_row import ExcelRow


class ExcelImporter:

    def __init__(self, sheet_number: int, first_row_index: int, columns_settings, file_path: str = None, file_content=None):
        self.sheet_number = sheet_number
        self.first_row_index = first_row_index
        self.columns_settings = columns_settings
        self.file_path = file_path
        self.file_content = file_content

        self.book, self.sheet = self.open_excel()

    def open_excel(self):
        if self.file_path:
            print(f'Loading excel file from path {self.file_path}')
            book = xlrd.open_workbook(filename=self.file_path)
        elif self.file_content:
            print('Loading excel file from contents')
            book = xlrd.open_workbook(file_contents=self.file_content)
        else:
            print('Unable to load excel file')
            return None, None

        print(f'Loading excel sheet number {self.sheet_number+1}')
        sheet = book.sheet_by_index(self.sheet_number)
        return book, sheet

    def get_row_range(self, columns_indexes, row_index, formatter):
        values = []
        for column_index in columns_indexes:
            try:
                value = self.sheet.cell_value(rowx=row_index, colx=column_index)
                value = formatter(value)
            except IndexError:
                value = None
            values.append(value)
        return values

    def get_rows(self) -> List[ExcelRow]:
        rows = []
        print(f'Importing rows {self.first_row_index + 1} - {self.sheet.nrows+1}')
        for row_index in range(self.first_row_index, self.sheet.nrows):
            row = ExcelRow(row_index)
            try:
                row.values = self.import_row_columns(row.index)
            except Exception as e:
                row.error = str(e)
            rows.append(row)
        return rows

    def import_row_columns(self, row_index: int) -> dict:
        columns_values = {}
        for settings in self.columns_settings:
            index = settings[0]
            formatter = settings[1]
            name = settings[2]
            try:
                columns_values[name] = formatter(self.sheet.cell_value(rowx=row_index, colx=index))
            except IndexError:
                columns_values[name] = None
        return columns_values
