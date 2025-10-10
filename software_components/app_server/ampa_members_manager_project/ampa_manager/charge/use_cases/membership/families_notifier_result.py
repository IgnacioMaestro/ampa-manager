from typing import Optional

from ampa_manager.family.models.family import Family


class FamiliesNotifierResult:
    def __init__(self, notified_families_ids: list[int], error_family: Optional[Family] = None, error: Optional[str] = None):
        self.notified_families_ids = notified_families_ids
        self.error_family = error_family
        self.error = error
