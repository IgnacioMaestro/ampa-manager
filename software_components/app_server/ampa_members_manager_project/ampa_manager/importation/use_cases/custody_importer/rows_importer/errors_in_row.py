from ampa_manager.importation.use_cases.custody_importer.rows_importer.rows_importer_error import RowsImporterErrorType


class ErrorsInRow:
    def __init__(self, row_number: int, errors: [RowsImporterErrorType]):
        self.__row_number = row_number
        self.__errors = errors

    def get_row_number(self):
        return self.__row_number

    def get_errors(self):
        return self.__errors

