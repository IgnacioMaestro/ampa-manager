from django.db import models
from django.utils.translation import gettext_lazy as _


class Level():
    ID_HH2 = 'HH2'
    ID_HH3 = 'HH3'
    ID_HH4 = 'HH4'
    ID_HH5 = 'HH5'
    ID_LH1 = 'LH1'
    ID_LH2 = 'LH2'
    ID_LH3 = 'LH3'
    ID_LH4 = 'LH4'
    ID_LH5 = 'LH5'
    ID_LH6 = 'LH6'
    
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

    LEVEL_BY_AGE = {
        AGE_HH2: ID_HH2,
        AGE_HH3: ID_HH3,
        AGE_HH4: ID_HH4,
        AGE_HH5: ID_HH5,
        AGE_LH1: ID_LH1,
        AGE_LH2: ID_LH2,
        AGE_LH3: ID_LH3,
        AGE_LH4: ID_LH4,
        AGE_LH5: ID_LH5,
        AGE_LH6: ID_LH6,
    }

    LEVELS_NAMES = {
        ID_HH2: NAME_HH2,
        ID_HH3: NAME_HH3,
        ID_HH4: NAME_HH4,
        ID_HH5: NAME_HH5,
        ID_LH1: NAME_LH1,
        ID_LH2: NAME_LH2,
        ID_LH3: NAME_LH3,
        ID_LH4: NAME_LH4,
        ID_LH5: NAME_LH5,
        ID_LH6: NAME_LH6,
    }

    AGE_BY_LEVEL = {
        ID_HH2: AGE_HH2,
        ID_HH3: AGE_HH3,
        ID_HH4: AGE_HH4,
        ID_HH5: AGE_HH5,
        ID_LH1: AGE_LH1,
        ID_LH2: AGE_LH2,
        ID_LH3: AGE_LH3,
        ID_LH4: AGE_LH4,
        ID_LH5: AGE_LH5,
        ID_LH6: AGE_LH6,
    }

    @staticmethod
    def get_level_name_by_age(age :int) -> str:
        try:
            level_id = Level.LEVEL_BY_AGE.get(age)
            return Level.LEVELS_NAMES.get(level_id)
        except ValueError:
            return None
    
    @staticmethod
    def get_age_by_level(level_id :str) -> int:
        return Level.AGE_BY_LEVEL.get(level_id)
