from typing import Optional

from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.academic_course.models.level_constants import LevelConstants


class Level:
    AGE_HH2 = 2
    AGE_HH3 = 3
    AGE_HH4 = 4
    AGE_HH5 = 5
    AGE_LH1 = 6
    AGE_LH2 = 7
    AGE_LH3 = 8
    AGE_LH4 = 9
    AGE_LH5 = 10
    AGE_LH6 = 11

    NAME_HH2 = _('HH2')
    NAME_HH3 = _('HH3')
    NAME_HH4 = _('HH4')
    NAME_HH5 = _('HH5')
    NAME_LH1 = _('LH1')
    NAME_LH2 = _('LH2')
    NAME_LH3 = _('LH3')
    NAME_LH4 = _('LH4')
    NAME_LH5 = _('LH5')
    NAME_LH6 = _('LH6')

    LEVEL_IDS_BY_AGE = {
        AGE_HH2: LevelConstants.ID_HH2,
        AGE_HH3: LevelConstants.ID_HH3,
        AGE_HH4: LevelConstants.ID_HH4,
        AGE_HH5: LevelConstants.ID_HH5,
        AGE_LH1: LevelConstants.ID_LH1,
        AGE_LH2: LevelConstants.ID_LH2,
        AGE_LH3: LevelConstants.ID_LH3,
        AGE_LH4: LevelConstants.ID_LH4,
        AGE_LH5: LevelConstants.ID_LH5,
        AGE_LH6: LevelConstants.ID_LH6,
    }

    LEVELS_NAMES = {
        LevelConstants.ID_HH2: NAME_HH2,
        LevelConstants.ID_HH3: NAME_HH3,
        LevelConstants.ID_HH4: NAME_HH4,
        LevelConstants.ID_HH5: NAME_HH5,
        LevelConstants.ID_LH1: NAME_LH1,
        LevelConstants.ID_LH2: NAME_LH2,
        LevelConstants.ID_LH3: NAME_LH3,
        LevelConstants.ID_LH4: NAME_LH4,
        LevelConstants.ID_LH5: NAME_LH5,
        LevelConstants.ID_LH6: NAME_LH6,
    }

    LEVEL_AGES = {
        LevelConstants.ID_HH2: AGE_HH2,
        LevelConstants.ID_HH3: AGE_HH3,
        LevelConstants.ID_HH4: AGE_HH4,
        LevelConstants.ID_HH5: AGE_HH5,
        LevelConstants.ID_LH1: AGE_LH1,
        LevelConstants.ID_LH2: AGE_LH2,
        LevelConstants.ID_LH3: AGE_LH3,
        LevelConstants.ID_LH4: AGE_LH4,
        LevelConstants.ID_LH5: AGE_LH5,
        LevelConstants.ID_LH6: AGE_LH6,
    }

    LEVELS_IDS = [
        LevelConstants.ID_HH2, LevelConstants.ID_HH3, LevelConstants.ID_HH4, LevelConstants.ID_HH5,
        LevelConstants.ID_LH1, LevelConstants.ID_LH2, LevelConstants.ID_LH3, LevelConstants.ID_LH4,
        LevelConstants.ID_LH5,
        LevelConstants.ID_LH6,
    ]

    CYCLE_LEVELS_PRE_SCHOOL = [
        LevelConstants.ID_HH2, LevelConstants.ID_HH3, LevelConstants.ID_HH4, LevelConstants.ID_HH5
    ]

    CYCLE_LEVELS_PRIMARY = [
        LevelConstants.ID_LH1, LevelConstants.ID_LH2, LevelConstants.ID_LH3, LevelConstants.ID_LH4,
        LevelConstants.ID_LH5, LevelConstants.ID_LH6
    ]

    ID_CYCLE_PRE_SCHOOL = 'PRE'
    ID_CYCLE_PRIMARY = 'PRI'
    ID_CYCLE_ALL = 'ALL'

    CYCLES = [
        (ID_CYCLE_PRE_SCHOOL, _('Pre-school')),
        (ID_CYCLE_PRIMARY, _('Primary education')),
        (ID_CYCLE_ALL, _('All cycles')),
    ]

    @staticmethod
    def get_level_by_age(age: int) -> Optional[str]:
        return Level.LEVEL_IDS_BY_AGE.get(age, None)

    @staticmethod
    def get_cycle_by_level(level_id: str) -> Optional[str]:
        if level_id in Level.CYCLE_LEVELS_PRIMARY:
            return Level.ID_CYCLE_PRIMARY
        elif level_id in Level.CYCLE_LEVELS_PRE_SCHOOL:
            return Level.ID_CYCLE_PRE_SCHOOL
        return None

    @staticmethod
    def get_age_by_level(level_id: str) -> Optional[int]:
        return Level.LEVEL_AGES.get(level_id, None)

    @staticmethod
    def get_level_name(level_id: str) -> int:
        return Level.LEVELS_NAMES.get(level_id)

    @staticmethod
    def calculate_repetition(current_level: str, year_of_birth: int) -> int:
        if current_level:
            age = Level.calculate_age(year_of_birth)
            school_age = Level.get_age_by_level(str(current_level))

            if school_age is not None:
                return age - school_age
        return 0

    @staticmethod
    def calculate_age(year_of_birth):
        active_course = ActiveCourse.load()
        return active_course.initial_year - year_of_birth

    @staticmethod
    def is_valid(level_id: str) -> bool:
        return level_id in Level.LEVELS_IDS

    @classmethod
    def guess_level(cls, level_description: str) -> Optional[str]:
        if LevelConstants.ID_HH2 in level_description:
            return LevelConstants.ID_HH2
        elif LevelConstants.ID_HH3 in level_description:
            return LevelConstants.ID_HH3
        elif LevelConstants.ID_HH4 in level_description:
            return LevelConstants.ID_HH4
        elif LevelConstants.ID_HH5 in level_description:
            return LevelConstants.ID_HH5
        elif LevelConstants.ID_LH1 in level_description:
            return LevelConstants.ID_LH1
        elif LevelConstants.ID_LH2 in level_description:
            return LevelConstants.ID_LH2
        elif LevelConstants.ID_LH3 in level_description:
            return LevelConstants.ID_LH3
        elif LevelConstants.ID_LH4 in level_description:
            return LevelConstants.ID_LH4
        elif LevelConstants.ID_LH5 in level_description:
            return LevelConstants.ID_LH5
        elif LevelConstants.ID_LH6 in level_description:
            return LevelConstants.ID_LH6
        return None
