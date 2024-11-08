from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.price_per_level import PricePerLevel


class AfterSchoolEdition(PricePerLevel):
    after_school = models.ForeignKey(to=AfterSchool, on_delete=CASCADE, verbose_name=_("After-school"))
    code = models.CharField(max_length=300, verbose_name=_("Code"), null=True, blank=True)
    period = models.CharField(max_length=300, verbose_name=_("Period"))
    timetable = models.CharField(max_length=300, verbose_name=_("Timetable"))
    academic_course = models.ForeignKey(to=AcademicCourse, on_delete=CASCADE, verbose_name=_("Academic course"))

    class Meta:
        verbose_name = _('After-school edition')
        verbose_name_plural = _('After-school editions')
        db_table = 'after_school_edition'
        constraints = [
            models.UniqueConstraint(
                fields=['after_school', 'academic_course', 'period', 'timetable'], name='unique_important_fields'),
            models.UniqueConstraint(
                fields=['academic_course', 'code'], name='unique_code_in_academic_course'),
        ]

    def __str__(self) -> str:
        return f'{self.academic_course}, {self.after_school}, {self.period}, {self.timetable}, {self.registrations_count} {_("registrations")}'

    def str_short(self) -> str:
        return f'{self.academic_course}, {self.after_school}, {self.period}, {self.timetable}'

    @property
    def no_members_registrations_count(self):
        return self.registrations.no_members().count()

    @property
    def members_registrations_count(self):
        return self.registrations.members().count()

    @property
    def registrations_count(self):
        return self.registrations.count()

    @staticmethod
    def find(after_school: AfterSchool, period: str, timetable: str, levels: str):
        try:
            return AfterSchoolEdition.objects.get(after_school=after_school, period=period, timetable=timetable,
                                                  levels=levels)
        except AfterSchoolEdition.DoesNotExist:
            return None

    def is_modified(self, after_school, period, timetable, levels, price_for_member, price_for_no_member):
        return self.after_school != after_school \
               or self.period != period \
               or self.timetable != timetable \
               or self.levels != levels \
               or self.price_for_member != price_for_member \
               or self.price_for_no_member != price_for_no_member
