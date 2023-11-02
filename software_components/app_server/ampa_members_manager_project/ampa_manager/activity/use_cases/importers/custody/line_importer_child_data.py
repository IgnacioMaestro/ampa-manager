from typing import Optional

from xlrd.sheet import Sheet

from ampa_manager.academic_course.models.level_constants import LevelConstants
from ampa_manager.utils.fields_formatters import FieldsFormatters
from .custody_child_import_data import CustodyChildImportData
from .lines_importer_error import LinesImporterError, LinesImporterErrorType, LinesImporterErrors
from ..excel_extracted_types.child_import_data import ChildImportData
from ..excel_extracted_types.child_with_surnames_import_data import ChildWithSurnamesImportData


class LineImporterChildData:
    NAME_COLUMN = 4
    SURNAMES_COLUMN = 5
    BIRTH_YEAR_COLUMN = 6
    # LEVEL_COLUMN = 7
    DAYS_ATTENDED_COLUMN = 8
    def __init__(self, sheet: Sheet, row_index: int):
        self.__sheet = sheet
        self.__row_index = row_index

    def import_line(self) -> CustodyChildImportData:
        child_with_surnames_import_data: ChildWithSurnamesImportData = self.import_line_child_with_surnames_import_data()
        return CustodyChildImportData(child_with_surnames_import_data, self.import_line_days_attended())

    def import_line_child_with_surnames_import_data(self) -> ChildWithSurnamesImportData:
        child_import_data = self.import_line_child_import_data()
        return ChildWithSurnamesImportData(child_import_data, self.import_line_surnames())

    def import_line_child_import_data(self) -> ChildImportData:
        errors: list[LinesImporterErrorType] = []
        try:
            name: str = self.import_line_name()
            birth_year: int = self.import_line_birth_year()
            return ChildImportData(name, birth_year, LevelConstants.ID_LH4)
        except LinesImporterError as e:
            errors.append(e.error)
        if errors:
            raise LinesImporterErrors(errors)

    def import_line_name(self) -> str:
        name: str = FieldsFormatters.clean_string(self.__sheet.cell_value(rowx=self.__row_index, colx=self.NAME_COLUMN))
        if not name:
            raise LinesImporterError(LinesImporterErrorType.NAME_NOT_FOUND)
        return name

    def import_line_birth_year(self) -> int:
        birth_year: Optional[int] = FieldsFormatters.clean_integer(
            self.__sheet.cell_value(rowx=self.__row_index, colx=self.BIRTH_YEAR_COLUMN))
        if birth_year is None:
            raise LinesImporterError(LinesImporterErrorType.BIRTH_YEAR_NOT_FOUND)
        return birth_year

    def import_line_surnames(self) -> str:
        surnames: str = FieldsFormatters.clean_string(
            self.__sheet.cell_value(rowx=self.__row_index, colx=self.SURNAMES_COLUMN))
        if not surnames:
            raise LinesImporterError(LinesImporterErrorType.SURNAMES_NOT_FOUND)
        return surnames

    def import_line_days_attended(self) -> int:
        days_attended: Optional[int] = FieldsFormatters.clean_integer(
            self.__sheet.cell_value(rowx=self.__row_index, colx=self.DAYS_ATTENDED_COLUMN))
        if days_attended is None:
            raise LinesImporterError(LinesImporterErrorType.DAYS_ATTENDED_NOT_FOUND)
        return days_attended
