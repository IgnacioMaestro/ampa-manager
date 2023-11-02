from typing import Optional

from django.core.exceptions import ValidationError
from localflavor.generic.validators import IBANValidator

from ampa_manager.academic_course.models.level import Level
from ampa_manager.utils.string_utils import StringUtils


class FieldsFormattersDjango:
    @staticmethod
    def clean_iban(value: str) -> Optional[str]:
        if value:
            iban = StringUtils.remove_all_spaces(str(value))
            try:
                validator = IBANValidator()
                validator(iban)
                return iban
            except ValidationError:
                raise ValidationError('Wrong IBAN')
        return None

    @staticmethod
    def clean_level(value: str) -> Optional[str]:
        if value:
            level = StringUtils.uppercase(
                StringUtils.remove_duplicated_spaces(StringUtils.remove_strip_spaces(str(value))))
            if Level.is_valid(level):
                return level
            else:
                raise ValidationError('Wrong level')
        return None
