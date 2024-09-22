from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.price_per_level import PricePerLevel
from ampa_manager.activity.use_cases.importers.fields_changes import FieldsChanges


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

    def update(self, after_school, period, timetable, levels, price_for_member, price_for_no_member) -> FieldsChanges:
        fields_before = [self.after_school, self.period, self.timetable, self.levels, self.price_for_member,
                         self.price_for_no_member]
        not_reset_fields = []
        updated = False

        if after_school and after_school != self.after_school:
            self.after_school = after_school
            updated = True

        if period != self.period:
            self.period = period
            updated = True

        if timetable != self.timetable:
            self.timetable = timetable
            updated = True

        if levels != self.levels:
            self.levels = levels
            updated = True

        if price_for_member != self.price_for_member:
            self.price_for_member = price_for_member
            updated = True

        if price_for_no_member != self.price_for_no_member:
            self.price_for_no_member = price_for_no_member
            updated = True

        if updated:
            self.save()

        fields_after = [self.after_school, self.period, self.timetable, self.levels, self.price_for_member,
                        self.price_for_no_member]

        return FieldsChanges(fields_before, fields_after, not_reset_fields)
