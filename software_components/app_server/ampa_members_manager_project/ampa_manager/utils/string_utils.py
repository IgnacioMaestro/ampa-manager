import re
from typing import Optional

from unidecode import unidecode

from ampa_manager.utils.surnames import SURNAMES


class StringUtils:
    SURNAMES_IGNORE_WORDS = ['de']

    @staticmethod
    def subtract_words(text: str, words_to_subtract: str):
        words = words_to_subtract.split()
        text_words = text.split()
        filtered_words = [word for word in text_words if word not in words]
        return ' '.join(filtered_words)

    @staticmethod
    def compare_ignoring_everything(value1: str, value2: str) -> bool:
        if value1 and value2:
            return StringUtils.normalize(value1) == StringUtils.normalize(value2)
        return False

    @staticmethod
    def normalize(value: str) -> Optional[str]:
        if value:
            return StringUtils.remove_strip_spaces(
                StringUtils.remove_duplicated_spaces(
                    StringUtils.remove_basque_characters(
                        StringUtils.lowercase(
                            StringUtils.remove_special_chars(
                                StringUtils.remove_accents(value))))))
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
    def remove_basque_characters(value: str) -> Optional[str]:
        if value:
            new_value = value
            for character in ['tx', 'tz', 'ts']:
                new_value = new_value.replace(character, 'ch')
            for character in ['tt']:
                new_value = new_value.replace(character, 't')
            for character in ['dd']:
                new_value = new_value.replace(character, 'd')
            for character in ['gu']:
                new_value = new_value.replace(character, 'g')
            for character in ['k']:
                new_value = new_value.replace(character, 'c')
            return new_value
        return None

    @staticmethod
    def remove_all_spaces(value: str) -> Optional[str]:
        if value is not None:
            return value.replace(' ', '')
        return None

    @staticmethod
    def remove_new_lines(value: str) -> Optional[str]:
        if value is not None:
            return value.replace('\n', '').replace('\r', '')
        return None

    @staticmethod
    def remove_tabs(value: str) -> Optional[str]:
        if value is not None:
            return value.replace('\t', '')
        return None

    @staticmethod
    def remove_special_chars(value: str) -> Optional[str]:
        if value is not None:
            special_chars = [
                '!', '¡', '¿', '?', '"', '\'', '.', ',', ':', ';', '-', '_', '#', '~', '@', '|', ',', '}', '[', ']',
                '(', ')', '/', '\\', '&', '%', '$', '·', '=', '\n', '\r', '\t'
            ]
            return value.translate({ord(x): '' for x in special_chars})
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
            return StringUtils.remove_accents(
                StringUtils.lowercase(
                    StringUtils.remove_strip_spaces(value))) in ["si", "bai", "yes", "1", "true"]
        else:
            return False

    @staticmethod
    def lowercase(value: str) -> Optional[str]:
        if value:
            return value.casefold()
        else:
            return None

    @staticmethod
    def uppercase(value: str) -> Optional[str]:
        if value:
            return value.upper()
        else:
            return None

    @staticmethod
    def get_excel_column_letter(column_index: int):
        letters = {
            0: 'A',
            1: 'B',
            2: 'C',
            3: 'D',
            4: 'E',
            5: 'F',
            6: 'G',
            7: 'H',
            8: 'I',
            9: 'J',
            10: 'K',
            11: 'L',
            12: 'M',
            13: 'N',
            14: 'O',
            15: 'P',
            16: 'Q',
            17: 'R',
            18: 'S',
            19: 'T',
            20: 'U',
            21: 'V',
            22: 'W',
            23: 'X',
            24: 'Y',
            25: 'Z',
            26: 'AA',
            27: 'AB',
            28: 'AC',
            29: 'AD',
            30: 'AE',
            31: 'AF',
            32: 'AG',
            33: 'AH',
            34: 'AI',
            35: 'AJ',
            36: 'AK',
            37: 'AL',
            38: 'AM',
            39: 'AN',
            40: 'AO',
        }
        return letters.get(column_index, '-')
