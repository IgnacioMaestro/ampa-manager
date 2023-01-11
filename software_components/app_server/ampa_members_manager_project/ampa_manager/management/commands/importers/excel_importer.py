import xlrd


class ExcelImporter:

    def __init__(self, excel_file_path: str, sheet_number: int, first_row_index: int):
        self.first_row_index = first_row_index
        self.book, self.sheet = self.open_excel(excel_file_path, sheet_number)

    @staticmethod
    def open_excel(file_path: str, sheet_number: int):
        print(f'\nOpening sheet {sheet_number} from file {file_path}')
        book = xlrd.open_workbook(file_path)
        sheet = book.sheet_by_index(sheet_number)
        return book, sheet

    def import_rows(self):
        rows = []
        for row_index in range(self.first_row_index, self.sheet.nrows):
            row_columns = self.import_row_columns(row_index)
            rows.append(row_columns)
        return rows

    def import_row_columns(self, row_index: int):
        pass
