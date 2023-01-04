import re
from typing import Optional

from unidecode import unidecode

from ampa_manager.utils.surnames import SURNAMES


class StringUtils:

    @staticmethod
    def compare_ignoring_everything(value1: str, value2: str) -> bool:
        if value1 and value2:
            return StringUtils.normalize(value1) == StringUtils.normalize(value2)
        return False

    @staticmethod
    def normalize(value: str) -> Optional[str]:
        if value:
            return StringUtils.lowercase(StringUtils.remove_strip_spaces(StringUtils.remove_duplicated_spaces(StringUtils.remove_accents(value))))
        return None

    @staticmethod
    def contains_any_word(value1: str, value2: str) -> bool:
        if value1 and value2:
            for word in StringUtils.normalize(value1).split(' '):
                pattern = rf'\b{word}\b'
                if re.search(pattern, StringUtils.normalize(value2)):
                    return True
        return False

    @staticmethod
    def remove_accents(value: str) -> Optional[str]:
        if value:
            return unidecode(value)
        return None

    @staticmethod
    def capitalize(value: str) -> Optional[str]:
        if value:
            return value.title()
        return None

    @staticmethod
    def remove_strip_spaces(value: str) -> Optional[str]:
        if value:
            return value.strip()
        return None

    @staticmethod
    def remove_duplicated_spaces(value: str) -> Optional[str]:
        if value:
            return re.sub(' +', ' ', value)
        return None

    @staticmethod
    def remove_all_spaces(value: str) -> Optional[str]:
        if value is not None:
            return value.replace(' ', '')
        return None

    @staticmethod
    def fix_accents(value: str) -> Optional[str]:
        if value:
            for wrong, right in SURNAMES.items():
                pattern = rf'\b{wrong}\b'
                if re.search(pattern, value, re.IGNORECASE):
                    value = re.sub(pattern, right, value)
            return value
        return None

    @staticmethod
    def parse_bool(value: str) -> bool:
        if value:
            return StringUtils.remove_accents(value.strip().lower()) in ["si", "bai", "yes", "1", "true"]
        else:
            return False

    @staticmethod
    def lowercase(value: str) -> Optional[str]:
        if value:
            return value.casefold()
        else:
            return None
