from enum import Enum


class RowsImporterErrorType(Enum):
    SURNAMES_NOT_FOUND = 'SURNAMES_NOT_FOUND'
    NAME_NOT_FOUND = 'NAME_NOT_FOUND'
    BIRTH_YEAR_NOT_FOUND = 'BIRTH_YEAR_NOT_FOUND'
    BIRTH_YEAR_NOT_INTEGER = 'BIRTH_YEAR_NOT_INTEGER'
    LEVEL_NOT_CORRECT = 'LEVEL_NOT_CORRECT'
    DAYS_ATTENDED_NOT_FOUND = 'DAYS_ATTENDED_NOT_FOUND'
    DAYS_ATTENDED_NOT_INTEGER = 'DAYS_ATTENDED_NOT_INTEGER'
    HOLDER_NAME_AND_SURNAMES_NOT_FOUND = 'HOLDER_NAME_AND_SURNAMES_NOT_FOUND'
    HOLDER_IBAN_NOT_FOUND = 'HOLDER_IBAN_NOT_FOUND'
    HOLDER_PHONE_NUMBER_NOT_FOUND = 'HOLDER_PHONE_NUMBER_NOT_FOUND'
    HOLDER_EMAIL_NOT_FOUND = 'HOLDER_EMAIL_NOT_FOUND'


class RowsImporterError(Exception):
    def __init__(self, error: RowsImporterErrorType):
        self.__error: RowsImporterErrorType = error

    @property
    def error(self) -> RowsImporterErrorType:
        return self.__error


class RowsImporterErrors(Exception):
    def __init__(self, errors: list[RowsImporterErrorType]):
        self.__errors: list[RowsImporterErrorType] = errors

    @property
    def errors(self) -> list[RowsImporterErrorType]:
        return self.__errors

class RowsImporterTotalErrors(Exception):
    def __init__(self, errors: list[RowsImporterErrorType]):
        self.__errors: list[RowsImporterErrorType] = errors

    @property
    def errors(self) -> list[RowsImporterErrorType]:
        return self.__errors
