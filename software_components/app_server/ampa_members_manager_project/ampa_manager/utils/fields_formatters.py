import re
from datetime import datetime
from typing import Optional

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from localflavor.generic.validators import IBANValidator

from ampa_manager.academic_course.models.level import Level
from ampa_manager.utils.string_utils import StringUtils


class FieldsFormatters:

    @staticmethod
    def format_name(value: str) -> Optional[str]:
        if value:
            return StringUtils.capitalize(
                StringUtils.fix_accents(
                    StringUtils.remove_duplicated_spaces(
                        StringUtils.remove_strip_spaces(str(value)))))
        return None

    @staticmethod
    def format_string(value: str) -> Optional[str]:
        if value:
            return StringUtils.remove_duplicated_spaces(StringUtils.remove_strip_spaces(str(value)))
        return None

    @staticmethod
    def format_email(value: str) -> Optional[str]:
        if value:
            value = StringUtils.lowercase(StringUtils.remove_all_spaces(StringUtils.remove_accents(str(value))))
            if FieldsFormatters.is_a_valid_email(value):
                return value
            else:
                raise ValidationError(_('Wrong email') + f' ({value})')
        return None

    @staticmethod
    def format_phone(value: str) -> Optional[str]:
        if value:
            value = StringUtils.remove_all_spaces(str(value))
            if value not in ['0', '0.0', '0,0']:
                if not value.startswith('+34'):
                    value = f'+34{value}'
                if value.endswith('.0'):
                    value = value[:-2]
                if value.endswith(',0'):
                    value = value[:-2]
                return value
        return None

    @staticmethod
    def format_date(value: str, date_format: str = '%d/%m/%y') -> Optional[datetime]:
        if value:
            return datetime.strptime(StringUtils.remove_all_spaces(str(value)), date_format)
        return None

    @staticmethod
    def format_integer(value: str) -> Optional[int]:
        if value is not None and value != '':
            return int(float(StringUtils.remove_all_spaces(str(value))))
        return None

    @staticmethod
    def format_float(value: str) -> Optional[float]:
        if value is not None and value != '':
            return float(StringUtils.remove_all_spaces(str(value)))
        return None

    @staticmethod
    def format_iban(value: str) -> Optional[str]:
        if value:
            iban = StringUtils.remove_all_spaces(str(value))
            try:
                validator = IBANValidator()
                validator(iban)
                return iban
            except ValidationError:
                raise ValidationError(_('Wrong IBAN') + f' ({value})')
        return None

    @staticmethod
    def format_level(value: str) -> Optional[str]:
        if value:
            level = StringUtils.uppercase(StringUtils.remove_all_spaces((str(value))))
            if Level.is_valid(level):
                return level
            else:
                raise ValidationError(_('Wrong level') + f' ({value})')
        return None

    @staticmethod
    def is_a_valid_email(email) -> bool:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
