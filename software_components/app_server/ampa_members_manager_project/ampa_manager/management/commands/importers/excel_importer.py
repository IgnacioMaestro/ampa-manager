from typing import Dict, List

import xlrd

from ampa_manager.management.commands.importers.excel_row import ExcelRow


class ExcelImporter:

    def __init__(self, excel_file_path: str, sheet_number: int, first_row_index: int, columns_settings):
        self.first_row_index = first_row_index
        self.book, self.sheet = self.open_excel(excel_file_path, sheet_number)
        self.columns_settings = columns_settings

    @staticmethod
    def open_excel(file_path: str, sheet_number: int):
        print(f'\nOpening sheet {sheet_number} from file {file_path}')
        book = xlrd.open_workbook(file_path)
        sheet = book.sheet_by_index(sheet_number)
        return book, sheet

    def import_rows(self) -> List[ExcelRow]:
        rows = []
        for row_index in range(self.first_row_index, self.sheet.nrows):
            columns = self.import_row_columns(row_index)
            rows.append(ExcelRow(row_index, columns))
        return rows

    def import_row_columns(self, row_index: int) -> dict:
        columns_values = {}
        for settings in self.columns_settings:
            index = settings[0]
            formatter = settings[1]
            name = settings[2]
            columns_values[name] = formatter(self.sheet.cell_value(rowx=row_index, colx=index))
        return columns_values
