from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models import CASCADE

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.price_per_level import PricePerLevel
from ampa_manager.management.commands.results.processing_state import ProcessingState


class AfterSchoolEdition(PricePerLevel):
    after_school = models.ForeignKey(to=AfterSchool, on_delete=CASCADE, verbose_name=_("After-school"))
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
        ]

    def __str__(self) -> str:
        return f'{self.after_school} {self.period} {self.timetable} {self.academic_course}'

    @staticmethod
    def find_edition_for_active_course(after_school, period, timetable, levels):
        academic_course = ActiveCourse.load()
        editions = AfterSchoolEdition.objects.filter(period=period, timetable=timetable, after_school=after_school,
                                                     levels=levels, academic_course=academic_course)
        if editions.count() == 1:
            return editions[0]
        return None

    @staticmethod
    def create_edition_for_active_course(after_school, period, timetable, levels, price_for_member, price_for_no_member):
        return AfterSchoolEdition.objects.create(after_school=after_school, period=period,
                                                 timetable=timetable, levels=levels,
                                                 academic_course=ActiveCourse.load(),
                                                 price_for_member=price_for_member,
                                                 price_for_no_member=price_for_no_member)

    @staticmethod
    def import_edition(after_school, period, timetable, levels, price_for_members, price_for_no_members, create_if_not_exists):
        edition = AfterSchoolEdition.find_edition_for_active_course(after_school, period, timetable, levels)
        if edition:
            return edition, ProcessingState.NOT_MODIFIED, None
        elif create_if_not_exists:
            edition = AfterSchoolEdition.create_edition_for_active_course(after_school, period, timetable, levels,
                                                        price_for_members, price_for_no_members)
            return edition, ProcessingState.CREATED, None
        else:
            return None, ProcessingState.ERROR, f'Not found: {after_school}, {period}, {timetable}, {levels}'
