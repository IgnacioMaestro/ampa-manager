from typing import Optional


class FamiliesNotifierResult:
    def __init__(self, notified_families_ids: list[int], error_family_id: Optional[int] = None, error: Optional[str] = None):
        self.notified_families_ids = notified_families_ids
        self.error_family_id = error_family_id
        self.error = error
