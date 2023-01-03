import re
from typing import Optional

from unidecode import unidecode

from ampa_manager.utils.surnames import SURNAMES


class StringUtils:

    @classmethod
    def compare_ignoring_everything(cls, value1: str, value2: str):
        if value1 and value2:
            return cls.normalize(value1) == cls.normalize(value2)
        return False

    @classmethod
    def normalize(cls, value: str):
        if value:
            return cls.lowercase(cls.remove_strip_spaces(cls.remove_duplicated_spaces(cls.remove_accents(value))))
        return None

    @classmethod
    def contains_any_word(cls, value1: str, value2: str):
        if value1 and value2:
            for word in cls.normalize(value1).split(' '):
                pattern = rf'\b{word}\b'
                if re.search(pattern, cls.normalize(value2)):
                    return True
        return False

    @classmethod
    def remove_accents(cls, value: str) -> Optional[str]:
        if value:
            return unidecode(value)
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
    def remove_duplicated_spaces(cls, value: str) -> Optional[str]:
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
    def parse_bool(cls, value: str) -> bool:
        if value:
            return StringUtils.remove_accents(value.strip().lower()) in ["si", "bai", "yes", "1", "true"]
        else:
            return False

    @classmethod
    def lowercase(cls, value: str) -> Optional[str]:
        if value:
            return value.casefold()
        else:
            return None
