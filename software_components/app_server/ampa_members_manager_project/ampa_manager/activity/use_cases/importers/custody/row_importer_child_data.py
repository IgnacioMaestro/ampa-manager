from typing import Optional

from xlrd.sheet import Sheet

from ampa_manager.academic_course.models.level_constants import LevelConstants
from ampa_manager.activity.use_cases.importers.excel_extracted_types.child_import_data import ChildImportData
from ampa_manager.activity.use_cases.importers.excel_extracted_types.child_with_surnames_import_data import \
    ChildWithSurnamesImportData
from ampa_manager.utils.fields_formatters import FieldsFormatters
from .custody_child_import_data import CustodyChildImportData
from .rows_importer_error import RowsImporterError, RowsImporterErrorType, RowsImporterErrors, \
    RowsImporterTotalErrors


class RowImporterChildData:
    NAME_COLUMN = 4
    SURNAMES_COLUMN = 5
    BIRTH_YEAR_COLUMN = 6
    LEVEL_COLUMN = 7
    DAYS_ATTENDED_COLUMN = 8

    def __init__(self, sheet: Sheet, row_index: int):
        self.__sheet = sheet
        self.__row_index = row_index

    def import_row(self) -> CustodyChildImportData:
        errors: list[RowsImporterErrorType] = []
        child_with_surnames_import_data: Optional[ChildWithSurnamesImportData] = None
        days_attended: Optional[int] = None
        try:
            child_with_surnames_import_data = self.import_row_child_with_surnames_import_data()
        except RowsImporterError as error:
            errors.append(error.error)
        except RowsImporterErrors as child_with_surnames_errors:
            errors.extend(child_with_surnames_errors.errors)
        try:
            days_attended = self.import_row_days_attended()
        except RowsImporterError as error:
            errors.append(error.error)
        if errors:
            raise RowsImporterTotalErrors(errors)
        return CustodyChildImportData(child_with_surnames_import_data, days_attended)

    def import_row_child_with_surnames_import_data(self) -> ChildWithSurnamesImportData:
        errors: list[RowsImporterErrorType] = []
        child_import_data: Optional[ChildImportData] = None
        surnames: Optional[str] = None
        try:
            child_import_data = self.import_row_child_import_data()
        except RowsImporterErrors as e:
            errors.extend(e.errors)
        try:
            surnames: str = self.import_row_surnames()
        except RowsImporterError as e:
            errors.append(e.error)
        if errors:
            raise RowsImporterErrors(errors)
        return ChildWithSurnamesImportData(child_import_data, surnames)

    def import_row_child_import_data(self) -> ChildImportData:
        errors: list[RowsImporterErrorType] = []
        try:
            name: str = self.import_row_name()
            birth_year: int = self.import_row_birth_year()
            level: Optional[LevelConstants] = self.import_row_level()
            return ChildImportData(name, birth_year, level)
        except RowsImporterError as e:
            errors.append(e.error)
        if errors:
            raise RowsImporterErrors(errors)

    def import_row_level(self) -> Optional[LevelConstants]:
        raw_level: str = FieldsFormatters.clean_string(
            self.__sheet.cell_value(rowx=self.__row_index, colx=self.LEVEL_COLUMN))
        if not raw_level:
            return None
        level: Optional[LevelConstants] = LevelConstants.obtain_level_from_str(raw_level)
        if not level:
            raise RowsImporterError(RowsImporterErrorType.CHILD_LEVEL_NOT_CORRECT)
        return level

    def import_row_name(self) -> str:
        name: str = FieldsFormatters.clean_string(self.__sheet.cell_value(rowx=self.__row_index, colx=self.NAME_COLUMN))
        if not name:
            raise RowsImporterError(RowsImporterErrorType.CHILD_NAME_NOT_FOUND)
        return name

    def import_row_birth_year(self) -> int:
        try:
            birth_year: Optional[int] = FieldsFormatters.clean_integer(
                self.__sheet.cell_value(rowx=self.__row_index, colx=self.BIRTH_YEAR_COLUMN))
        except ValueError:
            raise RowsImporterError(RowsImporterErrorType.CHILD_BIRTH_YEAR_NOT_INTEGER)
        return birth_year

    def import_row_surnames(self) -> str:
        surnames: str = FieldsFormatters.clean_string(
            self.__sheet.cell_value(rowx=self.__row_index, colx=self.SURNAMES_COLUMN))
        if not surnames:
            raise RowsImporterError(RowsImporterErrorType.CHILD_SURNAMES_NOT_FOUND)
        return surnames

    def import_row_days_attended(self) -> int:
        raw_days_attended = self.__sheet.cell_value(rowx=self.__row_index, colx=self.DAYS_ATTENDED_COLUMN)
        if raw_days_attended is None or raw_days_attended == '':
            raise RowsImporterError(RowsImporterErrorType.DAYS_ATTENDED_NOT_FOUND)
        try:
            days_attended: Optional[int] = FieldsFormatters.clean_integer(raw_days_attended)
        except ValueError:
            raise RowsImporterError(RowsImporterErrorType.DAYS_ATTENDED_NOT_INTEGER)
        return days_attended
