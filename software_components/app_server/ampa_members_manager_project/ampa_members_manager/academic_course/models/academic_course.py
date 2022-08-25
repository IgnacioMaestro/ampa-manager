from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class AcademicCourse(models.Model):
    YEARS_TO_COURSE = {
        1: 'HH2',
        2: 'HH3',
        3: 'HH4',
        4: 'HH4',
        5: 'HH5',
        6: 'LH1',
        7: 'LH2',
        8: 'LH3',
        9: 'LH4',
        10: 'LH5',
        11: 'LH6',
    }

    COURSE_TO_YEARS = {
        'HH2': 1,
        'HH3': 2,
        'HH4': 3,
        'HH4': 4,
        'HH5': 5,
        'LH1': 6,
        'LH2': 7,
        'LH3': 8,
        'LH4': 9,
        'LH5': 10,
        'LH6': 11,
    }

    initial_year = models.IntegerField(
        unique=True, validators=[MinValueValidator(1000), MaxValueValidator(3000)], verbose_name=_("Initial year"))
    fee = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Fee"))

    class Meta:
        verbose_name = _('Academic course')
        verbose_name_plural = _('Academic courses')

    def __str__(self) -> str:
        return f'{str(self.initial_year)}-{str(self.initial_year + 1)}'
    
    @staticmethod
    def get_course(years_since_birth, repetition):
        return AcademicCourse.YEARS_TO_COURSE.get(years_since_birth - repetition, None)
    
    @staticmethod
    def get_default_years_since_birth(course):
        return AcademicCourse.COURSE_TO_YEARS.get(course)
