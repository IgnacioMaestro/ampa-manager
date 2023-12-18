from typing import Optional

from xlrd.sheet import Sheet

from ampa_manager.importation.models.custody_child_import_data import CustodyChildImportData
from .custody_import_row import CustodyImportRow
from .row_importer_child_data import RowImporterChildData
from .row_importer_holder_data import RowImporterHolderData
from .rows_importer_error import RowsImporterErrorType


class RowImporter:
    def __init__(self, sheet: Sheet, row_index: int):
        self.__sheet = sheet
        self.__row_index = row_index

    def import_row(self) -> tuple[Optional[CustodyImportRow], Optional[list[RowsImporterErrorType]]]:
        custody_child_import_data: Optional[CustodyChildImportData]
        child_errors: Optional[list[RowsImporterErrorType]]
        custody_child_import_data, child_errors = RowImporterChildData(self.__sheet, self.__row_index).import_row()
        holder_import_data: Optional[CustodyChildImportData]
        holder_errors: Optional[list[RowsImporterErrorType]]
        holder_import_data, holder_errors = RowImporterHolderData(self.__sheet, self.__row_index).import_row()
        accumulated_errors: list[RowsImporterErrorType] = self.accumulate_errors(child_errors, holder_errors)
        if len(accumulated_errors) > 0:
            return None, accumulated_errors
        return (CustodyImportRow(self.__row_index + 1, custody_child_import_data, holder_import_data)), None

    @classmethod
    def accumulate_errors(cls, child_errors: Optional[list[RowsImporterErrorType]],
                          holder_errors: Optional[list[RowsImporterErrorType]]) -> list[RowsImporterErrorType]:
        accumulated_errors: list[RowsImporterErrorType] = []
        if child_errors is not None:
            accumulated_errors.extend(child_errors)
        if holder_errors is not None:
            accumulated_errors.extend(holder_errors)
        return accumulated_errors
