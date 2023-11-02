from typing import Optional

from xlrd.sheet import Sheet

from ampa_manager.utils.fields_formatters import FieldsFormatters
from .lines_importer_error import LinesImporterErrorType, LinesImporterError, LinesImporterErrors
from ..excel_extracted_types.holder_import_data import HolderImportData
from ..excel_extracted_types.parent_import_data import ParentImportData


class LineImporterHolderData:
    HOLDER_NAME_AND_SURNAMES_COLUMN = 0
    PHONE_NUMBER_COLUMN = 1
    EMAIL_COLUMN = 2
    IBAN_COLUMN = 3

    def __init__(self, sheet: Sheet, row_index: int):
        self.__sheet = sheet
        self.__row_index = row_index

    def import_line(self) -> Optional[HolderImportData]:
        holder_name_and_surnames: str = self.obtain_holder_name_and_surnames()
        phone_number: str = self.obtain_phone_number()
        email: str = self.obtain_email()
        iban: str = self.obtain_iban()
        if not holder_name_and_surnames and not phone_number and not email and not iban:
            return None
        parent_import_data: ParentImportData = self.import_line_parent_import_data()
        try:
            iban = self.import_line_iban()
        except LinesImporterError as error:
            raise LinesImporterErrors([error.error])
        return HolderImportData(parent_import_data, iban)

    def import_line_parent_import_data(self) -> ParentImportData:
        errors: list[LinesImporterErrorType] = []
        try:
            holder_name_and_surnames: str = self.import_line_holder_name_and_surnames()
            phone_number: str = self.import_line_phone_number()
            email: str = self.import_line_email()
            return ParentImportData(holder_name_and_surnames, phone_number, email)
        except LinesImporterError as e:
            errors.append(e.error)
        if errors:
            raise LinesImporterErrors(errors)

    def import_line_holder_name_and_surnames(self) -> str:
        holder_name_and_surnames: str = self.obtain_cleaned_holder_name_and_surnames()
        if not holder_name_and_surnames:
            raise LinesImporterError(LinesImporterErrorType.HOLDER_NAME_AND_SURNAMES_NOT_FOUND)
        return holder_name_and_surnames

    def obtain_cleaned_holder_name_and_surnames(self) -> Optional[str]:
        return FieldsFormatters.clean_string(self.obtain_holder_name_and_surnames())

    def obtain_holder_name_and_surnames(self):
        return self.__sheet.cell_value(rowx=self.__row_index, colx=self.HOLDER_NAME_AND_SURNAMES_COLUMN)

    def import_line_phone_number(self) -> str:
        phone_number: str = self.obtain_cleaned_phone_number()
        if not phone_number:
            raise LinesImporterError(LinesImporterErrorType.HOLDER_PHONE_NUMBER_NOT_FOUND)
        return phone_number

    def obtain_cleaned_phone_number(self) -> Optional[str]:
        return FieldsFormatters.clean_phone(self.obtain_phone_number())

    def obtain_phone_number(self):
        return self.__sheet.cell_value(rowx=self.__row_index, colx=self.PHONE_NUMBER_COLUMN)

    def import_line_email(self) -> str:
        email: str = self.obtain_cleaned_email()
        if not email:
            raise LinesImporterError(LinesImporterErrorType.HOLDER_EMAIL_NOT_FOUND)
        return email

    def obtain_cleaned_email(self) -> Optional[str]:
        return FieldsFormatters.clean_string(self.obtain_email())

    def obtain_email(self):
        return self.__sheet.cell_value(rowx=self.__row_index, colx=self.EMAIL_COLUMN)

    def import_line_iban(self) -> str:
        iban: str = self.obtain_cleaned_iban()
        if not iban:
            raise LinesImporterError(LinesImporterErrorType.HOLDER_IBAN_NOT_FOUND)
        return iban

    def obtain_cleaned_iban(self) -> Optional[str]:
        return FieldsFormatters.clean_string(self.obtain_iban())

    def obtain_iban(self):
        return self.__sheet.cell_value(rowx=self.__row_index, colx=self.IBAN_COLUMN)
