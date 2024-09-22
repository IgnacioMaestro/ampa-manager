from typing import List


class FieldsChanges:

    def __init__(self, values_before: List, values_after: List, not_reset_fields: List):
        self.values_before = values_before
        self.values_after = values_after
        self.not_reset_fields = not_reset_fields

    @property
    def any_not_reset_fields(self):
        return len(self.not_reset_fields) > 0
