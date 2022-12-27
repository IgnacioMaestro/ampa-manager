from django.db import models
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.funding import Funding


class AfterSchool(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("AfterSchool activity name"), unique=True)
    funding = models.IntegerField(choices=Funding.choices, verbose_name=_("Funding"))

    class Meta:
        verbose_name = _('AfterSchool')
        verbose_name_plural = _('AfterSchools')
        db_table = 'after_school'

    def __str__(self) -> str:
        return f'{self.name}'

    @staticmethod
    def find(name):
        try:
            return AfterSchool.objects.get(name=name)
        except AfterSchool.DoesNotExist:
            return None

    def find_edition(self, period, timetable):
        return AfterSchoolEdition.find_edition_for_active_course(self, period, timetable)
