from typing import Optional

from ampa_manager.academic_course.models.level_constants import LevelConstants


class ChildImportData:
    def __init__(self, name: str, birth_year: Optional[int] = None, level: Optional[LevelConstants] = None):
        self.__name: str = name
        self.__birth_year: Optional[int] = birth_year
        self.__level: Optional[LevelConstants] = level

    @property
    def name(self) -> str:
        return self.__name

    @property
    def birth_year(self) -> Optional[int]:
        return self.__birth_year

    @property
    def level(self) -> Optional[LevelConstants]:
        return self.__level
