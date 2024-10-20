from typing import Optional

from ampa_manager.utils.string_utils import StringUtils


class Column:
    def __init__(self, raw_value, formatted_value, error=None):
        self.raw_value: str = raw_value
        self.formatted_value = formatted_value
        self.error: Optional[str] = error

    def __str__(self):
        return f'{self.raw_value}, {self.formatted_value}, {self.error}'

    @property
    def modified(self):
        return self.raw_value and not StringUtils.strings_are_equal(
            self.raw_value, self.formatted_value, ignore_case=True, ignore_spaces=True, ignore_zero_decimals=True,
            ignore_spain_phone_prefix=True)

    @property
    def is_empty(self):
        return self.raw_value is None or self.raw_value == ''
