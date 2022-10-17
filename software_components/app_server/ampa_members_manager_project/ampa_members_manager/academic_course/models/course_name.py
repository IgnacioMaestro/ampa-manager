from django.db import models
from django.utils.translation import gettext_lazy as _


class CourseName():
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

    LABEL_HH2 = _('HH2')
    LABEL_HH3 = _('HH3')
    LABEL_HH4 = _('HH4')
    LABEL_HH5 = _('HH5')
    LABEL_LH1 = _('LH1')
    LABEL_LH2 = _('LH2')
    LABEL_LH3 = _('LH3')
    LABEL_LH4 = _('LH4')
    LABEL_LH5 = _('LH5')
    LABEL_LH6 = _('LH6')

    HH2 = (AGE_HH2, LABEL_HH2)
    HH3 = (AGE_HH3, LABEL_HH3)
    HH4 = (AGE_HH4, LABEL_HH4)
    HH5 = (AGE_HH5, LABEL_HH5)
    LH1 = (AGE_LH1, LABEL_LH1)
    LH2 = (AGE_LH2, LABEL_LH2)
    LH3 = (AGE_LH3, LABEL_LH3)
    LH4 = (AGE_LH4, LABEL_LH4)
    LH5 = (AGE_LH5, LABEL_LH5)
    LH6 = (AGE_LH6, LABEL_LH6)

    COURSES = {
        AGE_HH2: LABEL_HH2,
        AGE_HH3: LABEL_HH3,
        AGE_HH4: LABEL_HH4,
        AGE_HH5: LABEL_HH5,
        AGE_LH1: LABEL_LH1,
        AGE_LH2: LABEL_LH2,
        AGE_LH3: LABEL_LH3,
        AGE_LH4: LABEL_LH4,
        AGE_LH5: LABEL_LH5,
        AGE_LH6: LABEL_LH6,
    }

    @staticmethod
    def get_course_name_by_age(years :int) -> str:
        try:
            return CourseName.COURSES.get(years)
        except ValueError:
            return None
    
    @staticmethod
    def get_age_by_course_name(course_name :str) -> int:
        for key, value in CourseName.COURSES.items():
            if value == course_name:
                return key
        return None
