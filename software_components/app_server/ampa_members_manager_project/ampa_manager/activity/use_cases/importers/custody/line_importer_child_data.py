from typing import Optional

from xlrd.sheet import Sheet

from ampa_manager.academic_course.models.level_constants import LevelConstants
from ampa_manager.activity.use_cases.importers.excel_extracted_types.child_import_data import ChildImportData
from ampa_manager.activity.use_cases.importers.excel_extracted_types.child_with_surnames_import_data import \
    ChildWithSurnamesImportData
from ampa_manager.utils.fields_formatters import FieldsFormatters
from .custody_child_import_data import CustodyChildImportData
from .lines_importer_error import LinesImporterError, LinesImporterErrorType, LinesImporterErrors, \
    LinesImporterTotalErrors


class LineImporterChildData:
    NAME_COLUMN = 4
    SURNAMES_COLUMN = 5
    BIRTH_YEAR_COLUMN = 6
    LEVEL_COLUMN = 7
    DAYS_ATTENDED_COLUMN = 8

    def __init__(self, sheet: Sheet, row_index: int):
        self.__sheet = sheet
        self.__row_index = row_index

    def import_line(self) -> CustodyChildImportData:
        errors: list[LinesImporterErrorType] = []
        child_with_surnames_import_data: Optional[ChildWithSurnamesImportData] = None
        days_attended: Optional[int] = None
        try:
            child_with_surnames_import_data = self.import_line_child_with_surnames_import_data()
        except LinesImporterError as error:
            errors.append(error.error)
        except LinesImporterErrors as child_with_surnames_errors:
            errors.extend(child_with_surnames_errors.errors)
        try:
            days_attended = self.import_line_days_attended()
        except LinesImporterError as error:
            errors.append(error.error)
        if errors:
            raise LinesImporterTotalErrors(errors)
        return CustodyChildImportData(child_with_surnames_import_data, days_attended)

    def import_line_child_with_surnames_import_data(self) -> ChildWithSurnamesImportData:
        errors: list[LinesImporterErrorType] = []
        child_import_data: Optional[ChildImportData] = None
        surnames: Optional[str] = None
        try:
            child_import_data = self.import_line_child_import_data()
        except LinesImporterErrors as e:
            errors.extend(e.errors)
        try:
            surnames: str = self.import_line_surnames()
        except LinesImporterError as e:
            errors.append(e.error)
        if errors:
            raise LinesImporterErrors(errors)
        return ChildWithSurnamesImportData(child_import_data, surnames)

    def import_line_child_import_data(self) -> ChildImportData:
        errors: list[LinesImporterErrorType] = []
        try:
            name: str = self.import_line_name()
            birth_year: int = self.import_line_birth_year()
            level: Optional[LevelConstants] = self.import_line_level()
            return ChildImportData(name, birth_year, level)
        except LinesImporterError as e:
            errors.append(e.error)
        if errors:
            raise LinesImporterErrors(errors)

    def import_line_level(self) -> Optional[LevelConstants]:
        raw_level: str = FieldsFormatters.clean_string(
            self.__sheet.cell_value(rowx=self.__row_index, colx=self.LEVEL_COLUMN))
        if not raw_level:
            return None
        level: Optional[LevelConstants] = LevelConstants.obtain_level_from_str(raw_level)
        if not level:
            raise LinesImporterError(LinesImporterErrorType.LEVEL_NOT_CORRECT)
        return level

    def import_line_name(self) -> str:
        name: str = FieldsFormatters.clean_string(self.__sheet.cell_value(rowx=self.__row_index, colx=self.NAME_COLUMN))
        if not name:
            raise LinesImporterError(LinesImporterErrorType.NAME_NOT_FOUND)
        return name

    def import_line_birth_year(self) -> int:
        try:
            birth_year: Optional[int] = FieldsFormatters.clean_integer(
                self.__sheet.cell_value(rowx=self.__row_index, colx=self.BIRTH_YEAR_COLUMN))
        except ValueError:
            raise LinesImporterError(LinesImporterErrorType.BIRTH_YEAR_NOT_INTEGER)
        return birth_year

    def import_line_surnames(self) -> str:
        surnames: str = FieldsFormatters.clean_string(
            self.__sheet.cell_value(rowx=self.__row_index, colx=self.SURNAMES_COLUMN))
        if not surnames:
            raise LinesImporterError(LinesImporterErrorType.SURNAMES_NOT_FOUND)
        return surnames

    def import_line_days_attended(self) -> int:
        raw_days_attended = self.__sheet.cell_value(rowx=self.__row_index, colx=self.DAYS_ATTENDED_COLUMN)
        if raw_days_attended is None or raw_days_attended == '':
            raise LinesImporterError(LinesImporterErrorType.DAYS_ATTENDED_NOT_FOUND)
        try:
            days_attended: Optional[int] = FieldsFormatters.clean_integer(raw_days_attended)
        except ValueError:
            raise LinesImporterError(LinesImporterErrorType.DAYS_ATTENDED_NOT_INTEGER)
        return days_attended
