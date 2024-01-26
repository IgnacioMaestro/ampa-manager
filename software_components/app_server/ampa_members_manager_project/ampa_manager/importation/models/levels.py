from __future__ import annotations

from typing import Optional

from django.db import models

from ampa_manager.academic_course.models.level_constants import LevelConstants


class Levels(models.IntegerChoices):
    HH2 = 1, LevelConstants.ID_HH2
    HH3 = 2, LevelConstants.ID_HH3
    HH4 = 3, LevelConstants.ID_HH4
    HH5 = 4, LevelConstants.ID_HH5
    LH1 = 5, LevelConstants.ID_LH1
    LH2 = 6, LevelConstants.ID_LH2
    LH3 = 7, LevelConstants.ID_LH3
    LH4 = 8, LevelConstants.ID_LH4
    LH5 = 9, LevelConstants.ID_LH5
    LH6 = 10, LevelConstants.ID_LH6

    @classmethod
    def obtain_from_level_constant(cls, level_constant: str) -> Optional[int]:
        for value, name in cls.choices:
            if name == level_constant:
                return value
        return None


