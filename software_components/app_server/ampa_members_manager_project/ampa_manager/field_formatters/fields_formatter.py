from datetime import datetime
from typing import Optional

from ampa_manager.academic_course.models.level import Level

from ampa_manager.utils.string_utils import StringUtils


class FieldsFormatter:
    @classmethod
    def clean_name(cls, value: str) -> Optional[str]:
        if value:
            return StringUtils.capitalize(StringUtils.fix_accents(StringUtils.remove_duplicated_spaces(StringUtils.remove_strip_spaces(value))))
        return None

    @classmethod
    def clean_string(cls, value: str) -> Optional[str]:
        if value:
            return StringUtils.remove_duplicated_spaces(StringUtils.remove_strip_spaces(value))
        return None

    @classmethod
    def clean_email(cls, value: str) -> Optional[str]:
        if value:
            return StringUtils.lowercase(StringUtils.remove_all_spaces(StringUtils.remove_accents(value)))
        return None

    @classmethod
    def clean_phone(cls, value: str) -> Optional[str]:
        if value:
            value = StringUtils.remove_all_spaces(value)
            if value not in ['0', '0.0', '0,0']:
                if not value.startswith('+34'):
                    value = f'+34{value}'
                if value.endswith('.0'):
                    value = value[:-2]
                if value.endswith(',0'):
                    value = value[:-2]
                return value
        return ''

    @classmethod
    def clean_iban(cls, value: str) -> Optional[str]:
        if value:
            return StringUtils.remove_all_spaces(value)
        return None

    @classmethod
    def clean_date(cls, value: str, date_format: str = '%d/%m/%y') -> Optional[datetime]:
        if value:
            return datetime.strptime(StringUtils.remove_all_spaces(value), date_format)
        return None

    @classmethod
    def clean_integer(cls, value: str) -> Optional[int]:
        if value:
            return int(float(StringUtils.remove_all_spaces(value)))
        return None

    @classmethod
    def clean_float(cls, value: str) -> Optional[float]:
        if value:
            return int(StringUtils.remove_all_spaces(value))
        return None
