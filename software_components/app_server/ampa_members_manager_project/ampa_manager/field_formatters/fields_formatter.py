import re
from datetime import datetime
from typing import Optional

from ampa_manager.academic_course.models.level import Level
from ampa_manager.field_formatters.surnames import SURNAMES
from unidecode import unidecode


class FieldsFormatter:
    @classmethod
    def clean_name(cls, value: str) -> Optional[str]:
        if value:
            return cls.capitalize(cls.fix_accents(cls.remove_duplicate_spaces(cls.remove_strip_spaces(value))))
        return None

    @classmethod
    def clean_string(cls, value: str) -> Optional[str]:
        if value:
            return cls.remove_duplicate_spaces(cls.remove_strip_spaces(value))
        return None

    @classmethod
    def clean_email(cls, value: str) -> Optional[str]:
        if value:
            return cls.remove_all_spaces(cls.remove_accents(value.lower()))
        return None

    @classmethod
    def clean_phone(cls, value: str) -> Optional[str]:
        if value:
            value = cls.remove_all_spaces(value)
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
            return cls.remove_all_spaces(value)
        return None

    @classmethod
    def clean_date(cls, value: str, date_format: str = '%d/%m/%y') -> Optional[datetime]:
        if value:
            return datetime.strptime(cls.remove_all_spaces(value), date_format)
        return None

    @classmethod
    def clean_integer(cls, value: str) -> Optional[int]:
        if value:
            return int(float(cls.remove_all_spaces(value)))
        return None

    @classmethod
    def clean_float(cls, value: str) -> Optional[float]:
        if value:
            return int(cls.remove_all_spaces(value))
        return None

    @classmethod
    def capitalize(cls, value: str) -> Optional[str]:
        if value:
            return value.title()
        return None

    @classmethod
    def remove_strip_spaces(cls, value: str) -> Optional[str]:
        if value:
            return value.strip()
        return None

    @classmethod
    def remove_duplicate_spaces(cls, value: str) -> Optional[str]:
        if value:
            return re.sub(' +', ' ', value)
        return None

    @classmethod
    def remove_all_spaces(cls, value: str) -> Optional[str]:
        if value is not None:
            return value.replace(' ', '')
        return None

    @classmethod
    def fix_accents(cls, value) -> Optional[str]:
        if value:
            for wrong, right in SURNAMES.items():
                pattern = rf'\b{wrong}\b'
                if re.search(pattern, value, re.IGNORECASE):
                    value = re.sub(pattern, right, value)
            return value
        return None

    @classmethod
    def remove_accents(cls, value: str) -> Optional[str]:
        if value:
            return unidecode(value)
        return None

    @classmethod
    def parse_bool(cls, value: str) -> bool:
        if value:
            return cls.remove_accents(value.strip().lower()) in ["si", "bai", "yes", "1", "true"]
        else:
            return False

    @classmethod
    def parse_level(cls, value) -> Optional[str]:
        if value:
            value = value.strip().lower()
            for level_id, level_name in Level.LEVELS_NAMES.items():
                if level_name.strip().lower() in value:
                    return level_id
        return None
