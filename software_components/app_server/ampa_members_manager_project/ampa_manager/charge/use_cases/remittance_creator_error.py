from enum import Enum


class RemittanceCreatorError(Enum):
    NO_FAMILIES = 0
    BIC_ERROR = 1
    NO_FEE_FOR_COURSE = 2
