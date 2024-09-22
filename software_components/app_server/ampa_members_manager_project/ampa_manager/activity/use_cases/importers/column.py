from typing import Optional


class Column:
    def __init__(self, raw_value, formatted_value, error=None):
        self.value: str = raw_value
        self.formatted_value = formatted_value
        self.error: Optional[str] = error
