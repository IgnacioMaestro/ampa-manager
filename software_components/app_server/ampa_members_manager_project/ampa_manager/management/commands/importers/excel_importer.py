import xlrd


class ExcelImporter:

    def __init__(self, excel_file_path: str, sheet_number: int, first_row_index: int):
        self.first_row_index = first_row_index
        self.book, self.sheet = self.open_excel(excel_file_path, sheet_number)

    def open_excel(self, file_path: str, sheet_number: int):
        print(f'\nOpening sheet {sheet_number} from file {file_path}')
        book = xlrd.open_workbook(file_path)
        sheet = book.sheet_by_index(sheet_number)
        return book, sheet

    def get_data(self):
        data = []
        for row_index in range(self.first_row_index, self.sheet.nrows):
            row_fields = self.import_row_fields(row_index)
            data.append(row_fields)
        return data

    def import_row_fields(self, row_index: int):
        pass
