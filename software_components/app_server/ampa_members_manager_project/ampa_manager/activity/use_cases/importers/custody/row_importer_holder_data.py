from typing import Optional

from xlrd.sheet import Sheet

from ampa_manager.utils.fields_formatters import FieldsFormatters
from .rows_importer_error import RowsImporterErrorType, RowsImporterError, RowsImporterErrors
from ampa_manager.activity.use_cases.importers.excel_extracted_types.holder_import_data import HolderImportData
from ampa_manager.activity.use_cases.importers.excel_extracted_types.parent_import_data import ParentImportData


class RowImporterHolderData:
    HOLDER_NAME_AND_SURNAMES_COLUMN = 0
    PHONE_NUMBER_COLUMN = 1
    EMAIL_COLUMN = 2
    IBAN_COLUMN = 3

    def __init__(self, sheet: Sheet, row_index: int):
        self.__sheet = sheet
        self.__row_index = row_index

    def import_row(self) -> Optional[HolderImportData]:
        if self.__are_all_fields_empty():
            return None
        parent_import_data, iban = self.__obtain_parent_import_data_and_iban()
        return HolderImportData(parent_import_data, iban)

    def __obtain_parent_import_data_and_iban(self) -> tuple[ParentImportData, str]:
        errors: list[RowsImporterErrorType] = []
        parent_import_data: Optional[ParentImportData] = None
        iban: Optional[str] = None
        try:
            parent_import_data: ParentImportData = self.__import_row_parent_import_data()
        except RowsImporterErrors as parent_errors:
            errors.extend(parent_errors.errors)
        try:
            iban = self.__import_row_iban()
        except RowsImporterError as error:
            errors.append(error.error)
        if errors:
            raise RowsImporterErrors(errors)
        return parent_import_data, iban

    def __are_all_fields_empty(self):
        holder_name_and_surnames: str = self.__obtain_holder_name_and_surnames()
        phone_number: str = self.__obtain_phone_number()
        email: str = self.__obtain_email()
        iban: str = self.__obtain_iban()
        return not holder_name_and_surnames and not phone_number and not email and not iban

    def __import_row_parent_import_data(self) -> ParentImportData:
        errors: list[RowsImporterErrorType] = []
        try:
            holder_name_and_surnames: str = self.__import_row_holder_name_and_surnames()
            phone_number: str = self.__import_row_phone_number()
            email: str = self.__import_row_email()
            return ParentImportData(holder_name_and_surnames, phone_number, email)
        except RowsImporterError as e:
            errors.append(e.error)
        if errors:
            raise RowsImporterErrors(errors)

    def __import_row_holder_name_and_surnames(self) -> str:
        holder_name_and_surnames: str = self.__obtain_cleaned_holder_name_and_surnames()
        if not holder_name_and_surnames:
            raise RowsImporterError(RowsImporterErrorType.HOLDER_NAME_AND_SURNAMES_NOT_FOUND)
        return holder_name_and_surnames

    def __obtain_cleaned_holder_name_and_surnames(self) -> Optional[str]:
        return FieldsFormatters.clean_string(self.__obtain_holder_name_and_surnames())

    def __obtain_holder_name_and_surnames(self):
        return self.__sheet.cell_value(rowx=self.__row_index, colx=self.HOLDER_NAME_AND_SURNAMES_COLUMN)

    def __import_row_phone_number(self) -> str:
        phone_number: str = self.__obtain_cleaned_phone_number()
        if not phone_number:
            raise RowsImporterError(RowsImporterErrorType.HOLDER_PHONE_NUMBER_NOT_FOUND)
        return phone_number

    def __obtain_cleaned_phone_number(self) -> Optional[str]:
        return FieldsFormatters.clean_phone(self.__obtain_phone_number())

    def __obtain_phone_number(self):
        return self.__sheet.cell_value(rowx=self.__row_index, colx=self.PHONE_NUMBER_COLUMN)

    def __import_row_email(self) -> str:
        email: str = self.__obtain_cleaned_email()
        if not email:
            raise RowsImporterError(RowsImporterErrorType.HOLDER_EMAIL_NOT_FOUND)
        return email

    def __obtain_cleaned_email(self) -> Optional[str]:
        return FieldsFormatters.clean_string(self.__obtain_email())

    def __obtain_email(self):
        return self.__sheet.cell_value(rowx=self.__row_index, colx=self.EMAIL_COLUMN)

    def __import_row_iban(self) -> str:
        iban: str = self.__obtain_cleaned_iban()
        if not iban:
            raise RowsImporterError(RowsImporterErrorType.HOLDER_IBAN_NOT_FOUND)
        return iban

    def __obtain_cleaned_iban(self) -> Optional[str]:
        return FieldsFormatters.clean_string(self.__obtain_iban())

    def __obtain_iban(self):
        return self.__sheet.cell_value(rowx=self.__row_index, colx=self.IBAN_COLUMN)
