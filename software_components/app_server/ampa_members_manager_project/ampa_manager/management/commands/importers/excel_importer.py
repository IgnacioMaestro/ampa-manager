import traceback
from typing import Dict, List

import xlrd
from django.core.exceptions import ValidationError

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
            print(f'Loading excel file from path "{self.file_path}"')
            book = xlrd.open_workbook(filename=self.file_path)
        elif self.file_content:
            print('Loading excel file from contents')
            book = xlrd.open_workbook(file_contents=self.file_content)
        else:
            print('Unable to load excel file')
            return None, None

        sheet = book.sheet_by_index(self.sheet_number)
        print(f'Loading excel sheet "{sheet.name}"')

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

    def import_rows(self) -> List[ExcelRow]:
        rows = []
        print(f'Importing rows {self.first_row_index + 1} - {self.sheet.nrows}')
        for row_index in range(self.first_row_index, self.sheet.nrows):
            rows.append(self.import_row(row_index))
        return rows

    def import_row(self, row_index: int) -> ExcelRow:
        row = ExcelRow(row_index)

        for column_settings in self.columns_settings:
            col_index = column_settings[0]
            formatter = column_settings[1]
            key = column_settings[2]
            value = self.get_cell_value(row_index, col_index)
            try:
                row.values[key] = formatter(value)
            except ValidationError as e:
                row.values[key] = None
                row.error = str(e)
                break

        return row

    def get_cell_value(self, row_index, col_index):
        return self.sheet.cell_value(rowx=row_index, colx=col_index)
