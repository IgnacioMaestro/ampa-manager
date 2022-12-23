from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models import CASCADE

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.activity.models.after_school.after_school import AfterSchool
from ampa_members_manager.activity.models.price_per_level import PricePerLevel


class AfterSchoolEdition(PricePerLevel):
    after_school = models.ForeignKey(to=AfterSchool, on_delete=CASCADE, verbose_name=_("AfterSchool"))
    period = models.CharField(max_length=300, verbose_name=_("Period"))
    timetable = models.CharField(max_length=300, verbose_name=_("Timetable"))
    academic_course = models.ForeignKey(to=AcademicCourse, on_delete=CASCADE, verbose_name=_("Academic course"))

    class Meta:
        db_table = 'after_school_edition'
        constraints = [
            models.UniqueConstraint(
                fields=['after_school', 'academic_course', 'period', 'timetable'], name='unique_important_fields'),
        ]

    def __str__(self) -> str:
        return f'{self.after_school} {self.period} {self.timetable} {self.academic_course}'
