from enum import Enum


class RemittanceCreatorError(Enum):
    NO_FAMILIES = 0
    BIC_ERROR = 1
