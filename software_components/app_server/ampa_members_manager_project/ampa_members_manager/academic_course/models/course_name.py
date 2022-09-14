from django.db import models
from django.utils.translation import gettext_lazy as _


class CourseName():
    HH2 = (2, _('HH2'))
    HH3 = (3, _('HH3'))
    HH4 = (4, _('HH4'))
    HH5 = (5, _('HH5'))
    LH1 = (6, _('LH1'))
    LH2 = (7, _('LH2'))
    LH3 = (8, _('LH3'))
    LH4 = (9, _('LH4'))
    LH5 = (10, _('LH5'))
    LH6 = (11, _('LH6'))

    COURSES = {
        2: _('HH2'),
        3: _('HH3'),
        4: _('HH4'),
        5: _('HH5'),
        6: _('LH1'),
        7: _('LH2'),
        8: _('LH3'),
        9: _('LH4'),
        10: _('LH5'),
        11: _('LH6'),
    }

    @staticmethod
    def get_name_by_years(years :int) -> str:
        try:
            return CourseName.COURSES.get(years)
        except ValueError:
            return None
