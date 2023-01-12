from enum import Enum


class ProcessingState(Enum):
    NOT_PROCESSED = 0
    CREATED = 1
    UPDATED = 2
    PARENT_ADDED_TO_FAMILY = 3
    BANK_ACCOUNT_SET_AS_DEFAULT = 4
    NOT_MODIFIED = 5
    ERROR = 6