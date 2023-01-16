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

        print(f'Loading excel sheet number {self.sheet_number}')
        sheet = book.sheet_by_index(self.sheet_number)
        return book, sheet

    def import_rows(self) -> List[ExcelRow]:
        rows = []
        for row_index in range(self.first_row_index, self.sheet.nrows):
            columns_values = self.import_row_columns(row_index)
            rows.append(ExcelRow(row_index, columns_values))
        return rows

    def import_row_columns(self, row_index: int) -> dict:
        columns_values = {}
        for settings in self.columns_settings:
            index = settings[0]
            formatter = settings[1]
            name = settings[2]
            columns_values[name] = formatter(self.sheet.cell_value(rowx=row_index, colx=index))
        return columns_values
