from enum import Enum


class LinesImporterErrorType(Enum):
    SURNAMES_NOT_FOUND = 'SURNAMES_NOT_FOUND'
    NAME_NOT_FOUND = 'NAME_NOT_FOUND'
    BIRTH_YEAR_NOT_FOUND = 'BIRTH_YEAR_NOT_FOUND'
    LEVEL_NOT_FOUND = 'LEVEL_NOT_FOUND'
    DAYS_ATTENDED_NOT_FOUND = 'DAYS_ATTENDED_NOT_FOUND'
    DAYS_ATTENDED_NOT_INTEGER = 'DAYS_ATTENDED_NOT_INTEGER'
    HOLDER_NAME_AND_SURNAMES_NOT_FOUND = 'HOLDER_NAME_AND_SURNAMES_NOT_FOUND'
    HOLDER_IBAN_NOT_FOUND = 'HOLDER_IBAN_NOT_FOUND'
    HOLDER_PHONE_NUMBER_NOT_FOUND = 'HOLDER_PHONE_NUMBER_NOT_FOUND'
    HOLDER_EMAIL_NOT_FOUND = 'HOLDER_EMAIL_NOT_FOUND'


class LinesImporterError(Exception):
    def __init__(self, error: LinesImporterErrorType):
        self.__error: LinesImporterErrorType = error

    @property
    def error(self) -> LinesImporterErrorType:
        return self.__error


class LinesImporterErrors(Exception):
    def __init__(self, errors: list[LinesImporterErrorType]):
        self.__errors: list[LinesImporterErrorType] = errors

    @property
    def errors(self) -> list[LinesImporterErrorType]:
        return self.__errors

class LinesImporterTotalErrors(Exception):
    def __init__(self, errors: list[LinesImporterErrorType]):
        self.__errors: list[LinesImporterErrorType] = errors

    @property
    def errors(self) -> list[LinesImporterErrorType]:
        return self.__errors
